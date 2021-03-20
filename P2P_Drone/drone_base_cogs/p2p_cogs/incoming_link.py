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
        amount_of_incoming = len([name for name in os.listdir('./permanence_files/ip_messages/incoming_messages/') if os.path.isfile(name)])
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
                    print(f"CONNECTION SHUTDOWN FAILED FOR CONNECTION {conn} AT WELCOMER BECAUSE OF EXCEPTION: {e}")
                conn.close()
        else:
            try:
                conn.shutdown(2)
            except Exception as e:
                print(f"CONNECTION SHUTDOWN FAILED FOR CONNECTION {conn} AT WELCOMER BECAUSE OF EXCEPTION: {e}")
            conn.close()
def shutdown_incoming_link(conn, file, err, addr):
    """[summary]
    This function is a universal shutdown for an incoming link. 
    Args:
        conn ([sock]): [A socket connection]
        file ([TextIOWrapper]): [A file]
        err ([Exception]): [The exception that caused the error. (If applicable)]
        addr ([str]): [An IPv4 address, without the port number.]
    """
    ip_message_file_name = addr + ".ipmessage"
    ip_message_file_location = "./permanence_files/ip_messages/incoming_messages/"
    ip_message_file_path = os.path.join(ip_message_file_location, ip_message_file_name)
    if conn:
        try:
            conn.shutdown(2)
        except Exception as e:
            print(f"CONNECTION SHUTDOWN FAILED FOR CONNECTION {conn} BECAUSE OF EXCEPTION: {e}")
        conn.close()
    if os.pathexists(ip_message_file_path):
        try:
            os.remove(ip_message_file_path)
        except Exception as e:
            print(f"COULD NOT REMOVE FILE {ip_message_file_path}, EVEN THOUGH IT EXISTS, BECAUSE OF EXCEPTION: {e}")
    else:
        print(f"ERROR FOR .IPMESSAGE FUNCTIONALITY, {ip_message_file_path} COULD NOT BE REMOVED, BECAUSE IT DOES NOT EXIST.")
    if file:
        try:
            file.close()
        except Exception as e:
            print(f"FILE {file} COULD NOT BE CLOSED IN FATAL ERROR SHUTDOWN BECAUSE OF EXCEPTION {e}")
    if err:
        if addr:
            print(f"(SHUTDOWN SEQUENCE MESSAGE) THE EXCEPTION {err} OCCURRED AT {addr}. CONNECTION FATAL.")
        else:
            print(f"(SHUTDOWN SEQUENCE MESSAGE) THE EXCEPTION {err} OCCURRED AT {conn}. CONNECTION FATAL. EXAMINE CONNECTION FOR ADDRESS, ADDRESS NOT AVAILABLE.")
    sys.exit()

def link(conn, addr):
    """[summary]
    The incoming_link is the receiving end of an outcoming link from another bot.
    Args:
        conn ([socket]): [A socket connection (in the role of a server)]
        addr ([str]): [An IPv4 address, without the port number.]
    """
    addr = str(addr)
    ip_message_file_name = addr + ".ipmessage"
    ip_message_file_location = "./permanence_files/ip_messages/incoming_messages/"
    ip_message_file_path = os.path.join(ip_message_file_location, ip_message_file_name)
    if os.path.isdir(ip_message_file_path):
        try:
            os.remove(ip_message_file_path)
        except Exception as e:
            print(f"UNABLE TO REMOVE IP FILE PATH. THIS IS NORMAL IF THE FILE WAS ALREADY DELETED OR DID NOT EXIST. CAUSED BY EXCEPTION: {e}")
    if not os.path.isdir(ip_message_file_path):
        try:
            os.makedirs(ip_message_file_location, exist_ok=True)
        except Exception as e:
            print(f"FATAL ERROR FOR .IPMESSAGE FUNCTIONALITY, CANNOT CREATE REQUIRED FILES/DIRECTORY. CAUSED BY EXCEPTION: {e}")
            try:
                conn.shutdown(2)
            except Exception as e:
                print(f"SOCK SHUTDOWN ERROR IN DISCONNECTION PROCEDURE. CAUSED BY EXCEPTION: {e}")
            conn.close()
            sys.exit()
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
                        try:
                            conn.shutdown(2)
                        except Exception as e:
                            print(f"COULD NOT SHUTDOWN CONNECTION {conn} BECAUSE OF EXCEPTION {e}")
                        conn.close()
                        sys.exit()
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
                    print(f"UNEXPECTED FATAL READ/WRITE ERROR FOR .IPMESSAGE FUNCTIONALITY: {e}")
                    sys.exit()
            finally:
                try:
                    file = open(ip_message_file_path, "a+")
                except Exception as e:
                    print(f"UNEXPECTED FATAL READ/WRITE ERROR FOR .IPMESSAGE FUNCTIONALITY: {e}")
                    sys.exit()
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
                            print(f"FATAL I/O FAILURE IN INCOMING LINK THREAD: {e}")
                            conn.shutdown(2)
                            conn.close()
                            sys.exit()
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
                    print(f"CANNOT SHUTDOWN CONNECTION {conn} BECAUSE OF EXCEPTION {e}")
                conn.close()
                sys.exit()