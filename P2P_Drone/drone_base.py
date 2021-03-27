import socket
import time
import random
import sys
import threading
import os
import logging
if not os.path.isdir("./debug"):
    try:
        os.mkdir("./debug")
    except Exception as e:
        print(e)
logging.basicConfig(filename='./debug/init_sequence.log', filemode='a+', format='%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s')
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
    except:
        logging.critical("Could not determine name of self", exc_info=True)
    if ".pyw" in self_name:
        sys.stdout = open(os.devnull, 'w')
    try:
        # Should be noted that after finishing development on VSCode, this needs to be taken out to mean in the context of the stand-alone drone
        os.remove("./permanence_files/peer_scan.lock")
    except:
        logging.critical("Could not remove the peer_scan.lock!", exc_info=True)
    try:
        shutil.rmtree("./permanence_files\ip_messages")
    except:
        logging.error("Could not remove the directory tree of permanence_files!", exc_info=True)
    neighborhood_scanner_init_thread = threading.Thread(target=neighborhood_scanner.peer_scan, args=())
    neighborhood_scanner_init_thread.name = "init_scanner_thread"
    neighborhood_scanner_init_thread.start()
    p2p_server_thread = threading.Thread(target=incoming_link.p2p_welcomer, args=(server,))
    p2p_server_thread.name = "p2p_welcomer"
    p2p_server_thread.start()
tried_binds = []
while binding == True:
    HOST = get_ip.get_ip()
    PORT = random.randrange(49995, 50000)
    if bind_attempts >= 5:
        logging.critical(f"Could not bind to the bot with the following tried binds: {tried_binds}", exc_info=True)
        sys.exit()
    if PORT not in tried_binds:
        try:
            server.bind((HOST, PORT))
            try:
                init_thread = threading.Thread(target=initialization_process, args=())
                init_thread.name = "init_thread"
                init_thread.start()
            except:
                logging.critical("Could not start init thread!", exc_info=True)
                sys.exit()
            binding = False
        except:
            tried_binds.append(PORT)
            bind_attempts += 1
    else:
        continue

while True:
    time.sleep(1)