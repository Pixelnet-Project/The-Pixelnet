import zlib
import logging
def head_recv(conn, addr):
    """[summary]
    This function is used to "behead" the header that is sent to this bot. This function is to be used to receive messages, and to unwrap them to be readable
    for the .ipmessage that other modules use. 
    Args:
        conn ([socket]): [A socket to an incoming connection]
        addr ([str]): [An IPv4 address without a port number]

    Returns:
        [list]: [An error message that contains what type of error as well as what the error was specifically.]
        [str]: [An unwrapped message from a outgoing link.]
    """
    logging.basicConfig(filename=f'./debug/head_recv-{addr}.log', filemode='a+', format='%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s')
    conn.settimeout(5)
    while 1:
        try:
            message_raw = conn.recv(2048)
        except Exception as e:
            logging.critical(f"Could not receive messages from conn {conn}, addr {addr}", exc_info=True)
            return ["FATAL_CONNECTION_ERROR", "LOCAL_ERROR"]
        if message_raw:
            message = message_raw.decode('utf-8')
            message = str(message)
            message_split = message.split()
            message = message_split[3:]
            message.remove("[$!FOOTER$!]")
            #NOTE: For now, this solution is TEMPORARY. This can currently only handle messages that have 1 space between the characters. Any more, and the entire message is trash.
            message = " ".join(message)
            message = str(message)
            print(message)
            if message_split:
                if int(zlib.crc32(bytes(message, "utf-8"))) == int(message_split[2]):
                    if "[!$HEADER$!]" in message_split:
                        if "[$!FOOTER$!]" in message_split:
                            if len(message) == int(message_split[1]):
                                if "LOCAL_ERROR" not in message_split:
                                        return message
                                else:
                                    logging.warning(f"An attempted error_hijack has been attempted. Full message: {message_split}")
                                    return ["ATTEMPTED_ERROR_HIJACK", "SECURITY_ALERT"]
                            else:
                                logging.error(f"Message length does not match expected length Full message: {message_split}")
                                return ["MESSAGE_LEN_ERROR", "LOCAL_ERROR"]
                        else:
                            logging.error(f"A Footer is Missing or compromised. Full message: {message_split}")
                            return ["FOOTER_ERROR", "LOCAL_ERROR"]
                    else:
                        logging.error(f"A Header is Missing or compromised. Full message: {message_split}")
                        return ["HEADER_ERROR", "LOCAL_ERROR"]
                else:
                    logging.error(f"A CRC matching error has occurred. Full message: {message_split}")
                    return ["CRC_ERROR", "LOCAL_ERROR"]
        else:
            return message_raw
