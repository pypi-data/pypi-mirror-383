# Found at: https://www.murata.com/-/media/webrenewal/products/sensor/accel/sca10h_11h/sca11h_ssdp_discoverysamplecode.ashx

# external package imports.
import sys
import socket
import ipaddress
import argparse

# our package imports.

# load SmartInspect settings from a configuration settings file.
from smartinspectpython.siauto import *
print("** Loading SmartInspect configuration settings")
siConfigPath:str = "./test/smartinspect.cfg"
SIAuto.Si.LoadConfiguration(siConfigPath)

# start monitoring the configuration file for changes, and reload it when it changes.
# this will check the file for changes every 60 seconds.
print("** Starting SmartInspect configuration settings watchdog")
siConfig:SIConfigurationTimer = SIConfigurationTimer(SIAuto.Si, siConfigPath)

# get smartinspect logger reference and log basic system / domain details.
_logsi:SISession = SIAuto.Main            
_logsi.LogSeparator(SILevel.Fatal)
_logsi.LogAppDomain(SILevel.Message)
_logsi.LogSystem(SILevel.Message)

print("** Test Starting")

SSDP_MULTICAST_IP = b'239.255.255.250'
SSDP_MULTICAST_PORT = 1900
DEFAULT_TIMEOUT = 4.0
RECV_BUF_SIZE = 2048

# SSDP_DISCOVER_STRING = (b'M-SEARCH * HTTP/1.1\r\n' +
#                         b'HOST: 239.255.255.250:1900\r\n' +
#                         b'MAN: "ssdp:discover"\r\n' +
#                         b'MX: 3\r\n' +
#                         b'ST: ssdp:all\r\n' +
#                         b'\r\n')

# SSDP_DISCOVER_STRING = (b'M-SEARCH * HTTP/1.1\r\n' +
#                         b'HOST: 239.255.255.250:1900\r\n' +
#                         b'MAN: "ssdp:discover"\r\n' +
#                         b'MX: 2\r\n' +
#                         b'ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n' +
#                         b'\r\n')

SSDP_DISCOVER_STRING = (b'M-SEARCH * HTTP/1.1\r\n' +
                        b'HOST: 239.255.255.250:1900\r\n' +
                        b'MAN: "ssdp:discover"\r\n' +
                        b'MX: 2\r\n' +
                        b'ST: urn:schemas-upnp-org:device:MediaServer:1\r\n' +
                        b'\r\n')



class lsupnp:
    """Enumerate UPnP devices.
    
    'lsupnp' is short for 'list UPnP', in the same vein as lsusb, lsscsi, etc.
    """

    def __init__(self):
        """Instantiate an lsupnp object.

        All command-line options get their default values here.
        """
        self.opt_port = 0
        self.opt_rdns = True
        self.opt_verbose = True
        self.opt_timeout = DEFAULT_TIMEOUT


    def __str__(self):
        return "{0}: port={1} rdns={2} verbose={3} timeout={4}".format( \
            self.__class__.__name__, self.opt_port, self.opt_rdns, 
            self.opt_verbose, self.opt_timeout)


    def discover_hosts(self):
        """Discover all UPnP-enabled devices on a network.

        Returns:
            0 on success, errno on exception.
        """
        socket.setdefaulttimeout(self.opt_timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.opt_port > 0:
            try:
                sock.bind(('', self.opt_port))
            except OSError as e:
                print("Socket bind failed: {0}".format(e))
                return e.errno

        sock.sendto(SSDP_DISCOVER_STRING, (SSDP_MULTICAST_IP, SSDP_MULTICAST_PORT))

        try:
            hosts = []

            while True:
                data, server = sock.recvfrom(RECV_BUF_SIZE)

                # Get the IP address
                if server[0] not in hosts:
                    hosts.append(server[0])

                if self.opt_verbose == True:
                    print('{0}:{1}'.format(server[0], server[1]))
                    print('{0}'.format(data.decode(sys.stdout.encoding)))

        except socket.timeout:
            if self.opt_verbose == True:
                print("Socket timed out after {0:.1f} seconds".format(self.opt_timeout))
        finally:
            sock.close()

            # Do a natural sort on the IP addresses
            hosts = sorted(ipaddress.ip_address(host) for host in hosts)
            for host in hosts:
                print("{0}\t".format(host), end='')
                if self.opt_rdns == True:
                    print("{0}".format(self._rdns_lookup(str(host))), end='')
                print("")

        return 0


    def _rdns_lookup(self, ip):
        """Do a reverse DNS lookup (IP address to hostname) on the specified IP address.

        Args:
            ip: string of an IP address.

        Returns:
            A string of the associated hostname. May also be blank if no hostname found, 
            or exception data if verbose output is enabled.
        """
        hostname = ""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except socket.herror as e:
            if self.opt_verbose == True:
                hostname = e
        return hostname


try:

    print("Test Starting")
    _logsi.LogMessage("Testing SSDP", colorValue=SIColors.LightGreen)

    l = lsupnp()
    l.discover_hosts()
    
except Exception as ex:

    _logsi.LogException(None, ex)
    print("\n** Exception: %s" % str(ex))
    
finally:

    print("\n** Test Completed")

    # unwire events, and dispose of SmartInspect.
    print("** Disposing of SmartInspect resources")
    SIAuto.Si.Dispose()
