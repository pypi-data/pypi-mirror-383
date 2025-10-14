import sys
sys.path.append("..")

import unittest
from testVS_SpotifyClient_Base import Test_SpotifyClient_Base

# external package imports.
from smartinspectpython.siauto import *

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# ZeroconfConnect Tests.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_ZeroconfConnect(Test_SpotifyClient_Base): 
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_Connect(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_Connect"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # set credentials used to login to Spotify from the device.
            # accepts either the username (e.g. 'thlucas2010@gmail.com') or canonical user id (e.g. '31l77y2al5lnn7mxfrmd4bpfhqke')
            username = 'thlucas2010@gmail.com' 
            password = 'Crazy$1spot'
            loginid  = '31l77y2al5lnn7mxfrmd4bpfhqke'

            # username = 'yourspotifyusername' 
            # password = 'yourspotifypassword'
            # loginid  = 'yourspotifyloginid'

            # create Spotify Zeroconf API connection object for the device.
            zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.82', 8200, '/zc', tokenStorageDir='./test/testdata')
            
            # disconnect the device from Spotify Connect.
            print('\nDisconnecting device:%s' % zconn.ToString())
            result:ZeroconfResponse = zconn.Disconnect()
            print('\nResult - %s' % result.ToString())
            
            # connect the device to Spotify Connect, which should make it known to any available
            # Spotify Connect player clients.
            print('\nConnecting device:%s' % zconn.ToString())
            result:ZeroconfResponse = zconn.Connect(username, password, loginid)
            print('\nResult - %s' % result.ToString())

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_Connect_SONOS01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_Connect_SONOS01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # set credentials used to login to Spotify from the device.
            # accepts either the username (e.g. 'thlucas2010@gmail.com') or canonical user id (e.g. '31l77y2al5lnn7mxfrmd4bpfhqke')
            username = 'thlucas2010@gmail.com' 
            password = 'Crazy$1spot'
            loginid  = '31l77y2al5lnn7mxfrmd4bpfhqke'

            # username = '31l77y2al5lnn7mxfrmd4bpfhqke' 
            # password = 'Crazy$1spot'
            # loginid  = '2d64ca6c336932a6f7e64bd2fd5ff549'

            # create Spotify Zeroconf API connection object for the device.
            zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.91', 1400, '/spotifyzc', tokenStorageDir='./test/testdata', tokenAuthInBrowser=True)
            
            # disconnect the device from Spotify Connect.
            print('\nDisconnecting device:%s' % zconn.ToString())
            result:ZeroconfResponse = zconn.Disconnect()
            print('\nResult - %s' % result.ToString())
            
            # connect the device to Spotify Connect, which should make it known to any available
            # Spotify Connect player clients.
            print('\nConnecting device:%s' % zconn.ToString())
            result:ZeroconfResponse = zconn.Connect(username, password, loginid)
            print('\nResult - %s' % result.ToString())

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_Connect_SPOTIFYD(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_Connect_SPOTIFYD"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # set credentials used to login to Spotify from the device.
            # for librespot devices, only the loginId is needed, as the librespot credentials.json
            # contains the authentication details.
            loginid  = '31l77y2al5lnn7mxfrmd4bpfhqke'

            # create Spotify Zeroconf API connection object for the device.
            zconn:ZeroconfConnect = ZeroconfConnect('THLUCASI9.local', 8669, '/', '2.7.1', tokenStorageDir='./test/testdata', tokenAuthInBrowser=True)
            
            # # disconnect the device from Spotify Connect.
            # print('\nDisconnecting device:%s' % zconn.ToString())
            # result:ZeroconfResponse = zconn.Disconnect()
            # print('\nResult - %s' % result.ToString())
            
            # connect the device to Spotify Connect, which should make it known to any available
            # Spotify Connect player clients.
            print('\nConnecting device:%s' % zconn.ToString())
            result:ZeroconfResponse = zconn.Connect(None, None, loginid)
            print('\nResult - %s' % result.ToString())

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_Disconnect(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_Disconnect"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify Zeroconf API connection object for the device.
            zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.82', 8200, '/zc', tokenStorageDir='./test/testdata')
            
            # disconnect the device from Spotify Connect.
            print('\nDisconnecting device:%s' % zconn.ToString())
            result:ZeroconfResponse = zconn.Disconnect()
            print('\nResult - %s' % result.ToString())
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_Disconnect_SONOS01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_Disconnect_SONOS01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify Zeroconf API connection object for the device.
            zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.91', 1400, '/spotifyzc', tokenStorageDir='./test/testdata')
            
            # disconnect the device from Spotify Connect.
            print('\nDisconnecting device:%s' % zconn.ToString())
            result:ZeroconfResponse = zconn.Disconnect()
            print('\nResult - %s' % result.ToString())
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_Disconnect_SPOTIFYD(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_Disconnect_SPOTIFYD"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify Zeroconf API connection object for the device.
            zconn:ZeroconfConnect = ZeroconfConnect('THLUCASI9.local', 8669, '/', '2.7.1', tokenStorageDir='./test/testdata')
            
            # *** NOTE - this method will always fail, as librespot does not implement the zeroconf removeUsers endpoint!

            # disconnect the device from Spotify Connect.
            print('\nDisconnecting device:%s' % zconn.ToString())
            result:ZeroconfResponse = zconn.Disconnect()
            print('\nResult - %s' % result.ToString())
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetInformation(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetInformation"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)
            
            # create Spotify Zeroconf API connection object for the device.
            zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.82', 8200, '/zc', '2.9.0', tokenStorageDir='./test/testdata')
            #zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.82', 8200, '/zc', tokenStorageDir='./test/testdata')
            
            # get Spotify Zeroconf information for the device.
            print('\nGetting Spotify Zeroconf information for device:%s' % zconn.ToString())
            result:ZeroconfGetInfo = zconn.GetInformation()
            print('\nResult - %s' % result.ToString())
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetInformation_SONOS01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetInformation_SONOS01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)
            
            # create Spotify Zeroconf API connection object for the device.
            zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.91', 1400, '/spotifyzc', tokenStorageDir='./test/testdata')
            
            # get Spotify Zeroconf information for the device.
            print('\nGetting Spotify Zeroconf information for device:%s' % zconn.ToString())
            result:ZeroconfGetInfo = zconn.GetInformation()
            print('\nResult - %s' % result.ToString())
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
