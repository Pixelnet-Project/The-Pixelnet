
import threading
import logging
import os
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
        #NOTE: This listen function is only supposed to be here until I figure out how to have the amount of server connections (+2)
        server.listen(2)
        incoming_link_path = "permanence_files\ip_messages\incoming_messages/"
        if os.path.isfile(incoming_link_path):
            dir_list = os.listdir(incoming_link_path)
            print(f"THIS IS HOW MANY FILES ARE IN INCOMING_MESSAGES: {len(dir_list)}")
        else:
            dir_list = 0
            logging.info(f"No files found in {incoming_link_path}", exc_info=True)
        print(f"HOW MANY MESSAGES IN INCOMING: {dir_list}")
        conn, addr = server.accept()
        print(f"BOT_CONNECTED:{conn}, {addr}")
        if conn:
            if addr:
                link_drone_thread = threading.Thread(target=link, args=(conn, addr))
                link_drone_thread.name = "INCOMING_LINK"
                link_drone_thread.start()
            else:
                logging.info(f"Failed to retrieve {conn} address.", exc_info=True)
                try:
                    conn.shutdown(2)
                except:
                    logging.error(f"Failed to shutdown connection {conn}", exc_info=True)
                conn.close()
        else:
            try:
                conn.shutdown(2)
            except Exception as e:
                logging.error(f"Failed to shutdown unknown connection", exc_info=True)
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
            logging.error(f"Failed to remove {ip_message_file_path} in shutdown_sequence for link {addr}", exc_info=True)
    else:
        logging.info(f"Failed to remove {ip_message_file_path} in shutdown_sequence for link {addr} because it does not exist.")
    if conn:
        try:
            conn.shutdown(2)
        except Exception as e:
            logging.error(f"Could not shutdown incoming_link {addr}", exc_info=True)
        conn.close()
    if file:
        if file == False:
            print(f"(SHUTDOWN SEQUENCE MESSAGE) FILE TEXTIOWRAPPER NOT FOUND, NON-FATAL SHUTDOWN ERROR.")
        elif file != False:
            try:
                file.close()
            except Exception as e:
                logging.critical(f"Could not close file {file} even though it exists.", exc_info=True)
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
            logging.critical(f"Could not remove a previous version of .ipmessage file from incoming_link {addr}, even though the previous file exists. Shutting down incoming_link.", exc_info=True)
            shutdown_incoming_link(conn, False, e, addr)
    if not os.path.isdir(ip_message_file_path):
        try:
            os.makedirs(ip_message_file_location, exist_ok=True)
        except Exception as e:
            logging.critical(f"Could not create {ip_message_file_location} for incoming_link {addr}, even though the file does not exist. Shutting down incoming_link", exc_info=True)
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
                        logging.critical(f"Encountered fatal connection error in incoming_link {addr} , for more details, check the appropriate head_recv log file.", exc_info=True)
                        shutdown_incoming_link(conn, file, "", addr)
                    else:
                        print(f"LOCAL_ERROR: {net_link[0]} experienced. Non-fatal.")
                if net_link[1] == "SECURITY_ALERT":
                    print(f"SECURITY_ALERT: {net_link[0]} experienced. Non-fatal.")
            try:
                file = open(ip_message_file_path, "r")
            except Exception as e:
                logging.info(f"Could not open or read {ip_message_file_path} in incoming_link {addr}", exc_info=True)
                try:
                    file = open(ip_message_file_path, "x")
                except Exception.error as e:
                    logging.critical(f"Could not create the file {ip_message_file_path} in incoming_link {addr}", exc_info=True)
                    shutdown_incoming_link(conn, file, e, addr)
            finally:
                try:
                    file = open(ip_message_file_path, "a+")
                except Exception as e:
                    logging.critical(f"Could not open {ip_message_file_path} in append+ mode in incoming_link {addr}", exc_info=True)
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
                            logging.critical(f"Could not open {ip_message_file_path} in append+ mode, or could not write to {ip_message_file_path} in append+ mode in incoming_link {addr}", exc_info=True)
                            shutdown_incoming_link(conn, file, e, addr)
                    file.write("\n")
                    file.close()
        elif not net_link:
            disconnection_counter += 1
        if disconnection_counter == 5:
            try:
                conn.sendall(bytes("conn_test", "utf-8"))
                disconnection_counter = 0
            except Exception as err:
                print("INCOMING_LINK_DISCONNECTED")
                try:
                    conn.shutdown(2)
                except Exception as e:
                    logging.critical(f"Could not shutdown connection {conn} in incoming_link {addr}", exc_info=True)
                    shutdown_incoming_link(conn, file, e, addr)
                finally:
                    logging.critical(f"Outgoing link {conn} disconnected from incoming_link {addr}", exc_info=True)
                    shutdown_incoming_link(conn, file, err, addr)