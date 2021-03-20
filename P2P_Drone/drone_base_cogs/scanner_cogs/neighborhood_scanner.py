import socket
import threading
import sys
import time
import os.path
import random
from . import ip_range
from ..p2p_cogs import outgoing_link
from . import get_ip
try:
    from . import broadcast_get
except Exception as e:
    print(f"FAILED TO IMPORT BROADCAST_GET BECAUSE EXCEPTION: {e}")
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
    while os.path.exists(lock_file_path):
        #print("scanner_locked")
        time.sleep(random.uniform(0.1,1.0))
    try:
        peer_lock = open(lock_file_path, "x")
        peer_lock.close()
    except Exception as e:
        print(f"COULD NOT OPEN OR CLOSE FILE {peer_lock} BECAUSE OF EXCEPTION: {e}")
    target_number = 0
    try:
        broadcast = broadcast_get.get()
    except Exception as e:
        print(f"COULD NOT GET BROADCAST IP BECAUSE OF EXCEPTION: {e}")
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
                except Exception as e:
                    print(f"COULD NOT REMOVE BROADCAST IP FROM TARGETS LIST BECAUSE OF EXCEPTION: {e}")
            for workers in targets:
                worker_threads = threading.Thread(target=worker_scan, args=(workers))
                worker_threads.name = f"Port Scan Worker {workers}"
                time.sleep(0.01)
                worker_threads.start()
                if workers == targets[-1]:
                    #print("WORKERS END")
                    time.sleep(5)
                    while True:
                        if not actual_workers:
                            #print("Targets is equal to finished_workers")
                            os.remove("./permanence_files/peer_scan.lock")
                            sys.exit()

def peer_recording(ip, port):
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
        try:
            file = open(file_path, "x")
        except:
            print("UNEXPECTED PEER RECORDING FILE ERROR")
            sys.exit()
    finally:
        try:
            file = open(file_path, "a+")
        except:
            #print("UNEXPECTED PEER RECORDING FILE ERROR")
            sys.exit()
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
                            print(f"Had exception {e} when attempting to remove localhost from neighborhood scanner.")
                    #print(actual_workers)
                    try:
                        sock.close()
                    except Exception as e:
                        print(f"DEBUG: COULD NOT CLOSE SOCK {sock} BECAUSE OF EXCEPTION: {e}.")
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
                        print(f"Had exception {e} when attempting to remove localhost from neighborhood scanner.")
                #print(actual_workers)
                try:
                    sock.close()
                except Exception as e:
                    print(f"COULD NOT CLOSE CONNECTION {sock} BECAUSE OF EXCEPTION: {e}")
                sys.exit()
            else:
                pass
                #print(f"Nothing on {ip}:{port}")
    except socket.gaierror:
        actual_workers.remove(ip)
        sys.exit()
    except socket.error as err:
        try:
            actual_workers.remove(ip)
        except Exception as e:
            print(f"COULD NOT REMOVE WORKER: {ip} FROM ACTUAL_WORKERS LIST BECAUSE OF EXCEPTION: {e} ")
        print(f"SOCKET ERROR: {err}")
def worker_scan(*ip):
    str = ''.join(ip)
    port_scan(str)