import threading
import os.path
import sys
from ..scanner_cogs import *
from .. scanner_cogs import get_ip
from .head_recv import *
local_net = []
lhost = get_ip.get_ip()
def p2p_welcomer(server):
    """[summary]
    A function that takes incoming connections and transfers them to an incoming link. Can listen to the amount of current incoming link threads
    plus 2.
    Args:
        server ([sock]): [description]
    """
    while True:
        if os.path.exists("./permanence_files/ip_messages/incoming_messages/"):
            amount_of_incoming = len([name for name in os.listdir('./permanence_files/ip_messages/incoming_messages/') if os.path.isfile(name)])
        else:
            print("(p2p_welcomer) POSSIBLE ERROR, THE PATH ./permanence_files/ip_messages/incoming_messages/ DOES NOT EXIST.")
            amount_of_incoming = 0
        server.listen(amount_of_incoming + 2)
        print("SERVER LISTENING")
        conn, addr = server.accept()
        print(f"BOT_CONNECTED:{conn}, {addr}")
        if conn:
            if addr:
                link_drone_thread = threading.Thread(target=link, args=(conn, addr))
                link_drone_thread.name = "INCOMING_LINK"
                link_drone_thread.start()
            else:
                try:
                    conn.shutdown(2)
                except Exception as e:
                    print(f"(p2p_welcomer) CONNECTION SHUTDOWN FAILED FOR CONNECTION {conn} AT WELCOMER BECAUSE OF EXCEPTION: {e}")
                conn.close()
        else:
            try:
                conn.shutdown(2)
            except Exception as e:
                print(f"(p2p_welcomer) CONNECTION SHUTDOWN FAILED FOR CONNECTION {conn} AT WELCOMER BECAUSE OF EXCEPTION: {e}")
            conn.close()
def shutdown_incoming_link(conn, file, err, addr):
    """[summary]
    This function is a universal shutdown for an incoming link. Provides information of why the incoming link shut down in a summary message.

    Args:
        conn ([sock]): [A socket connection]
        file ([TextIOWrapper]): [A file]
        err ([Exception]): [The exception that caused the error. (If applicable)]
        addr ([str]): [An IPv4 address, without the port number.]
    """

    ip_message_file_name = addr + ".ipmessage"
    ip_message_file_location = "./permanence_files/ip_messages/incoming_messages/"
    ip_message_file_path = os.path.join(ip_message_file_location, ip_message_file_name)
    if os.path.exists(ip_message_file_path):
        try:
            os.remove(ip_message_file_path)
        except Exception as e:
            print(f"(SHUTDOWN SEQUENCE MESSAGE) COULD NOT REMOVE FILE {ip_message_file_path}, EVEN THOUGH IT EXISTS, BECAUSE OF EXCEPTION: {e}")
    else:
        print(f"(SHUTDOWN SEQUENCE MESSAGE) ERROR FOR .IPMESSAGE FUNCTIONALITY, {ip_message_file_path} COULD NOT BE REMOVED, BECAUSE IT DOES NOT EXIST.")
    if conn:
        try:
            conn.shutdown(2)
        except Exception as e:
            print(f"(SHUTDOWN SEQUENCE MESSAGE) CONNECTION SHUTDOWN FAILED FOR CONNECTION {conn} BECAUSE OF EXCEPTION: {e}")
        conn.close()
    if file:
        if file == False:
            print(f"(SHUTDOWN SEQUENCE MESSAGE) FILE TEXTIOWRAPPER NOT FOUND, NON-FATAL SHUTDOWN ERROR.")
        elif file != False:
            try:
                file.close()
            except Exception as e:
                print(f"(SHUTDOWN SEQUENCE MESSAGE) FILE {file} COULD NOT BE CLOSED IN FATAL ERROR SHUTDOWN BECAUSE OF EXCEPTION {e}")
    if err:
        if err != False:
            if addr:
                print(f"(SHUTDOWN SEQUENCE MESSAGE) THE EXCEPTION {err} OCCURRED AT {addr}. CONNECTION FATAL.")
            else:
                print(f"(SHUTDOWN SEQUENCE MESSAGE) THE EXCEPTION {err} OCCURRED AT {conn}. CONNECTION FATAL. EXAMINE CONNECTION FOR ADDRESS, ADDRESS NOT AVAILABLE.")
        elif err == False:
            if addr:
                print(f"(SHUTDOWN SEQUENCE MESSAGE) SHUTTING DOWN INCOMING LINK CONNECTION WITH {addr} FOR UNPROVIDED REASON.")
            else:
                print(f"(SHUTDOWN SEQUENCE MESSAGE) SHUTTING DOWN AN INCOMING LINK FOR AN UNPROVIDED REASON. ADDRESS NOT AVAILABLE, EXAMINE CONNECTION: {conn}")
        else:
            if addr:
                print(f"(SHUTDOWN SEQUENCE MESSAGE) EXAMINE CODE IN INCOMING LINK, GOT RESPONSE {err} from {addr}")
            else:
                print(f"(SHUTDOWN SEQUENCE MESSAGE) EXAMINE CODE IN INCOMING LINK, GOT RESPONSE {err} FROM UNKNOWN INCOMING LINK, EXAMINE CONNECTION: {conn}")
    sys.exit()

