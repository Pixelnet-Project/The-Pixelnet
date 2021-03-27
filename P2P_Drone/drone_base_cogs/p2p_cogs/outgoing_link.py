import socket
import threading
import sys
import os
import logging
import time
from .head_send import *
def outreach_local_peer(address):
    """[summary]
    A small function that starts an outreach thread.
    Args:
        address ([str]): [An IPv4 address, as well as a port number]
    """
    outreach_command = threading.Thread(target=outreach, args=(address,))
    outreach_command.name = "OUTREACH_LINK_FOR_REAL"
    outreach_command.start()
    sys.exit()

def outreach(addr):
    """[summary]
    Communicates with the receiving end through .ipmessage files, so that any module can easily use the "gate out".
    Args:
        addr ([str]): [An IPv4 address, as well as a port number.]
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"STARTED OUTREACH LINK TO {addr}")
    try:
        sock.connect(addr)
        sock.settimeout(5)
    except:
        logging.critical(f"Could not outreach to {addr}", exc_info=True)
        try:
            sock.shutdown(2)
        except socket.error:
            logging.error(f"Could not shutdown sock {sock} in outgoing link {addr}", exc_info=True)
        try:
            sock.close()
        except:
            logging.critical(f"Could not close sock {sock} in outgoing link {addr}", exc_info=True)
            sys.exit()
        sys.exit()
    addr = str(addr)
    ip_message_file_name = addr + ".ipmessage"
    ip_message_file_location = "./permanence_files/ip_messages/outgoing_messages/"
    ip_message_file_path = os.path.join(ip_message_file_location, ip_message_file_name)
    if os.path.isdir(ip_message_file_path):
        try:
            os.remove(ip_message_file_path)
        except Exception as e:
            logging.warning(f"Could not remove {ip_message_file_path} (even though it exists)", exc_info=True)
    if not os.path.isdir(ip_message_file_path):
        try:
            os.makedirs(ip_message_file_location, exist_ok=True)
        except Exception as e:
            logging.critical(f"Could not make the directory tree for {ip_message_file_location} in outgoing_link {addr}", exc_info=True)
            try:
                sock.shutdown(2)
            except Exception as e:
                logging.error(f"Could not shutdown sock {sock} in outgoing_link {addr}", exc_info=True)
            sock.close()
            sys.exit()
    while 1:
        try:
            file = open(ip_message_file_path, "r")
        except:
            logging.warning(f"Could not read {ip_message_file_path}", exc_info=True)
            try:
                file = open(ip_message_file_path, "x")
                file.close()
            except Exception as e:
                    logging.critical(f"Could not create the file {ip_message_file_path} in outgoing_link {addr}", exc_info=True)
                    sys.exit()
            finally:
                try:
                    file = open(ip_message_file_path, "a+")
                except Exception as e:
                    logging.critical(f"Could not open the file {ip_message_file_path} in append+ mode in outgoing_link {addr}", exc_info=True)
                    sys.exit()
        output = []
        for line in file:
            line = line.rstrip("\n")
            output.append(line)
            print(output)
            if output:
                for message in output:
                    message_to_send = str(message)
                    print(f"MESSAGE TO SEND: {message_to_send}")
                    check_for_error = head_send(sock, message_to_send)
                    output.remove(message)
                    if check_for_error:
                        if check_for_error == "FATAL_CONNECTION_ERROR":
                            try:
                                file.close()
                            except Exception as e:
                                logging.warning(f"Could not close file {ip_message_file_path} in outgoing_link {addr}", exc_info=True)
                            try:
                                sock.shutdown(2)
                            except socket.error as e:
                                logging.error(f"Could not shutdown sock {sock} in outgoing_link {addr}", exc_info=True)
                            sock.close()
                            sys.exit()
        lst = []
        for line in file:
                if line in output:
                    line = line.replace(output[0],'')
                    lst.append(line)
        file = open(ip_message_file_path,'w')
        for line in lst:
            print(lst)
            file.write(line)
        time.sleep(1)
        head_send(sock, "DRONE_IDLE")
        file.close()