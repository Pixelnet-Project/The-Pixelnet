import socket
import threading
import sys
import os
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
        print("OUTREACH_FAILED")
        try:
            sock.shutdown(2)
        except socket.error:
            pass
        try:
            sock.close()
        except:
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
            print(f"UNABLE TO REMOVE IP FILE PATH. THIS IS NORMAL IF THE FILE WAS ALREADY DELETED OR DID NOT EXIST. CAUSED BY EXCEPTION: {e}")
    if not os.path.isdir(ip_message_file_path):
        try:
            os.makedirs(ip_message_file_location, exist_ok=True)
        except Exception as e:
            print(f"FATAL ERROR FOR .IPMESSAGE FUNCTIONALITY, CANNOT CREATE REQUIRED FILES/DIRECTORY. CAUSED BY EXCEPTION: {e}")
            try:
                sock.shutdown(2)
            except Exception as e:
                print(f"SOCK SHUTDOWN ERROR IN DISCONNECTION PROCEDURE. CAUSED BY EXCEPTION: {e}")
            sock.close()
            sys.exit()
    while 1:
        try:
            file = open(ip_message_file_path, "r")
        except:
            try:
                file = open(ip_message_file_path, "x")
                file.close()
            except Exception as e:
                    print(f"UNEXPECTED FATAL READ/WRITE ERROR FOR .IPMESSAGE FUNCTIONALITY: {e}")
                    sys.exit()
            finally:
                try:
                    file = open(ip_message_file_path, "a+")
                except Exception as e:
                    print(f"UNEXPECTED FATAL READ/WRITE ERROR FOR .IPMESSAGE FUNCTIONALITY: {e}")
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
                                print(f"DEBUG: COULD NOT CLOSE FILE: {file} IN FATAL_CONNECTION_ERROR SHUTDOWN SEQUENCE: {e}")
                            try:
                                sock.shutdown(2)
                            except socket.error as e:
                                pass
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