def link(conn, addr):
    """[summary]
    The incoming_link is the receiving end of an outcoming link from another bot.
    Args:
        conn ([socket]): [A socket connection (in the role of a server)]
        addr ([str]): [An IPv4 address, without the port number.]
    """
    file = False
    addr = str(addr)
    ip_message_file_name = addr + ".ipmessage"
    ip_message_file_location = "./permanence_files/ip_messages/incoming_messages/"
    ip_message_file_path = os.path.join(ip_message_file_location, ip_message_file_name)
    if os.path.isdir(ip_message_file_path):
        try:
            os.remove(ip_message_file_path)
        except Exception as e:
            shutdown_incoming_link(conn, False, e, addr)
    if not os.path.isdir(ip_message_file_path):
        try:
            os.makedirs(ip_message_file_location, exist_ok=True)
        except Exception as e:
            shutdown_incoming_link(conn, False, e, addr)
    print("STARTED INCOMING LINK")
    disconnection_counter = 0
    waiting_for_info = True
    conn.settimeout(5)
    while waiting_for_info == True:
        net_link = head_recv(conn, addr)
        if net_link:
            if net_link == "DRONE_IDLE":
                conn.settimeout(None)
            else:
                conn.settimeout(5)
            if type(net_link) == type([]):
                if net_link[1] == "LOCAL_ERROR":
                    if net_link[0] == "FATAL_CONNECTION_ERROR":
                        shutdown_incoming_link(conn, file, "", addr)
                    else:
                        print(f"LOCAL_ERROR: {net_link[0]} experienced. Non-fatal.")
                if net_link[1] == "SECURITY_ALERT":
                    print(f"SECURITY_ALERT: {net_link[0]} experienced. Non-fatal.")
            try:
                file = open(ip_message_file_path, "r")
            except Exception as e:
                print(f"POSSIBLY EXPECTED ERROR FOR .IPMESSAGE FUNCTIONALITY: {e}")
                try:
                    file = open(ip_message_file_path, "x")
                except Exception.error as e:
                    shutdown_incoming_link(conn, file, e, addr)
            finally:
                try:
                    file = open(ip_message_file_path, "a+")
                except Exception as e:
                    shutdown_incoming_link(conn, file, e, addr)
            if net_link == "DRONE_IDLE":
                pass
            else:
                if type(net_link) != type([]):
                    net_link = str(net_link)
                    try:
                        file.write(net_link)
                    except:
                        try:
                            file = open(ip_message_file_path, "a+")
                            file.write(net_link)
                        except Exception as e:
                            shutdown_incoming_link(conn, file, e, addr)
                    file.write("\n")
                    file.close()
        elif not net_link:
            disconnection_counter += 1
        if disconnection_counter == 5:
            try:
                conn.sendall("conn_test", "utf-8")
                disconnection_counter = 0
            except:
                print("INCOMING_LINK_DISCONNECTED")
                try:
                    conn.shutdown(2)
                except Exception as e:
                    shutdown_incoming_link(conn, file, e, addr)