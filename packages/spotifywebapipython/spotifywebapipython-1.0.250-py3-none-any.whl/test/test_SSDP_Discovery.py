# Found at: https://www.murata.com/-/media/webrenewal/products/sensor/accel/sca10h_11h/sca11h_ssdp_discoverysamplecode.ashx

# external package imports.
from smartinspectpython.siauto import *
import socket
import time

# our package imports.

# load SmartInspect settings from a configuration settings file.
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

class SSDPClient:

    REPEAT = 10

    def ssdpSearch(self) -> None:
    
        print("Starting SSDP Search.")
        UDP_IP = '<broadcast>'
        UDP_PORT = 2000
        
        SSDP_DISCOVER_STRING = (b'M-SEARCH * HTTP/1.1\r\n' +
                                b'HOST: 239.255.255.250:1900\r\n' +
                                b'MAN: "ssdp:discover"\r\n' +
                                b'MX: 2\r\n' +
                                b'ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n' +
                                b'\r\n')
        
        # SSDP_DISCOVER_STRING = (b'M-SEARCH * HTTP/1.1\r\n' +
        #                         b'HOST: 239.255.255.250:1900\r\n' +
        #                         b'MAN: "ssdp:discover"\r\n' +
        #                         b'MX: 2\r\n' +
        #                         b'ST: urn:schemas-upnp-org:device:MediaServer:1\r\n' +
        #                         b'\r\n')
        
        networks = socket.gethostbyname_ex(socket.gethostname())[2] # Find all networks (i.e, wifi, wired)
        sockets = []
    
        for net in networks: # Connect to all networks
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Allow broadcast
            sock.bind((net, UDP_PORT)) # Connect
            sock.settimeout(1.0) # Set timeout (if no answer when reading)
            sockets.append(sock) # Save "sock" to sockets
        
        timeStart = time.time()
        devices = []
    
        print('Found devices:')
        time.sleep(0.1)
    
        while time.time() - timeStart < SSDPClient.REPEAT:
            for sock in sockets:
                try:
                    sock.sendto(SSDP_DISCOVER_STRING, (UDP_IP, UDP_PORT))
                    data, addr = sock.recvfrom(2048)
                    data = data.decode()
                    data = data[1:].split(',')
                
                    #if data[0] == '"type":"SCS-NOTIFY"': # Only accept correct responses
                    oldDevice = 0
                    print('Address: %s' % str(addr))  # test - dump address
                    print(data)  # test - dump all data
                    for dev in devices:
                        if dev[0] == data[1]:
                            oldDevice = 1
                        if not oldDevice:
                            devices.append([data[1],data[2]]) # Save found devices
                            print('\t' + data[1] + ' ' + data[2])
                            
                except Exception as ex:
                    print('Exception: %s' % str(ex))
                    
            time.sleep(0.2)
        
        if not len(devices):
            print('\tNo devices found.')

        print('')
        for sock in sockets:
            sock.close()
        
try:

    print("Test Starting")
    _logsi.LogMessage("Testing SSDP", colorValue=SIColors.LightGreen)

    client:SSDPClient = SSDPClient()
    client.ssdpSearch()
    
except Exception as ex:

    _logsi.LogException(None, ex)
    print("\n** Exception: %s" % str(ex))
    
finally:

    print("\n** Test Completed")

    # unwire events, and dispose of SmartInspect.
    print("** Disposing of SmartInspect resources")
    SIAuto.Si.Dispose()
