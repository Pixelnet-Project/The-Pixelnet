import socket
import time
import random
import sys
import threading
import os
import shutil
from drone_base_cogs.scanner_cogs import *
from drone_base_cogs.scanner_cogs import get_ip
from drone_base_cogs.scanner_cogs import neighborhood_scanner
from drone_base_cogs.p2p_cogs import *
from drone_base_cogs.p2p_cogs import incoming_link
binding = True
squadron_dict = {}
squadron_checked = 0
start_address = ""
global server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bind_attempts = 0
def initialization_process():
    """[summary]
    This function starts the initialization process for the bot. It starts all of the modules that need to be started, removes all of the stuff that (such as .ipmessage files)
    that may have been left over from previous runs of the bot that isn't meant for permanence, and starts threads of the neighborhood scanner. The initialization process is
    a required part of the drone and cannot be removed, unless the drone is not to work correctly (or someone finds a better way to do it)
    """
    try:
        self_name = os.path.basename(__file__)
    except Exception as e:
        print(f"COULD NOT FIND NAME OF THIS FILE BECAUSE OF EXCEPTION: {e}")
    if ".pyw" in self_name:
        sys.stdout = open(os.devnull, 'w')
    p2p_server_thread = threading.Thread(target=incoming_link.p2p_welcomer, args=(server,))
    p2p_server_thread.name = "p2p_welcomer"
    p2p_server_thread.start()
    try:
        # Should be noted that after finishing development on VSCode, this needs to be taken out to mean in the context of the stand-alone drone
        os.remove("./permanence_files/peer_scan.lock")
    except Exception as e:
        print(f"COULD NOT REMOVE peer_scan.lock IN START UP SEQUENCE BECAUSE OF EXCEPTION {e}")
    try:
        shutil.rmtree("./permanence_files/ip_messages")
    except Exception as e:
        print(f"COULD NOT REMOVE TREE ./permanence_files/ip_messages IN START UP SEQUENCE BECAUSE OF EXCEPTION {e}")
    neighborhood_scanner_init_thread = threading.Thread(target=neighborhood_scanner.peer_scan, args=())
    neighborhood_scanner_init_thread.name = "init_scanner_thread"
    neighborhood_scanner_init_thread.start()
tried_binds = []
while binding == True:
    HOST = get_ip.get_ip()
    PORT = random.randrange(49995, 50000)
    if bind_attempts >= 5:
        print("HOST MACHINE REFUSED BIND FIVE TIMES, SHUTTING DOWN BOT")
        sys.exit()
    if PORT not in tried_binds:
        try:
            server.bind((HOST, PORT))
            init_thread = threading.Thread(target=initialization_process, args=())
            init_thread.name = "init_thread"
            init_thread.start()
            binding = False
        except:
            tried_binds.append(PORT)
            bind_attempts += 1
    else:
        continue

while True:
    time.sleep(1)