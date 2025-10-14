# external package imports.
from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *

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

try:

    print("Test Starting\n")
    _logsi.LogMessage("Testing ZeroSpot", colorValue=SIColors.LightGreen)

    # Spotify premium account info:
    # Disconnect = success.
    # Connect = success - device shows up in the device list of the Spotify Connect Player if UID / PWD are correct.
    username = 'thlucas2010@gmail.com'
    password = 'Crazy$1spot'
    loginid  = '31l77y2al5lnn7mxfrmd4bpfhqke'
    
    # create Spotify Zeroconf API connection object for the device.
    zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.81', 8200, '/zc', useSSL=False, tokenStorageDir='./test/testdata')

    # get Spotify Zeroconf information for the device.
    print('\nGetting Spotify Zeroconf information for device:%s' % zconn.ToString())
    result:ZeroconfGetInfo = zconn.GetInformation()
    print('\nResult - %s' % result.ToString())

except Exception as ex:

    _logsi.LogException(None, ex)
    print(str(ex))
        
finally:
            
    print("\nTests Completed")

    # dispose of SmartInspect.
    print("** Disposing of SmartInspect resources")
    SIAuto.Si.Dispose()