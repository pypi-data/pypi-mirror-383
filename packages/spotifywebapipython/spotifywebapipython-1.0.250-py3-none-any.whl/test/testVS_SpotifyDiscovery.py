import sys
sys.path.append("..")

import unittest
from testVS_SpotifyClient_Base import Test_SpotifyClient_Base

# external package imports.
from smartinspectpython.siauto import *
from zeroconf import Zeroconf

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.models import *

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# SpotifyClient Tests - Zeroconf Discovery.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyDiscovery(Test_SpotifyClient_Base): 
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_DiscoverDevices(self) -> None:
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_DiscoverDevices"

        try:

            print("Test Starting:  %s\n" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create a new instance of the discovery class.
            # we will print device details to the console as they are discovered.
            discovery:SpotifyDiscovery = SpotifyDiscovery(printToConsole=True)

            # discover Spotify Connect devices on the network, waiting up to 
            # the specified seconds for all devices to be discovered.
            discovery.DiscoverDevices(timeout=4)
            
            # print all discovered devices.
            _logsi.LogText(SILevel.Message, "Discovered Spotify Connect Devices (%i items)" % len(discovery), discovery.ToString(True), colorValue=SIColors.LightGreen)
            print("\n%s" % (discovery.ToString(True)))
           
            # print all discovered devices (detailed information).
            print("\nDetailed Discovery Results:")
            oResult: ZeroconfDiscoveryResult
            for oResult in discovery.DiscoveryResults:
                _logsi.LogObject(SILevel.Message,'ZeroConf Discovery Result: "%s" (%s:%d) [%s]' % (oResult.DeviceName, oResult.HostIpAddress, oResult.HostIpPort, oResult.HostIpAddress), oResult, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message,'ZeroConf Discovery Result: "%s" (%s:%d) [%s] (Dictionary)' % (oResult.DeviceName, oResult.HostIpAddress, oResult.HostIpPort, oResult.HostIpAddress), oResult.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print('\n- %s' % oResult.ToString())

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()

