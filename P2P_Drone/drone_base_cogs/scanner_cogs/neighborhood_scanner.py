import socket
import threading
import sys
import time
import logging
import os.path
import random
from . import ip_range
from ..p2p_cogs import outgoing_link
from . import get_ip
try:
    from . import broadcast_get
except Exception as e:
    logging.warning("broadcast_get could not be imported", exc_info=True)
possible_peers = []
max_ip = ip_range.ip_range()
global lhost
lhost = get_ip.get_ip()
targets = []
actual_workers = []
lock_dir = "./permanence_files"
lock_file_name = "peer_scan.lock"
lock_file_path = os.path.join(lock_dir, lock_file_name)
if not os.path.isdir(lock_dir):
    os.mkdir(lock_dir)
def peer_scan():
    """[summary]
    This module creates the threads for the individual workers that then scan the IP's. Currently, one worker is assigned to each IP address.
    The module is also in charge of the scan_lock, to make sure that more than one scans cannot happen at the same time, and also shuts down the 
    scan after all bots have finished.
    """
    while os.path.exists(lock_file_path):
        #print("scanner_locked")
        time.sleep(random.uniform(0.1,1.0))
    try:
        peer_lock = open(lock_file_path, "x")
        peer_lock.close()
    except Exception:
        logging.critical("Could not create lock file (even thought it's believed that the lock file does not exist!)", exc_info=True)
    target_number = 0
    try:
        broadcast = broadcast_get.get()
    except Exception:
        logging.debug("broadcast_get couldn't be used", exc_info=True)
        broadcast = False
    for i in range(0, max_ip):
        target_number = int(target_number)
        target_number += 1
        target_number = str(target_number)
        targets.append(lhost[:lhost.rfind(".")] + "." + target_number)
        if i >= max_ip - 1:
            # Putting the line below on hold for now, for connection testing purposes.
            #targets.remove(lhost)
            if broadcast != False:
                try:
                    targets.remove(broadcast)
                except Exception:
                    logging.debug("Could not remove broadcast_get", exc_info=True)
            for workers in targets:
                worker_threads = threading.Thread(target=worker_scan, args=(workers))
                worker_threads.name = f"Port Scan Worker {workers}"
                time.sleep(0.01)
                worker_threads.start()
                if workers == targets[-1]:
                    #print("WORKERS END")
                    time.sleep(5)
                    peer_scan_lock_path = "./permanence_files/peer_scan.lock"
                    while True:
                        if not actual_workers:
                            #print("Targets is equal to finished_workers")
                            if os.path.isdir(peer_scan_lock_path):
                                os.remove(peer_scan_lock_path)
                            else:
                                logging.critical("Could not remove peer_scan_lock_path even though it exists", exc_info=True)
                            sys.exit()

def peer_recording(ip, port):
    """[summary]
    The module that is used to record the already recorded peers in the port_report. The port_report.txt (as of 3/20/21) file does not contain any useful
    information. By this I mean that no module nor program uses it yet, so this module is more for preperation for when I will inevitably want to record
    the ports that have successful IP and Port Numbers, so that they can be immediately reached out to if the bot is shut down and then is turned on again. 
    Args:
        ip ([str]): [An IPv4 address (without port number)]
        port ([str]): [Port number]
    """
    ip = str(ip)
    port = str(port)
    filename = "port_report.txt"
    file_path = os.path.join(lock_dir, filename)
    if not os.path.isdir(lock_dir):
        os.mkdir(lock_dir)
    ip_to_write = ip + ":" + port
    try:
        file = open(file_path, "r")
    except:
        logging.debug("Could not open port report file")
        try:
            file = open(file_path, "x")
        except:
            logging.critical("Could not create port_report.txt (after being unable to read a possibly existing port_report.txt)", exc_info=True)
            sys.exit()
    finally:
        try:
            file = open(file_path, "a+")
        except:
            logging.critical(f"Could not open {file_path} in append mode", exc_info=True)
    with open(file_path, "r") as file:
        ip_list_str = file.read()
        print(ip_list_str)
        if ip_to_write in ip_list_str:
            file.close()
            sys.exit()
        else:
            pass
    file.close()
    file = open(file_path, "a")
    file.write(ip_to_write)
    file.write("\n")
    file.close()
    sys.exit()

def port_scan(ip):
    """[summary]
    The port scan module is the module that is used to scan the ports. The module takes the IP that it is given and scans it from port 49995 to port 50001.
    If it finds a open port, it will start a thread to report the event in the port_report.txt, and it will then dispatch an outreach thread, which will then
    communicate with the port, although at this point the port scan worker has moved on to the next port (and if not, has already completed it's assignment.)
    Args:
        ip ([str]): [An IPv4 address (without port number)]
    """
    actual_workers.append(ip)
    try:
        for port in range(49995,50001):
            ip = str(ip)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            sock.settimeout(5)
            address = (ip, port)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result == 0:
                print(f"GOT POSSIBLE PEER FROM {ip}:{port}")
                peer_record_thread = threading.Thread(target=peer_recording, args=(ip, port))
                peer_record_thread.name = "Peer_Recording_Thread_Manager"
                peer_record_thread.start()
                outgoing_link_thread = threading.Thread(target=outgoing_link.outreach_local_peer, args=(address,))
                outgoing_link_thread.name = "OUTGOING_LINK"
                outgoing_link_thread.start()
                if port == 50000:
                    actual_workers.remove(ip)
                    #print("Completed Scan.")
                    if lhost in actual_workers:
                        try:
                            actual_workers.remove(lhost)
                        except ValueError as e:
                            logging.error("Could not remove lhost from actual_workers list", exc_info=True)
                    #print(actual_workers)
                    try:
                        sock.close()
                    except Exception as e:
                        logging.critical("Could not close sock in port_scan function", exc_info=True)
                    sys.exit()
                else:
                    break
            if port == 50000:
                actual_workers.remove(ip)
                #print("Completed Scan.")
                if lhost in actual_workers:
                    try:
                        actual_workers.remove(lhost)
                    except ValueError as e:
                        logging.error("Could not remove lhost from actual_workers list", exc_info=True)
                #print(actual_workers)
                try:
                    sock.close()
                except Exception as e:
                    logging.critical("Could not close sock in port_scan function", exc_info=True)
                sys.exit()
            else:
                pass
                #print(f"Nothing on {ip}:{port}")
    except socket.gaierror:
        actual_workers.remove(ip)
        logging.info(f"On worker {ip}, there was no client to scan.")
        sys.exit()
    except socket.error as err:
        try:
            actual_workers.remove(ip)
        except Exception as e:
            logging.critical(f"In worker {ip}, could not remove worker IP from actual_workers list", exc_info=True)
        logging.error(f"In worker {ip}, there was a socket error", exc_info=True)
def worker_scan(*ip):
    """[summary]
    A small function that joins the ip address together and then starts the port_scan module.
    """
    str = ''.join(ip)
    port_scan(str)