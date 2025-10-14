import sys
sys.path.append("..")

import unittest
from testVS_SpotifyClient_Base import Test_SpotifyClient_Base

# external package imports.
from smartinspectpython.siauto import *

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.models import *
from spotifywebapipython.spotifyconnect import *

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# SpotifyConnect Tests.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyConnect(Test_SpotifyClient_Base): 
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_AddDynamicDevice(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_AddDynamicDevice"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # log all spotify connect devices.
            scDevices = spotify.GetSpotifyConnectDevices(refresh=True)
            print('\nSpotify Connect device list (before) ...')
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

            # add dynamic device to Spotify Connect Devices collection.
            device:Device = Device()
            device.Id = "1234567890123456789012345678901234567890"
            device.Name = "MyNewDevice"
            device.Type = "SPEAKER"
            print('\nAdding new dynamic device: \"%s\" ...' % (device.Name))
            spotify.SpotifyConnectDirectory.AddDynamicDevice(device)

            # log all spotify connect devices.
            scDevices = spotify.GetSpotifyConnectDevices(refresh=False)
            print('\nSpotify Connect device list (after add) ...')
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

            # remove dynamic device from Spotify Connect Devices collection.
            print('\nRemoving existing dynamic device: \"%s\" ...' % (device.Name))
            spotify.SpotifyConnectDirectory.RemoveDevice(device.Id, dynamicDeviceOnly=True)

            # log all spotify connect devices.
            scDevices = spotify.GetSpotifyConnectDevices(refresh=False)
            print('\nSpotify Connect device list (after remove) ...')
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
        finally:

            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)
        

    def test_AddDynamicDevice_ALIAS(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_AddDynamicDevice_ALIAS"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # log all spotify connect devices.
            scDevices = spotify.GetSpotifyConnectDevices(refresh=True)
            print('\nSpotify Connect device list (before) ...')
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

            # add dynamic device to Spotify Connect Devices collection.
            device:Device = Device()
            device.Id = "1234567890123456789012345678901234567890"
            device.Name = "MyNewDevice"
            device.Type = "SPEAKER"
            print('\nAdding new dynamic device: \"%s\" ...' % (device.Name))
            spotify.SpotifyConnectDirectory.AddDynamicDevice(device)

            # log all spotify connect devices.
            scDevices = spotify.GetSpotifyConnectDevices(refresh=False)
            print('\nSpotify Connect device list (after add) ...')
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

            # remove dynamic device from Spotify Connect Devices collection.
            print('\nRemoving existing dynamic device: \"%s\" ...' % (device.Name))
            spotify.SpotifyConnectDirectory.RemoveDevice(device.Id, dynamicDeviceOnly=True)

            # log all spotify connect devices.
            scDevices = spotify.GetSpotifyConnectDevices(refresh=False)
            print('\nSpotify Connect device list (after remove) ...')
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
        finally:

            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)
        

    def test_GetActiveDevice(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetActiveDevice"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get active device info.
            print('\nGetting active player device ...\n')
            scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetActiveDevice()
            if scDevice is not None:
                _logsi.LogObject(SILevel.Message,"Active Device: %s" % (scDevice.Title), scDevice, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, "Active Device: %s (Dictionary)" % (scDevice.Title), scDevice.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(scDevice))
            else:
                _logsi.LogMessage("Active device not found: \"%s\"" % (device), colorValue=SIColors.LightGreen)
                print("No active device")

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
        finally:

            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)
        

    def test_GetDevice(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetDevice"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get device info - by name.
            # exception will be raised if device was not resolved.
            device:str = "Bose-ST10-2"
            print("\nDevice info - by name \"%s\" ..." % (device))
            scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice(device)

            # log results.
            _logsi.LogObject(SILevel.Message,"Device info - by name: %s" % (scDevice.Title), scDevice, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, "Device info - by name: %s (Dictionary)" % (scDevice.Title), scDevice.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(scDevice) + "\n")

            # get device info - by id.
            # exception will be raised if device was not resolved.
            device:str = "5d4931f9d0684b625d702eaa24137b2c1d99539c"
            print("\nDevice info - by id \"%s\" ..." % (device))
            scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice(device)

            # log results.
            _logsi.LogObject(SILevel.Message,"Device info - by id: %s" % (scDevice.Title), scDevice, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, "Device info - by id: %s (Dictionary)" % (scDevice.Title), scDevice.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(scDevice) + "\n")

            # get device info - by * default.
            # exception will be raised if device was not resolved.
            spotify.DefaultDeviceId = "Bose-ST10-1111"
            device:str = "*"
            print("\nDevice info - by * default  \"%s\" ..." % (device))
            scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice(device)

            # log results.
            _logsi.LogObject(SILevel.Message,"Device info - by * default: %s" % (scDevice.Title), scDevice, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, "Device info - by * default: %s (Dictionary)" % (scDevice.Title), scDevice.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(scDevice) + "\n")

            # get device info - by default.
            # exception will be raised if device was not resolved.
            device:str = None
            print("\nDevice info - by active default  \"%s\" ..." % (device))
            scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice(device)

            # log results.
            _logsi.LogObject(SILevel.Message,"Device info - by active default: %s" % (scDevice.Title), scDevice, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, "Device info - by active default: %s (Dictionary)" % (scDevice.Title), scDevice.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(scDevice) + "\n")

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
        finally:

            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)
        

    def test_GetDevices(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetDevices"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get devices from Spotify Connect Directory task.
            # note that collection is already sorted as devices are added.
            scDevices:SpotifyConnectDevices = spotify.SpotifyConnectDirectory.GetDevices()

            # log all spotify connect devices.
            print('\nSpotify Connect device list (after) ...')
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
        finally:

            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)
        

    def test_GetPlayerDevice(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetActiveDevice"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get player device info - by name.
            device:str = "Bose-ST10-1"
            print("\nPlayer device info - by name \"%s\" ..." % (device))
            scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetPlayerDevice(device, refresh=True)
            if scDevice is not None:
                _logsi.LogObject(SILevel.Message,"Player Device info - by name: %s" % (scDevice.Title), scDevice, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, "Player Device info - by name: %s (Dictionary)" % (scDevice.Title), scDevice.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(scDevice) + "\n")
            else:
                _logsi.LogMessage("Player device not found: \"%s\"" % (device), colorValue=SIColors.LightGreen)
                print("Player device not found: \"%s\"" % (device))

            # get player device info - by id.
            device:str = "30fbc80e35598f3c242f2120413c943dfd9715fe"
            print("\nPlayer device info - by id \"%s\" ..." % (device))
            scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetPlayerDevice(device, refresh=True)
            if scDevice is not None:
                _logsi.LogObject(SILevel.Message,"Player Device info - by id: %s" % (scDevice.Title), scDevice, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, "Player Device info - by id: %s (Dictionary)" % (scDevice.Title), scDevice.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(scDevice) + "\n")
            else:
                _logsi.LogMessage("Player device not found: \"%s\"" % (device), colorValue=SIColors.LightGreen)
                print("Player device not found: \"%s\"" % (device))

            # get player device info - by unknown name.
            device:str = "MyName"
            print("\nPlayer device info - by unknown name \"%s\" ..." % (device))
            scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetPlayerDevice(device, refresh=True)
            if scDevice is not None:
                _logsi.LogObject(SILevel.Message,"Player Device info - by unknown name: %s" % (scDevice.Title), scDevice, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, "Player Device info - by unknown name: %s (Dictionary)" % (scDevice.Title), scDevice.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(scDevice) + "\n")
            else:
                _logsi.LogMessage("Player device not found: \"%s\"" % (device), colorValue=SIColors.LightGreen)
                print("Player device not found: \"%s\"" % (device))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
        finally:

            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)
        

    def test_RefreshDynamicDevices(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RefreshDynamicDevices"

        # The best way to execute this sample is to set a breakpoint on the 
        # ".RefreshDynamicDevices()" line, and debug the sample.  Once the
        # breakpoint is hit, open the Spotify Web Player in a new browser
        # window (or even the Spotify Desktop app). Continue debugging the
        # sample; the new Spotify player should show up as a dynamic device
        # in the output log.

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # log all spotify connect devices.
            scDevices = spotify.GetSpotifyConnectDevices(refresh=True)
            print('\nSpotify Connect device list (before) ...')
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

            # refresh the player device list, and return the active device.
            scActiveDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.RefreshDynamicDevices()

            # log all spotify connect devices.
            scDevices = spotify.GetSpotifyConnectDevices(refresh=False)
            print('\nSpotify Connect device list (after) ...')
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
        finally:

            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)
        

    def test_UpdateActiveDevice(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_UpdateActiveDevice"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # log active device info.
            print('\nGetting active player device (before) ...\n')
            scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetActiveDevice()
            if scDevice is not None:
                print(str(scDevice))
            else:
                print("No active device")

            # updates currently active device based on current playerState.
            scActiveDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.UpdateActiveDevice()

            # updates currently active device based on specified playerState.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            scActiveDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.UpdateActiveDevice(playerState)

            # log active device info.
            print('\nActive player device (after) ...\n')
            if scActiveDevice is not None:
                print(str(scActiveDevice))
            else:
                print("No active device")

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
        finally:

            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)
        

    def test_UpdatePlayerDevices(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_UpdatePlayerDevices"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # log all spotify connect devices.
            scDevices = spotify.GetSpotifyConnectDevices(refresh=True)
            print('\nSpotify Connect device list (before) ...')
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

            # update player device list.
            spotify.SpotifyConnectDirectory.UpdatePlayerDevices()

            # log all spotify connect devices.
            scDevices = spotify.GetSpotifyConnectDevices(refresh=False)
            print('\nSpotify Connect device list (after) ...')
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
        finally:

            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
