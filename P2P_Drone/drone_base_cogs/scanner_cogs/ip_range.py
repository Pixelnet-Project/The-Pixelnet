# addressInNetwork and calcDottedNetmask functions courtesy of: https://stackoverflow.com/a/3188535
from . import get_ip
from . import netmask_determine
from netaddr import IPNetwork
def ip_range():
    """[summary]
    Uses the get_ip module to get the current IP address of the current bot, and then extrapolates the bot's IP to find the IP range of the network. 
    This module is used exclusively in the neighborhood_scanner module to give the scanner the parameters it needs to scan the local area network.
    """
    ip = get_ip.get_ip()
    netmask = netmask_determine.netmask()
    ip_prefix = "/" + str(sum([bin(int(x)).count('1') for x in netmask.split('.')]))
    suffixed_ip = ip + ip_prefix
    print(suffixed_ip)
    netaddr_ip = IPNetwork(suffixed_ip)
    max_range = netaddr_ip.size
    return int(max_range)