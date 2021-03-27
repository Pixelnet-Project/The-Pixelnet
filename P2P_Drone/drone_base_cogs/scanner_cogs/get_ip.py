import socket
import logging
def get_ip():
    """[summary]
    An important function that gets the IP of the current bot. DO NOT REMOVE. 
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
        logging.info("Could not get own IP address, assuming that IP address is localhost.", exc_info=True)
    return IP