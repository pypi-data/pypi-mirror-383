import sys
sys.path.append("..")

import unittest
from testVS_SpotifyClient_Base import Test_SpotifyClient_Base

# external package imports.
from datetime import datetime
from smartinspectpython.siauto import *
import time

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.models import *
from spotifywebapipython.zeroconfapi import ZeroconfConnect, ZeroconfResponse

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# SpotifyClient Tests - Player.
#
# Test Uri's:
# Uri="spotify:artist:6APm8EjxOHSYM5B4i3vT3q" - Artist="MercyMe"
# Uri="spotify:album:6vc9OTcyd3hyzabCmsdnwE"  - Artist="MercyMe", Album="Welcome to the New"
# Uri="spotify:track:1kWUud3vY5ij5r62zxpTRy"  - Artist="MercyMe", Album="Welcome to the New", Track="Flawless"
#
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Player(Test_SpotifyClient_Base):
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_AddPlayerQueueItems(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_AddPlayerQueueItems"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Google Home 01" # Chromecast device
            #deviceId:str = "Google Group 01" # Chromecast device
            #deviceId:str = "Google Group 02" # Chromecast device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Nest Group 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # add item(s) to the end of the user's current playback queue.
            #uris:str = 'spotify:track:27JODWXo4VNa6s7HqDL9yQ'
            #uris:str = 'spotify:track:4iV5W9uYEdYUVa79Axb7Rh, spotify:track:27JODWXo4VNa6s7HqDL9yQ'
            uris:str='spotify:track:2VAtZmI9nCB97Kdnn9tMIF, spotify:track:6ZRKMJ7x5WGHuyUjoZjNEu, spotify:track:1u21AFQtqUHHlqePHk3qUL, spotify:track:4Wea9K8KRTsrlfIks5yepP, spotify:track:3ji2WLLlpJmvvSOlAyqB6p'
            #uris:str='spotify:track:2VAtZmI9nCB97Kdnn9tMIF, spotify:track:6ZRKMJ7x5WGHuyUjoZjNEu, spotify:track:1u21AFQtqUHHlqePHk3qUL, spotify:track:4Wea9K8KRTsrlfIks5yepP, spotify:track:3ji2WLLlpJmvvSOlAyqB6p, spotify:track:3wFt2cfgRnGarpybCiCHj2, spotify:track:6FVg2subR7uoD80BmTOsdR, spotify:track:3rmzOry93Q6CQuHKVyBTQm, spotify:track:1RGV3trL1O9FgIrv8FcjRU, spotify:track:1z5YtEopKg5pyjCM3BEsr5, spotify:track:5hWtMn99mB2ckaLubacTuZ, spotify:track:2ZicbtrMnz97j3WyFf4So4, spotify:track:6OC3n631AkgqbWrrQbN1yH, spotify:track:7aIvVeBrvC7K3hYbpRXRdZ, spotify:track:6Dkou08rjWrgGijVmoAVZp, spotify:track:68x16tb33FQdWyiOaZYteP, spotify:track:1FlPIUDSRIxrulONSUQRaN, spotify:track:7KT088cs0FVVQum6IyT0X9, spotify:track:43yFiQ18Nhnb2YJwk09f3a, spotify:track:15eJjGIuCDEtF6ph4Hd3eR'
            print('\nAdding items to the users current playback queue:\n- "%s" ...' % (uris))
            spotify.AddPlayerQueueItems(uris, deviceId)

            _logsi.LogMessage('Success - items were added to the queue', colorValue=SIColors.LightGreen)
            print('\nSuccess - items were added to the queue')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
               

    def test_GetDevicePlaybackState(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetDevicePlaybackState"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Google Home 01" # Chromecast device
            #deviceId:str = "Google Group 01" # Chromecast device
            #deviceId:str = "Google Group 02" # Chromecast device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Nest Group 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get Spotify Connect playback state.
            print('\nGetting Spotify Connect device playback state ...\n- Device = \"%s\"' % (deviceId))
            playerState:PlayerPlayState = spotify.GetDevicePlaybackState(deviceId)

            if playerState.IsEmpty:

                print('Spotify Connect device playback State is unavailable at this time')

            else:

                _logsi.LogObject(SILevel.Message, 'PlayerPlayState: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState: %s (Dictionary)' % (playerState.Summary), playerState.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(playerState))
                print('')
                print(str(playerState.Item))
                print('')
                print(str(playerState.Device))
                print('')
                print(str(playerState.Actions))
                print('')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetDevicePlaybackState_FREE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetDevicePlaybackState_FREE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_FREE()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Google Home 01" # Chromecast device
            #deviceId:str = "Google Group 01" # Chromecast device
            #deviceId:str = "Google Group 02" # Chromecast device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Nest Group 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get Spotify Connect playback state.
            print('\nGetting Spotify Connect device playback state ...\n- Device = \"%s\"' % (deviceId))
            playerState:PlayerPlayState = spotify.GetDevicePlaybackState(deviceId)

            if playerState.IsEmpty:

                print('Spotify Connect device playback State is unavailable at this time')

            else:

                _logsi.LogObject(SILevel.Message, 'PlayerPlayState: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState: %s (Dictionary)' % (playerState.Summary), playerState.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(playerState))
                print('')
                print(str(playerState.Item))
                print('')
                print(str(playerState.Device))
                print('')
                print(str(playerState.Actions))
                print('')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerDevice(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerDevice"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify Connect player device by it's Id value.
            deviceId:str = '30fbc80e35598f3c242f2120413c943dfd9715fe'
            print('\nGetting Spotify Connect player device: \n- ID = "%s" ...\n' % deviceId)
            device:Device = spotify.GetPlayerDevice(deviceId)

            if device is not None:
                _logsi.LogObject(SILevel.Message,'Device: "%s" (%s)' % (device.Name, device.Id), device, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'Device: "%s" (%s) (Dictionary)' % (device.Name, device.Id), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(device))
            else:
                print("Device Id was not found in the list of devices")

            # get Spotify Connect player device by it's Name value.
            deviceName:str = 'Bose-ST10-1'
            print('\nGetting Spotify Connect player device: \n- Name = "%s" ...\n' % deviceName)
            device:Device = spotify.GetPlayerDevice(deviceName)

            if device is not None:
                _logsi.LogObject(SILevel.Message,'Device: "%s" (%s)' % (device.Name, device.Id), device, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'Device: "%s" (%s) (Dictionary)' % (device.Name, device.Id), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(device))
            else:
                print("Device Name was not found in the list of devices")
    
            # get cached configuration, refreshing from device if needed.
            device:Device = spotify.GetPlayerDevice(deviceId, refresh=False)
            print("\nCached configuration (by Id):\n%s" % str(device))

            # get cached configuration, refreshing from device if needed.
            device:Device = spotify.GetPlayerDevice(deviceName, refresh=False)
            print("\nCached configuration (by Name):\n%s" % str(device))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerDevices(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerDevices"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get information about a user's available Spotify Connect player devices.
            print('\nGetting available Spotify Connect player devices ...')
            playerDevices:list[Device] = spotify.GetPlayerDevices()

            # log device summary.
            print('\nDevice Summary:')
            device:Device
            for device in playerDevices:
                print('- "%s"' % device.SelectItemNameAndId)
    
            # log device details.
            print('\nDevice Details:\n')
            device:Device
            for device in playerDevices:
                
                _logsi.LogObject(SILevel.Message,'Device: "%s" (%s)' % (device.Name, device.Id), device, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'Device: "%s" (%s) (Dictionary)' % (device.Name, device.Id), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(device))
                print(' SelectItemNameAndId = "%s"' % device.SelectItemNameAndId)
                print(' GetIdFromSelectItem = "%s"' % Device.GetIdFromSelectItem(device.SelectItemNameAndId))
                print(' GetNameFromSelectItem = "%s"' % Device.GetNameFromSelectItem(device.SelectItemNameAndId))
                print('')
    
            # get cached configuration, refreshing from device if needed.
            playerDevices:list[Device] = spotify.GetPlayerDevices(refresh=False)
            print("\nCached configuration (count): %d" % len(playerDevices))

            # get cached configuration directly from the configuration manager dictionary.
            if "GetPlayerDevices" in spotify.ConfigurationCache:
                playerDevices:list[Device] = spotify.ConfigurationCache["GetPlayerDevices"]
                print("\nCached configuration direct access (count): %d" % len(playerDevices))

            # add dynamic devices to Spotify Connect Devices collection.
            scActiveDevice:SpotifyConnectDevice = None
            scDevices:SpotifyConnectDevices = spotify.GetSpotifyConnectDevices(refresh=False)
            playerDevices:list[Device] = spotify.GetPlayerDevices(refresh=True)
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            spotify.SpotifyConnectDirectory.UpdatePlayerDevices(playerDevices)
            scActiveDevice = spotify.SpotifyConnectDirectory.UpdateActiveDevice(playerState)
            #scActiveDevice2 = spotify.SpotifyConnectDirectory.GetActiveDevice()

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerNowPlaying(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerNowPlaying"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get the object currently being played on the user's Spotify account.
            print('\nGetting object that is now playing on the users account ...\n')
            nowPlaying:PlayerPlayState = spotify.GetPlayerNowPlaying()

            if nowPlaying.CurrentlyPlayingType is not None:
                
                _logsi.LogObject(SILevel.Message, 'PlayerPlayState: %s' % (nowPlaying.Summary), nowPlaying, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState: %s (Dictionary)' % (nowPlaying.Summary), nowPlaying.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(nowPlaying))
                print('')
                print(str(nowPlaying.Item))
                print('')
                print(str(nowPlaying.Device))
               
            else:
                
                print('Nothing is currently playing via Spotify Connect')

            _logsi.LogObject(SILevel.Message, 'PlayerLastPlayedInfo: %s' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerLastPlayedInfo: %s (Dictionary)' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerNowPlaying_Episode(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerNowPlaying_Episode"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get the object currently being played on the user's Spotify account.
            print('\nGetting object that is now playing on the users account ...\n')
            nowPlaying:PlayerPlayState = spotify.GetPlayerNowPlaying(additionalTypes='episode')

            if nowPlaying.CurrentlyPlayingType is not None:
                
                _logsi.LogObject(SILevel.Message, 'PlayerPlayState: %s' % (nowPlaying.Summary), nowPlaying, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState: %s (Dictionary)' % (nowPlaying.Summary), nowPlaying.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(nowPlaying))
                print('')
                print(str(nowPlaying.Item))
               
            else:
                
                print('Nothing is currently playing via Spotify Connect')

            _logsi.LogObject(SILevel.Message, 'PlayerLastPlayedInfo: %s' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerLastPlayedInfo: %s (Dictionary)' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerNowPlaying_Track(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerNowPlaying_Track"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get the object currently being played on the user's Spotify account.
            print('\nGetting object that is now playing on the users account ...\n')
            nowPlaying:PlayerPlayState = spotify.GetPlayerNowPlaying(additionalTypes='track')

            if nowPlaying.CurrentlyPlayingType is not None:
                
                _logsi.LogObject(SILevel.Message, 'PlayerPlayState: %s' % (nowPlaying.Summary), nowPlaying, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState: %s (Dictionary)' % (nowPlaying.Summary), nowPlaying.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(nowPlaying))
                print('')
                print(str(nowPlaying.Item))
               
            else:
                
                print('Nothing is currently playing via Spotify Connect')

            _logsi.LogObject(SILevel.Message, 'PlayerLastPlayedInfo: %s' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerLastPlayedInfo: %s (Dictionary)' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerPlaybackState(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerPlaybackState"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Spotify Connect playback state.
            print('\nGetting Spotify Connect playback state ...\n')
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')

            if playerState.CurrentlyPlayingType is not None:
                
                _logsi.LogObject(SILevel.Message, 'PlayerPlayState: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState: %s (Dictionary)' % (playerState.Summary), playerState.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           

                print(str(playerState))
                print('')
                print(str(playerState.Item))
                print('')
                print(str(playerState.Device))
                print('')
                print(str(playerState.Actions))
                print('')
               
            else:
                
                print('Spotify Connect playback State is unavailable at this time')

            playerState = PlayerPlayState()
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState (empty): %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState (empty): %s (Dictionary)' % (playerState.Summary), playerState.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print("Empty PlayerPlayState Object ...\n%s" % str(playerState))
                
            _logsi.LogObject(SILevel.Message, 'PlayerLastPlayedInfo: %s' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerLastPlayedInfo: %s (Dictionary)' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerPlaybackState_SONOS(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerPlaybackState_SONOS"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Sonos device reference.
            scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice("Office", refreshDynamicDevices=False)
            #scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice("Bose-ST10-1", refreshDynamicDevices=False)

            # get Spotify Connect playback state.
            print('\nGetting Sonos device playback state ...\n')
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')

            _logsi.LogObject(SILevel.Message, 'PlayerPlayState: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState: %s (Dictionary)' % (playerState.Summary), playerState.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            if playerState.IsEmpty:

                print('Spotify Connect playback State is unavailable at this time')

            else:
                
                print(str(playerState))
                print('')
                print(str(playerState.Item))
                print('')
                print(str(playerState.Device))
                print('')
                print(str(playerState.Actions))
                print('')
               
            playerState = PlayerPlayState()
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState (empty): %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState (empty): %s (Dictionary)' % (playerState.Summary), playerState.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print("Empty PlayerPlayState Object ...\n%s" % str(playerState))
                
            _logsi.LogObject(SILevel.Message, 'PlayerLastPlayedInfo: %s' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerLastPlayedInfo: %s (Dictionary)' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerPlaybackState_SONOS_FREE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerPlaybackState_SONOS_FREE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_FREE()

            # get Sonos device reference.
            scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice("Office", refreshDynamicDevices=False)
            #scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice("Bose-ST10-1", refreshDynamicDevices=False)

            # get Spotify Connect playback state.
            print('\nGetting Sonos device playback state ...\n')
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')

            _logsi.LogObject(SILevel.Message, 'PlayerPlayState: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState: %s (Dictionary)' % (playerState.Summary), playerState.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            if playerState.IsEmpty:

                print('Spotify Connect playback State is unavailable at this time')

            else:
                
                print(str(playerState))
                print('')
                print(str(playerState.Item))
                print('')
                print(str(playerState.Device))
                print('')
                print(str(playerState.Actions))
                print('')
               
            playerState = PlayerPlayState()
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState (empty): %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState (empty): %s (Dictionary)' % (playerState.Summary), playerState.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print("Empty PlayerPlayState Object ...\n%s" % str(playerState))
                
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerPlaybackStateSonos_FREE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerPlaybackStateSonos_FREE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_FREE()

            # get Sonos device reference.
            scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice("Office", refreshDynamicDevices=False)

            # get Spotify Connect playback state.
            print('\nGetting Sonos device playback state ...\n')
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackStateSonos(scDevice)

            _logsi.LogObject(SILevel.Message, 'PlayerPlayState: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState: %s (Dictionary)' % (playerState.Summary), playerState.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            if playerState.IsEmpty:

                print('Spotify Connect playback State is unavailable at this time')

            else:
                
                print(str(playerState))
                print('')
                print(str(playerState.Item))
                print('')
                print(str(playerState.Device))
                print('')
                print(str(playerState.Actions))
                print('')
               
            playerState = PlayerPlayState()
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState (empty): %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState (empty): %s (Dictionary)' % (playerState.Summary), playerState.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print("Empty PlayerPlayState Object ...\n%s" % str(playerState))
                
            _logsi.LogObject(SILevel.Message, 'PlayerLastPlayedInfo: %s' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerLastPlayedInfo: %s (Dictionary)' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerPlaybackState_Episode(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerPlaybackState_Episode"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify Connect playback state.
            print('\nGetting Spotify Connect playback state ...\n')
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')

            if playerState.CurrentlyPlayingType is not None:
                
                _logsi.LogObject(SILevel.Message, 'PlayerPlayState: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState: %s (Dictionary)' % (playerState.Summary), playerState.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(playerState))
                print('')
                print(str(playerState.Item))
               
            else:
                
                print('Spotify Connect playback State is unavailable at this time')

            _logsi.LogObject(SILevel.Message, 'PlayerLastPlayedInfo: %s' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerLastPlayedInfo: %s (Dictionary)' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerPlaybackState_Track(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerPlaybackState_Track"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify Connect playback state.
            print('\nGetting Spotify Connect playback state ...\n')
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='track')

            if playerState.CurrentlyPlayingType is not None:
                
                _logsi.LogObject(SILevel.Message, 'PlayerPlayState: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'PlayerPlayState: %s (Dictionary)' % (playerState.Summary), playerState.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(playerState))
                print('')
                print(str(playerState.Item))
               
            else:
                
                print('Spotify Connect playback State is unavailable at this time')

            _logsi.LogObject(SILevel.Message, 'PlayerLastPlayedInfo: %s' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerLastPlayedInfo: %s (Dictionary)' % (spotify.PlayerLastPlayedInfo.Summary), spotify.PlayerLastPlayedInfo.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerQueueInfo(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerQueueInfo"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify Connect player queue info for the current user.
            print('\nGetting Spotify Connect player queue info ...\n')
            queueInfo:PlayerQueueInfo = spotify.GetPlayerQueueInfo()

            _logsi.LogObject(SILevel.Message, 'PlayerQueueInfo: %s (%s items)' % (queueInfo.Summary, queueInfo.QueueCount), queueInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'PlayerQueueInfo: %s (%s items) (Dictionary)' % (queueInfo.Summary, queueInfo.QueueCount), queueInfo.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(queueInfo))
            
            if queueInfo.CurrentlyPlaying is not None:
                _logsi.LogObject(SILevel.Message,'Currently Playing: %s - "%s" (%s)' % (queueInfo.CurrentlyPlaying.Type, queueInfo.CurrentlyPlaying.Name, queueInfo.CurrentlyPlaying.Uri), queueInfo.CurrentlyPlaying, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('\nCurrently Playing:\n%s' % queueInfo.CurrentlyPlaying)

            print('\nQueue: (%s items)' % queueInfo.QueueCount)
            for item in queueInfo.Queue:
                _logsi.LogObject(SILevel.Message,'Queue Item: %s - "%s" (%s)' % (item.Type, item.Name, item.Uri), item, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- {type}: "{name}" ({uri})'.format(type=item.Type, name=item.Name, uri=item.Uri))
                
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerRecentTracks_AfterDateTime(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerRecentTracks_AfterDateTime"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get all tracks played after UTC date 2024-01-25T21:34:16.821Z (1706218456821)
            afterMS:int = 1706218456821

            # get tracks from current user's recently played tracks.
            print('\nGetting recently played tracks for current user ...\n')
            pageObj:PlayHistoryPage = spotify.GetPlayerRecentTracks(after=afterMS)

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results - Tracks %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('')
                print('Tracks in this page of results:')
                
                # display history details.
                history:PlayHistory
                for history in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'Track: %s %s - "%s" (%s)' % (history.PlayedAt, history.PlayedAtMS, history.Track.Name, history.Track.Uri), history.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- {played_at} {played_atMS}: "{name}" ({uri})'.format(played_at=history.PlayedAt, played_atMS=history.PlayedAtMS, name=history.Track.Name, uri=history.Track.Uri))

                # anymore page results?
                if (pageObj.Next is None) \
                or (pageObj.IsCursor and pageObj.CursorAfter is None and pageObj.CursorBefore is None):
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of items ...\n')
                    pageObj = spotify.GetPlayerRecentTracks(after=pageObj.CursorAfter, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerRecentTracks_BeforeDateTime(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerRecentTracks_BeforeDateTime"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get all tracks played before 1730846315066.
            #beforeMS:int = 1730846315066
            beforeMS:int = int(datetime.utcnow().timestamp()) * 1000   # convert seconds to milliseconds

            # get tracks from current user's recently played tracks.
            print('\nGetting recently played tracks for current user ...\n')
            pageObj:PlayHistoryPage = spotify.GetPlayerRecentTracks(before=beforeMS, limitTotal=122)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results - Tracks %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(pageObj))
            print('')
            print('Tracks in this page of results:')
                
            # display history details.
            history:PlayHistory
            for history in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'Track: %s %s - "%s" (%s)' % (history.PlayedAt, history.PlayedAtMS, history.Track.Name, history.Track.Uri), history.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- {played_at} {played_atMS}: "{name}" ({uri})'.format(played_at=history.PlayedAt, played_atMS=history.PlayedAtMS, name=history.Track.Name, uri=history.Track.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerRecentTracks_Last100(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerRecentTracks_Last100"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get the last 50 tracks played from now, regardless of time period.
            beforeMS:int = GetUnixTimestampMSFromUtcNow(seconds=-1)

            # get tracks from current user's recently played tracks.
            print('\nGetting recently played tracks for current user ...\n')
            pageObj:PlayHistoryPage = spotify.GetPlayerRecentTracks()
            #pageObj:PlayHistoryPage = spotify.GetPlayerRecentTracks(before=beforeMS, limitTotal=1000)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results - Tracks %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results - Tracks %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('')
            print('Tracks in this page of results:')
                
            # display history details.
            history:PlayHistory
            for history in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'Track: %s %s - "%s" (%s)' % (history.PlayedAt, history.PlayedAtMS, history.Track.Name, history.Track.Uri), history.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message,'Track: %s %s - "%s" (%s) (Dictionary)' % (history.PlayedAt, history.PlayedAtMS, history.Track.Name, history.Track.Uri), history.Track.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print('- {played_at} {played_atMS}: "{name}" ({uri})'.format(played_at=history.PlayedAt, played_atMS=history.PlayedAtMS, name=history.Track.Name, uri=history.Track.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerRecentTracks_Past01Hours(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerRecentTracks_Past01Hours"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get all tracks played within the past 1 hour.
            afterMS:int = GetUnixTimestampMSFromUtcNow(hours=-1)     # last 1 hour
            #afterMS:int = GetUnixTimestampMSFromUtcNow(hours=-24)   # last 24 hours
            #afterMS:int = GetUnixTimestampMSFromUtcNow(days=-7)     # last 7 days

            # get tracks from current user's recently played tracks.
            print('\nGetting recently played tracks for current user ...\n')
            pageObj:PlayHistoryPage = spotify.GetPlayerRecentTracks(after=afterMS)

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results - Tracks %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('')
                print('Tracks in this page of results:')
                
                # display history details.
                history:PlayHistory
                for history in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'Track: %s %s - "%s" (%s)' % (history.PlayedAt, history.PlayedAtMS, history.Track.Name, history.Track.Uri), history.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- {played_at} {played_atMS}: "{name}" ({uri})'.format(played_at=history.PlayedAt, played_atMS=history.PlayedAtMS, name=history.Track.Name, uri=history.Track.Uri))

                # anymore page results?
                if (pageObj.Next is None) \
                or (pageObj.IsCursor and pageObj.CursorAfter is None and pageObj.CursorBefore is None):
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of items ...\n')
                    pageObj = spotify.GetPlayerRecentTracks(after=pageObj.CursorAfter, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerRecentTracks_Past07Days(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerRecentTracks_Past07Days"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get all tracks played within the past 1 hour.
            #afterMS:int = GetUnixTimestampMSFromUtcNow(hours=-1)     # last 1 hour
            #afterMS:int = GetUnixTimestampMSFromUtcNow(hours=-24)   # last 24 hours
            afterMS:int = GetUnixTimestampMSFromUtcNow(days=-7)     # last 7 days

            # get tracks from current user's recently played tracks.
            print('\nGetting recently played tracks for current user ...\n')
            pageObj:PlayHistoryPage = spotify.GetPlayerRecentTracks(after=afterMS)

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results - Tracks %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('')
                print('Tracks in this page of results:')
                
                # display history details.
                history:PlayHistory
                for history in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'Track: %s %s - "%s" (%s)' % (history.PlayedAt, history.PlayedAtMS, history.Track.Name, history.Track.Uri), history.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- {played_at} {played_atMS}: "{name}" ({uri})'.format(played_at=history.PlayedAt, played_atMS=history.PlayedAtMS, name=history.Track.Name, uri=history.Track.Uri))

                # anymore page results?
                if (pageObj.Next is None) \
                or (pageObj.IsCursor and pageObj.CursorAfter is None and pageObj.CursorBefore is None):
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of items ...\n')
                    pageObj = spotify.GetPlayerRecentTracks(after=pageObj.CursorAfter, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerRecentTracks_BeforeNow(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerRecentTracks_BeforeNow"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get tracks played before the designated time.
            beforeMS:int = GetUnixTimestampMSFromUtcNow(seconds=1)     # now

            # get tracks from current user's recently played tracks.
            print('\nGetting recently played tracks for current user ...\n')
            pageObj:PlayHistoryPage = spotify.GetPlayerRecentTracks(before=beforeMS)

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results - Tracks %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('')
                print('Tracks in this page of results:')
                
                # display history details.
                history:PlayHistory
                for history in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'Track: %s %s - "%s" (%s)' % (history.PlayedAt, history.PlayedAtMS, history.Track.Name, history.Track.Uri), history.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- {played_at} {played_atMS}: "{name}" ({uri})'.format(played_at=history.PlayedAt, played_atMS=history.PlayedAtMS, name=history.Track.Name, uri=history.Track.Uri))

                # anymore page results?
                if (pageObj.Next is None) \
                or (pageObj.IsCursor and pageObj.CursorAfter is None and pageObj.CursorBefore is None):
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of items ...\n')
                    pageObj = spotify.GetPlayerRecentTracks(after=pageObj.CursorAfter, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlayerRecentTracks_Past24Hours(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlayerRecentTracks_Past24Hours"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get all tracks played within the past 1 hour.
            #afterMS:int = GetUnixTimestampMSFromUtcNow(hours=-1)     # last 1 hour
            #afterMS:int = GetUnixTimestampMSFromUtcNow(hours=-24)   # last 24 hours
            #afterMS:int = GetUnixTimestampMSFromUtcNow(days=-7)     # last 7 days

            # get tracks from current user's recently played tracks.
            print('\nGetting recently played tracks for current user ...\n')
            pageObj:PlayHistoryPage = spotify.GetPlayerRecentTracks()

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results - Tracks %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('')
                print('Tracks in this page of results:')
                
                # display history details.
                history:PlayHistory
                for history in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'Track: %s %s - "%s" (%s)' % (history.PlayedAt, history.PlayedAtMS, history.Track.Name, history.Track.Uri), history.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- {played_at} {played_atMS}: "{name}" ({uri})'.format(played_at=history.PlayedAt, played_atMS=history.PlayedAtMS, name=history.Track.Name, uri=history.Track.Uri))

                # anymore page results?
                if (pageObj.Next is None) \
                or (pageObj.IsCursor and pageObj.CursorAfter is None and pageObj.CursorBefore is None):
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of items ...\n')
                    pageObj = spotify.GetPlayerRecentTracks(after=pageObj.CursorAfter, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetSpotifyConnectDevice_BOSE01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetSpotifyConnectDevice_BOSE01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            
            # get information about a specified Spotify Connect player device.
            deviceId:str = 'bose-st10-1'
            print('\nGetting Spotify Connect device: \n- ID = "%s" ...\n' % deviceId)
            device:SpotifyConnectDevice = spotify.GetSpotifyConnectDevice(deviceId, activateDevice=True, refreshDeviceList=True, delay=0)

            # log device summary.
            _logsi.LogDictionary(SILevel.Message, 'Spotify Connect Device: "%s" (%s) (Dictionary)' % (device.Name, device.Id), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (object)' % (device.Name, device.Id), device, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DeviceInfo)' % (device.Name, device.Id), device.DeviceInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DiscoveryResult)' % (device.Name, device.Id), device.DiscoveryResult, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (ZeroconfResponseInfo)' % (device.Name, device.Id), device.ZeroconfResponseInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(device))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetSpotifyConnectDevice_BOSE02(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetSpotifyConnectDevice_BOSE02"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            
            # get information about a specified Spotify Connect player device.
            deviceId:str = 'bose-st10-2' # '30fbc80e35598f3c242f2120413c943dfd9715fe'
            print('\nGetting Spotify Connect device: \n- ID = "%s" ...\n' % deviceId)
            device:SpotifyConnectDevice = spotify.GetSpotifyConnectDevice(deviceId, activateDevice=True, refreshDeviceList=True, delay=0)

            # log device summary.
            _logsi.LogDictionary(SILevel.Message, 'Spotify Connect Device: "%s" (%s) (Dictionary)' % (device.Name, device.Id), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (object)' % (device.Name, device.Id), device, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DeviceInfo)' % (device.Name, device.Id), device.DeviceInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DiscoveryResult)' % (device.Name, device.Id), device.DiscoveryResult, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (ZeroconfResponseInfo)' % (device.Name, device.Id), device.ZeroconfResponseInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(device))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetSpotifyConnectDevice_NEST01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetSpotifyConnectDevice_NEST01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            
            # get information about a specified Spotify Connect player device.
            deviceId:str = 'Nest Audio 01'
            print('\nGetting Spotify Connect device: \n- ID = "%s" ...\n' % deviceId)
            device:SpotifyConnectDevice = spotify.GetSpotifyConnectDevice(deviceId, activateDevice=False)

            # log device summary.
            _logsi.LogDictionary(SILevel.Message, 'Spotify Connect Device: "%s" (%s) (Dictionary)' % (device.Name, device.Id), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (object)' % (device.Name, device.Id), device, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DeviceInfo)' % (device.Name, device.Id), device.DeviceInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DiscoveryResult)' % (device.Name, device.Id), device.DiscoveryResult, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (ZeroconfResponseInfo)' % (device.Name, device.Id), device.ZeroconfResponseInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(device))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetSpotifyConnectDevice_SONOS01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetSpotifyConnectDevice_SONOS01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            
            # get information about a specified Spotify Connect player device.
            deviceId:str = 'Office'
            print('\nGetting Spotify Connect device: \n- ID = "%s" ...\n' % deviceId)
            device:SpotifyConnectDevice = spotify.GetSpotifyConnectDevice(deviceId, activateDevice=True)

            # log device summary.
            _logsi.LogDictionary(SILevel.Message, 'Spotify Connect Device: "%s" (%s) (Dictionary)' % (device.Name, device.Id), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (object)' % (device.Name, device.Id), device, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DeviceInfo)' % (device.Name, device.Id), device.DeviceInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DiscoveryResult)' % (device.Name, device.Id), device.DiscoveryResult, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (ZeroconfResponseInfo)' % (device.Name, device.Id), device.ZeroconfResponseInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(device))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetSpotifyConnectDevice_SONOS01_Free(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetSpotifyConnectDevice_SONOS01_Free"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_FREE()
            
            # get information about a specified Spotify Connect player device.
            deviceId:str = 'Office'
            print('\nGetting Spotify Connect device: \n- ID = "%s" ...\n' % deviceId)
            device:SpotifyConnectDevice = spotify.GetSpotifyConnectDevice(deviceId, activateDevice=True)

            # log device summary.
            _logsi.LogDictionary(SILevel.Message, 'Spotify Connect Device: "%s" (%s) (Dictionary)' % (device.Name, device.Id), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (object)' % (device.Name, device.Id), device, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DeviceInfo)' % (device.Name, device.Id), device.DeviceInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DiscoveryResult)' % (device.Name, device.Id), device.DiscoveryResult, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (ZeroconfResponseInfo)' % (device.Name, device.Id), device.ZeroconfResponseInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(device))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetSpotifyConnectDevice_SPOTIFYD_LIBRESPOT(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetSpotifyConnectDevice_SPOTIFYD_LIBRESPOT"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            
            # get information about a specified Spotify Connect player device.
            deviceId:str = 'spotifyd-Debian-Linux'
            print('\nGetting Spotify Connect device: \n- ID = "%s" ...\n' % deviceId)
            device:SpotifyConnectDevice = spotify.GetSpotifyConnectDevice(deviceId, activateDevice=True)

            # log device summary.
            _logsi.LogDictionary(SILevel.Message, 'Spotify Connect Device: "%s" (%s) (Dictionary)' % (device.Name, device.Id), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (object)' % (device.Name, device.Id), device, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DeviceInfo)' % (device.Name, device.Id), device.DeviceInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DiscoveryResult)' % (device.Name, device.Id), device.DiscoveryResult, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (ZeroconfResponseInfo)' % (device.Name, device.Id), device.ZeroconfResponseInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(device))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetSpotifyConnectDevice_SCADDON_LIBRESPOT(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetSpotifyConnectDevice_SCADDON_LIBRESPOT"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            
            # get information about a specified Spotify Connect player device.
            deviceId:str = 'HAVM-SpotifyConnect'
            print('\nGetting Spotify Connect device: \n- ID = "%s" ...\n' % deviceId)
            device:SpotifyConnectDevice = spotify.GetSpotifyConnectDevice(deviceId, activateDevice=True)

            # log device summary.
            _logsi.LogDictionary(SILevel.Message, 'Spotify Connect Device: "%s" (%s) (Dictionary)' % (device.Name, device.Id), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (object)' % (device.Name, device.Id), device, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DeviceInfo)' % (device.Name, device.Id), device.DeviceInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DiscoveryResult)' % (device.Name, device.Id), device.DiscoveryResult, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (ZeroconfResponseInfo)' % (device.Name, device.Id), device.ZeroconfResponseInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(device))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetSpotifyConnectDevice_SPOTIFYD_LIBRESPOT(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetSpotifyConnectDevice_SPOTIFYD_LIBRESPOT"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            
            # get information about a specified Spotify Connect player device.
            deviceId:str = 'spotifyd-Debian-Linux'
            print('\nGetting Spotify Connect device: \n- ID = "%s" ...\n' % deviceId)
            device:SpotifyConnectDevice = spotify.GetSpotifyConnectDevice(deviceId, activateDevice=True)

            # log device summary.
            _logsi.LogDictionary(SILevel.Message, 'Spotify Connect Device: "%s" (%s) (Dictionary)' % (device.Name, device.Id), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (object)' % (device.Name, device.Id), device, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DeviceInfo)' % (device.Name, device.Id), device.DeviceInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (DiscoveryResult)' % (device.Name, device.Id), device.DiscoveryResult, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogObject(SILevel.Message,'Spotify Connect Device: "%s" (%s) (ZeroconfResponseInfo)' % (device.Name, device.Id), device.ZeroconfResponseInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(device))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetSpotifyConnectDevices(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetSpotifyConnectDevices"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get information about all available Spotify Connect player devices.
            print('\nRetrieving Spotify Connect player devices')
            result:SpotifyConnectDevices = spotify.GetSpotifyConnectDevices()

            _logsi.LogDictionary(SILevel.Message, 'Spotify Connect Device Info (Dictionary)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            
            # log device summary.
            print('\nDevice Summary: (%d items, refreshed on %f)' % (result.ItemsCount, result.DateLastRefreshed))
            device:Device
            for device in result.GetDeviceList():
                print('- "%s"' % device.SelectItemNameAndId)
                print(' SelectItemNameAndId = "%s"' % device.SelectItemNameAndId)
                print(' GetIdFromSelectItem = "%s"' % Device.GetIdFromSelectItem(device.SelectItemNameAndId))
                print(' GetNameFromSelectItem = "%s"' % Device.GetNameFromSelectItem(device.SelectItemNameAndId))
    
            # log device details.
            print('\nDevice Details: (%d items, refreshed on %f)\n' % (result.ItemsCount, result.DateLastRefreshed))
            device:SpotifyConnectDevice
            for device in result:
                
                _logsi.LogObject(SILevel.Message,'Device: %s' % (device.Title), device.DeviceInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'Device: %s (Dictionary)' % (device.Title), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(device))
                print('')

            # get cached configuration, refreshing from device if needed.
            result:SpotifyConnectDevices = spotify.GetSpotifyConnectDevices(refresh=False)    
            print("\nCached configuration (count): %d" % result.ItemsCount)

            # get cached configuration directly from the configuration manager dictionary.
            if "GetPlayerDevices" in spotify.ConfigurationCache:
                result:SpotifyConnectDevices = spotify.ConfigurationCache["GetSpotifyConnectDevices"]
                print("\nCached configuration direct access (count): %d" % result.ItemsCount)

            # compare devices for equality.
            if (result.Items[0].Equals(result.Items[0])):
                print("\nDevice \"%s\" equals Device \"%s\"" % (result.Items[0].Name, result.Items[0].Name))
            if (not result.Items[0].Equals(result.Items[1])):
                print("\nDevice \"%s\" does not equal Device \"%s\"" % (result.Items[0].Name, result.Items[1].Name))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise

        finally:

            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)
        

    def test_GetSpotifyConnectDevices_FREE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetSpotifyConnectDevices_FREE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_FREE()

            # get information about all available Spotify Connect player devices.
            print('\nRetrieving Spotify Connect player devices')
            result:SpotifyConnectDevices = spotify.GetSpotifyConnectDevices()

            _logsi.LogDictionary(SILevel.Message, 'Spotify Connect Device Info (Dictionary)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            
            # log device summary.
            print('\nDevice Summary: (%d items, refreshed on %f)' % (result.ItemsCount, result.DateLastRefreshed))
            device:Device
            for device in result.GetDeviceList():
                print('- "%s"' % device.SelectItemNameAndId)
                print(' SelectItemNameAndId = "%s"' % device.SelectItemNameAndId)
                print(' GetIdFromSelectItem = "%s"' % Device.GetIdFromSelectItem(device.SelectItemNameAndId))
                print(' GetNameFromSelectItem = "%s"' % Device.GetNameFromSelectItem(device.SelectItemNameAndId))
    
            # log device details.
            print('\nDevice Details: (%d items, refreshed on %f)\n' % (result.ItemsCount, result.DateLastRefreshed))
            device:SpotifyConnectDevice
            for device in result:
                
                _logsi.LogObject(SILevel.Message,'Device: %s' % (device.Title), device.DeviceInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'Device: %s (Dictionary)' % (device.Title), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(device))
                print('')

            # get cached configuration, refreshing from device if needed.
            result:SpotifyConnectDevices = spotify.GetSpotifyConnectDevices(refresh=False)    
            print("\nCached configuration (count): %d" % result.ItemsCount)

            # get cached configuration directly from the configuration manager dictionary.
            if "GetPlayerDevices" in spotify.ConfigurationCache:
                result:SpotifyConnectDevices = spotify.ConfigurationCache["GetSpotifyConnectDevices"]
                print("\nCached configuration direct access (count): %d" % result.ItemsCount)

            # compare devices for equality.
            if (result.Items[0].Equals(result.Items[0])):
                print("\nDevice \"%s\" equals Device \"%s\"" % (result.Items[0].Name, result.Items[0].Name))
            if (not result.Items[0].Equals(result.Items[1])):
                print("\nDevice \"%s\" does not equal Device \"%s\"" % (result.Items[0].Name, result.Items[1].Name))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise

        finally:

            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)
        

    def test_GetSpotifyConnectDevices_NoUserName(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetSpotifyConnectDevices_NoUserName"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()
            
            # get information about all available Spotify Connect player devices.
            print('\nRetrieving Spotify Connect player devices')
            result:SpotifyConnectDevices = spotify.GetSpotifyConnectDevices()

            _logsi.LogDictionary(SILevel.Message, 'Spotify Connect Device Info (Dictionary)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            
            # log device summary.
            print('\nDevice Summary: (%d items, refreshed on %f)' % (result.ItemsCount, result.DateLastRefreshed))
            device:Device
            for device in result.GetDeviceList():
                print('- "%s"' % device.SelectItemNameAndId)
                print(' SelectItemNameAndId = "%s"' % device.SelectItemNameAndId)
                print(' GetIdFromSelectItem = "%s"' % Device.GetIdFromSelectItem(device.SelectItemNameAndId))
                print(' GetNameFromSelectItem = "%s"' % Device.GetNameFromSelectItem(device.SelectItemNameAndId))
    
            # log device details.
            print('\nDevice Details: (%d items, refreshed on %f)\n' % (result.ItemsCount, result.DateLastRefreshed))
            device:SpotifyConnectDevice
            for device in result:
                
                _logsi.LogObject(SILevel.Message,'Device: %s' % (device.Title), device.DeviceInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'Device: %s (Dictionary)' % (device.Title), device.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(device))
                print('')

            # get cached configuration, refreshing from device if needed.
            result:SpotifyConnectDevices = spotify.GetSpotifyConnectDevices(refresh=False)    
            print("\nCached configuration (count): %d" % result.ItemsCount)

            # get cached configuration directly from the configuration manager dictionary.
            if "GetPlayerDevices" in spotify.ConfigurationCache:
                result:SpotifyConnectDevices = spotify.ConfigurationCache["GetSpotifyConnectDevices"]
                print("\nCached configuration direct access (count): %d" % result.ItemsCount)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerConvertDeviceNameToId(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerConvertDeviceNameToId"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get device id for specified device name.
            deviceName:str = 'Web Player (Chrome)'
            print('\nGetting Spotify Connect Player device id for name:\n- Name: %s ...' % (deviceName))
            deviceId:str = spotify.PlayerConvertDeviceNameToId(deviceName, True)
            _logsi.LogMessage('Device name "%s" ID = %s' % (deviceName, deviceId), colorValue=SIColors.LightGreen)
            print('- ID:   %s' % (deviceId))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_PlayerMediaPause(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPause"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Google Home 01" # Chromecast device
            #deviceId:str = "Google Group 01" # Chromecast device
            #deviceId:str = "Google Group 02" # Chromecast device
            deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Nest Group 01" # Chromecast device
            #deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # pause play on the specified Spotify Connect device.
            print('\nPause media on Spotify Connect device:\n- "%s" ...' % str(deviceId))
            spotify.PlayerMediaPause(deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media was paused', colorValue=SIColors.LightGreen)
            print('\nSuccess - media was paused')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPause_FREE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPause_FREE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_FREE()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Google Home 01" # Chromecast device
            #deviceId:str = "Google Group 01" # Chromecast device
            #deviceId:str = "Google Group 02" # Chromecast device
            deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Nest Group 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # pause play on the specified Spotify Connect device.
            print('\nPause media on Spotify Connect device:\n- "%s" ...' % str(deviceId))
            spotify.PlayerMediaPause(deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media was paused', colorValue=SIColors.LightGreen)
            print('\nSuccess - media was paused')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Album(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Album"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Google Home 01" # Chromecast device
            #deviceId:str = "Google Group 01" # Chromecast device
            #deviceId:str = "Google Group 02" # Chromecast device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Nest Group 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play album on the specified Spotify Connect device.
            contextUri:str = 'spotify:album:6vc9OTcyd3hyzabCmsdnwE'  # Album = Welcome to the New
            print('\nPlaying album on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - album should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - album should be playing')

            # play album starting at track #7 on the specified Spotify Connect device.
            contextUri:str = 'spotify:album:6vc9OTcyd3hyzabCmsdnwE'  # Album = Welcome to the New
            print('\nPlaying album starting at track #7 on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, offsetPosition=6, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - album should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - album should be playing')

            # play album starting at track #5 and 25 seconds position on the specified Spotify Connect device.
            contextUri:str = 'spotify:album:6vc9OTcyd3hyzabCmsdnwE'  # Album = Welcome to the New
            print('\nPlaying album starting at track #5 (25 seconds) on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, offsetPosition=4, positionMS=25000, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - album should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - album should be playing')

            # play album starting at track id #7 on the specified Spotify Connect device.
            contextUri:str = 'spotify:album:6vc9OTcyd3hyzabCmsdnwE'  # Album = Welcome to the New
            offsetUri:str = 'spotify:track:1kWUud3vY5ij5r62zxpTRy'   # Track = Flawless
            print('\nPlaying album starting at track #7 on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, offsetUri=offsetUri, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - album should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - album should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Album_DEFAULTID(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Album_DEFAULTID"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Nest Audio 01"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Google Home 01" # Chromecast device
            #deviceId:str = "Google Group 01" # Chromecast device
            #deviceId:str = "Google Group 02" # Chromecast device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Nest Group 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            deviceId:str = None            # use currently playing device

            # play album on the specified Spotify Connect device.
            contextUri:str = 'spotify:album:6vc9OTcyd3hyzabCmsdnwE'  # Album = Welcome to the New
            print('\nPlaying album on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - album should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - album should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Album_SHUFFLE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Album_SHUFFLE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-1"   # Bose SoundTouch device
            deviceId:str = "Echo Dot 01"   # Amazon Echo Dot device
            #deviceId:str = "Google Home 01" # Chromecast device
            #deviceId:str = "Google Group 01" # Chromecast device
            #deviceId:str = "Google Group 02" # Chromecast device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Nest Group 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play album on the specified Spotify Connect device.
            contextUri:str = 'spotify:album:6vc9OTcyd3hyzabCmsdnwE'  # Album = Welcome to the New
            print('\nPlaying album on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId, shuffle=None)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - album should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - album should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Artist(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Artist"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play artist on the specified Spotify Connect device.
            contextUri:str = 'spotify:artist:6g10GEtmIVqIQBhPZh4ScQ'  # Artist = Zach Williams
            print('\nPlaying artist on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - artist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - artist should be playing')

            # play artist and start first song played at the 25 seconds position on the specified Spotify Connect device.
            contextUri:str = 'spotify:artist:6g10GEtmIVqIQBhPZh4ScQ'  # Artist = Zach Williams
            print('\nPlaying artist at the 25 seconds position on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, positionMS=25000, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - artist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - artist should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Artist_SHUFFLE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Artist_SHUFFLE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-1"   # Bose SoundTouch device
            deviceId:str = "Echo Dot 01"   # Amazon Echo Dot device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play artist on the specified Spotify Connect device.
            contextUri:str = 'spotify:artist:6g10GEtmIVqIQBhPZh4ScQ'  # Artist = Zach Williams
            print('\nPlaying artist on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId, shuffle=True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - artist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - artist should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Audiobook(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Audiobook"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play audiobook on the specified Spotify Connect device.
            contextUri:str = 'spotify:show:74aydHJKgYz3AIq3jjBSv1'  # Audiobook = The Elfstones of Shannara
            print('\nPlaying audiobook on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - audiobook should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - audiobook should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Playlist(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Playlist"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-1"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play playlist on the specified Spotify Connect device.
            contextUri:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'  # Playlist = My Playlist
            print('\nPlaying playlist on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - playlist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist should be playing')

            # play playlist starting at track #7 on the specified Spotify Connect device.
            contextUri:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'  # Playlist = My Playlist
            print('\nPlaying playlist starting at track #7 on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, offsetPosition=6, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - playlist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist should be playing')

            # play playlist starting at track #5 and 25 seconds position on the specified Spotify Connect device.
            contextUri:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'  # Playlist = My Playlist
            print('\nPlaying playlist starting at track #5 (25 seconds) on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, offsetPosition=4, positionMS=25000, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - playlist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist should be playing')

            # play playlist starting at track id #7 on the specified Spotify Connect device.
            # note that this will not work on a Sonos device, as it does not understand "offsetUri" values!
            contextUri:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'  # Playlist = My Playlist
            offsetUri:str = 'spotify:track:1kWUud3vY5ij5r62zxpTRy'      # Track = Flawless
            print('\nPlaying playlist starting at track #7 on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, offsetUri=offsetUri, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - playlist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Playlist_SHUFFLE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Playlist_SHUFFLE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-2"
            
            # set device to control.
            deviceId:str = "HAVM-SpotifyConnect"    # SpotifyConnect AddOn (librespot)
            #deviceId:str = "Bose-ST10-2"           # Bose SoundTouch device
            #deviceId:str = "Echo Dot 01"           # Amazon Echo Dot device
            #deviceId:str = "Nest Audio 01"         # Chromecast device
            #deviceId:str = "Sonos 01"              # Sonos device
            #deviceId:str = "*"                     # use DefaultDeviceId
            #deviceId:str = None                    # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play playlist on the specified Spotify Connect device.
            #contextUri:str = 'spotify:playlist:37i9dQZF1E39vTG3GurFPW'  # Playlist = Daily Mix 01
            #contextUri:str = 'spotify:playlist:2El5V8a3DojPAww7VrdPaz'  # Playlist = My New Playlist 99
            #contextUri:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'  # Playlist = Worship Playlist
            contextUri:str = 'spotify:playlist:1XhVM7jWPrGLTiNiAy97Za'  # Playlist = LARGE playlist (5,000+ items)
            print('\nPlaying playlist on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId, shuffle=True, offsetPosition=0)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - playlist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_DisconnectedDevice(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Album"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # disconnect Spotify Connect player device.
            zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.81', 8200, '/zc', useSSL=False, tokenStorageDir=spotify.TokenStorageDir)
            result:ZeroconfResponse = zconn.Disconnect()            
            deviceName:str = 'Bose-ST10-1'

            # play playlist on the specified Spotify Connect device.
            contextUri:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'  # Playlist = My Playlist
            print('\nPlaying playlist on Spotify Connect device: \nName: %s \n- %s' % (deviceName, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceName)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - playlist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Playlist_DEVICEID(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Album"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play playlist on the specified Spotify Connect device.
            deviceId:str = '30fbc80e35598f3c242f2120413c943dfd9715fe'   # use specific device
            contextUri:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'  # Playlist = My Playlist
            print('\nPlaying playlist on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - playlist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Playlist_DEFAULTID(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Playlist_DEFAULTID"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Nest Audio 01"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            deviceId:str = None            # use currently playing device

            # get player state.
            #playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            #_logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play playlist on the specified Spotify Connect device.
            contextUri:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'  # Playlist = My Playlist
            print('\nPlaying playlist on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - playlist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Playlist_NEST01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Playlist_NEST01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            
            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play playlist on the specified Spotify Connect device.
            contextUri:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'  # Playlist = Worship
            print('\nPlaying playlist on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId, shuffle=True) #, resolveDeviceId=False)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - playlist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Playlist_HAVMSPOTIFYCONNECT(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Playlist_HAVMSPOTIFYCONNECT"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            
            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "HAVM-SpotifyConnect"    # SpotifyConnect AddOn (librespot)
            #deviceId:str = "Bose-ST10-2"           # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01"         # Chromecast device
            #deviceId:str = "Sonos 01"              # Sonos device
            #deviceId:str = "*"                     # use DefaultDeviceId
            #deviceId:str = None                    # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play playlist on the specified Spotify Connect device.
            contextUri:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'  # Playlist = Worship
            print('\nPlaying playlist on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId, shuffle=True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - playlist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Playlist_SONOS01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Playlist_SONOS01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            
            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play playlist on the specified Spotify Connect device.
            contextUri:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'  # Playlist = Worship
            print('\nPlaying playlist on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId, shuffle=None)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - playlist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayContext_Playlist_SpotifyDJ(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayContext_Playlist_SpotifyDJ"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            
            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # *** Spotify Web API does not currently support Spotify DJ playlist!
            # The following error is returned (as of 2024/06/07):
            
            # SAM1001E - Spotify Web API returned an error status while processing the "PlayerMediaPlayContext" method.
            # Status: 403 - Forbidden
            # Message: "Player command failed: Restriction violated"

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play playlist on the specified Spotify Connect device.
            contextUri:str = 'spotify:playlist:37i9dQZF1EYkqdzj48dyYq'  # Playlist = Spotify DJ AI
            print('\nPlaying playlist on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
            spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - playlist should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTrackFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTrackFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play all track favorites on the specified Spotify Connect device.
            print('\nPlaying track favorites on Spotify Connect device: \nID: %s' % deviceId)
            spotify.PlayerMediaPlayTrackFavorites(deviceId, False, limitTotal=100)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTrackFavorites_BOSE02(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTrackFavorites_BOSE02"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play all track favorites on the specified Spotify Connect device.
            print('\nPlaying track favorites on Spotify Connect device: \nID: %s' % deviceId)
            spotify.PlayerMediaPlayTrackFavorites(deviceId, False, limitTotal=10)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTrackFavorites_GOOGLEGROUP02(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTrackFavorites_GOOGLEGROUP02"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Google Group 02"
            
            # set device to control.
            deviceId:str = "Google Group 02"  # Chromecast Group device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play all track favorites on the specified Spotify Connect device.
            print('\nPlaying track favorites on Spotify Connect device: \nID: %s' % deviceId)
            spotify.PlayerMediaPlayTrackFavorites(deviceId, False, limitTotal=10)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTrackFavorites_GOOGLEHOME01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTrackFavorites_GOOGLEHOME01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Google Home 01"
            
            # set device to control.
            deviceId:str = "Google Home 01"   # Chromecast device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play all track favorites on the specified Spotify Connect device.
            print('\nPlaying track favorites on Spotify Connect device: \nID: %s' % deviceId)
            spotify.PlayerMediaPlayTrackFavorites(deviceId, False, limitTotal=10)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTrackFavorites_SONOS01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTrackFavorites_SONOS01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play all track favorites on the specified Spotify Connect device.
            print('\nPlaying track favorites on Spotify Connect device: \nID: %s' % deviceId)
            spotify.PlayerMediaPlayTrackFavorites(deviceId, False, limitTotal=10)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTrackFavorites_SHUFFLE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTrackFavorites_SHUFFLE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-2"
            
            # set device to control.
            deviceId:str = "HAVM-SpotifyConnect"    # SpotifyConnect AddOn (librespot)
            #deviceId:str = "Bose-ST10-2"           # Bose SoundTouch device
            #deviceId:str = "Echo Dot 01"           # Amazon Echo Dot device
            #deviceId:str = "Nest Audio 01"         # Chromecast device
            #deviceId:str = "Sonos 01"              # Sonos device
            #deviceId:str = "*"                     # use DefaultDeviceId
            #deviceId:str = None                    # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play all track favorites on the specified Spotify Connect device.
            print('\nPlaying track favorites on Spotify Connect device: \nID: %s' % deviceId)
            spotify.PlayerMediaPlayTrackFavorites(deviceId, shuffle=True, limitTotal=10)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTrackFavorites_ARTIST(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTrackFavorites_ARTIST"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM_NoDiscovery()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play all track favorites on the specified Spotify Connect device.
            print('\nPlaying track favorites on Spotify Connect device: \nID: %s' % deviceId)
            spotify.PlayerMediaPlayTrackFavorites(deviceId, False, limitTotal=1000, filterArtist="spotify:artist:5wpEBloInversG3zp3CVAk")  # Jeremy Camp
            #spotify.PlayerMediaPlayTrackFavorites(deviceId, False, limitTotal=1000, filterAlbum="spotify:album:3gSR4A397QFdzyvO2qihm3") # The Story's Not Over
            #spotify.PlayerMediaPlayTrackFavorites(deviceId, False, limitTotal=1000, filterArtist="jeremy camp")
            #spotify.PlayerMediaPlayTrackFavorites(deviceId, False, limitTotal=1000, filterAlbum="carried me")
            #spotify.PlayerMediaPlayTrackFavorites(deviceId, False, limitTotal=1000, filterArtist="jeremy camp", filterAlbum="carried me")

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTracks(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTracks"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play single track on the specified Spotify Connect device.
            uris:str='spotify:track:1kWUud3vY5ij5r62zxpTRy'  # Flawless
            print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
            spotify.PlayerMediaPlayTracks(uris, 0, deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            # play single track on the specified Spotify Connect device.
            # start playing at the 25 seconds (25000 milliseconds) point in the track.
            uris:str='spotify:track:1kWUud3vY5ij5r62zxpTRy'  # Flawless
            print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
            spotify.PlayerMediaPlayTracks(uris, 25000, deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            # play multiple tracks on the specified Spotify Connect device.
            uris:str='spotify:track:1kWUud3vY5ij5r62zxpTRy,spotify:track:27JODWXo4VNa6s7HqDL9yQ,spotify:track:4iV5W9uYEdYUVa79Axb7Rh'
            print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
            spotify.PlayerMediaPlayTracks(uris, 0, deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play multiple tracks on the specified Spotify Connect device.
            uris:list[str]=['spotify:track:1kWUud3vY5ij5r62zxpTRy','spotify:track:27JODWXo4VNa6s7HqDL9yQ','spotify:track:4iV5W9uYEdYUVa79Axb7Rh']
            print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, str(uris)))
            spotify.PlayerMediaPlayTracks(uris, 0, deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTracks_01TRACKTEST(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTracks_01TRACKTEST"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-1"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play 1 track on the specified Spotify Connect device.
            uris:str='spotify:track:6ZRKMJ7x5WGHuyUjoZjNEu'
            print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
            spotify.PlayerMediaPlayTracks(uris, 0, deviceId)

            #  Queue: (5 items)
            # - track: "Blessed Be Your Name" (spotify:track:6ZRKMJ7x5WGHuyUjoZjNEu)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTracks_05TRACKTEST(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTracks_05TRACKTEST"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play 5 tracks on the specified Spotify Connect device.
            uris:str='spotify:track:2VAtZmI9nCB97Kdnn9tMIF, spotify:track:6ZRKMJ7x5WGHuyUjoZjNEu, spotify:track:1u21AFQtqUHHlqePHk3qUL, spotify:track:4Wea9K8KRTsrlfIks5yepP, spotify:track:3ji2WLLlpJmvvSOlAyqB6p'
            print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
            spotify.PlayerMediaPlayTracks(uris, 0, deviceId, shuffle=None)
            
            #  Queue: (5 items)
            # - track: "Leaning On The Everlasting Arms / 'Tis So Sweet To Trust In Jesus - Medley" (spotify:track:2VAtZmI9nCB97Kdnn9tMIF)
            # - track: "Blessed Be Your Name" (spotify:track:6ZRKMJ7x5WGHuyUjoZjNEu)
            # - track: "Out Of My Hands" (spotify:track:1u21AFQtqUHHlqePHk3qUL)
            # - track: "Good God Almighty" (spotify:track:4Wea9K8KRTsrlfIks5yepP)
            # - track: "That Was Then, This Is Now" (spotify:track:3ji2WLLlpJmvvSOlAyqB6p)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTracks_20TRACKTEST(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTracks_20TRACKTEST"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play 20 tracks on the specified Spotify Connect device.
            uris:str='spotify:track:2VAtZmI9nCB97Kdnn9tMIF, spotify:track:6ZRKMJ7x5WGHuyUjoZjNEu, spotify:track:1u21AFQtqUHHlqePHk3qUL, spotify:track:4Wea9K8KRTsrlfIks5yepP, spotify:track:3ji2WLLlpJmvvSOlAyqB6p, spotify:track:3wFt2cfgRnGarpybCiCHj2, spotify:track:6FVg2subR7uoD80BmTOsdR, spotify:track:3rmzOry93Q6CQuHKVyBTQm, spotify:track:1RGV3trL1O9FgIrv8FcjRU, spotify:track:1z5YtEopKg5pyjCM3BEsr5, spotify:track:5hWtMn99mB2ckaLubacTuZ, spotify:track:2ZicbtrMnz97j3WyFf4So4, spotify:track:6OC3n631AkgqbWrrQbN1yH, spotify:track:7aIvVeBrvC7K3hYbpRXRdZ, spotify:track:6Dkou08rjWrgGijVmoAVZp, spotify:track:68x16tb33FQdWyiOaZYteP, spotify:track:1FlPIUDSRIxrulONSUQRaN, spotify:track:7KT088cs0FVVQum6IyT0X9, spotify:track:43yFiQ18Nhnb2YJwk09f3a, spotify:track:15eJjGIuCDEtF6ph4Hd3eR'
            print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
            spotify.PlayerMediaPlayTracks(uris, 0, deviceId, shuffle=True)
            
            #  Queue: (20 items)
            # - track: "Leaning On The Everlasting Arms / 'Tis So Sweet To Trust In Jesus - Medley" (spotify:track:2VAtZmI9nCB97Kdnn9tMIF)
            # - track: "Blessed Be Your Name" (spotify:track:6ZRKMJ7x5WGHuyUjoZjNEu)
            # - track: "Out Of My Hands" (spotify:track:1u21AFQtqUHHlqePHk3qUL)
            # - track: "Good God Almighty" (spotify:track:4Wea9K8KRTsrlfIks5yepP)
            # - track: "That Was Then, This Is Now" (spotify:track:3ji2WLLlpJmvvSOlAyqB6p)
            # - track: "I Got You" (spotify:track:3wFt2cfgRnGarpybCiCHj2)
            # - track: "Word of God Speak" (spotify:track:6FVg2subR7uoD80BmTOsdR)
            # - track: "Made New" (spotify:track:3rmzOry93Q6CQuHKVyBTQm)
            # - track: "King" (spotify:track:1RGV3trL1O9FgIrv8FcjRU)
            # - track: "Dead Man Walking" (spotify:track:1z5YtEopKg5pyjCM3BEsr5)
            # - track: "Holding Me Up" (spotify:track:5hWtMn99mB2ckaLubacTuZ)
            # - track: "O, For A Thousand Tongues To Sing" (spotify:track:2ZicbtrMnz97j3WyFf4So4)
            # - track: "Thank God For Sunday Morning" (spotify:track:6OC3n631AkgqbWrrQbN1yH)
            # - track: "Shake" (spotify:track:7aIvVeBrvC7K3hYbpRXRdZ)
            # - track: "My Story" (spotify:track:6Dkou08rjWrgGijVmoAVZp)
            # - track: "There Is Power" (spotify:track:68x16tb33FQdWyiOaZYteP)
            # - track: "Keep Me In The Moment" (spotify:track:1FlPIUDSRIxrulONSUQRaN)
            # - track: "You Love Me Anyway" (spotify:track:7KT088cs0FVVQum6IyT0X9)
            # - track: "Giants Fall" (spotify:track:43yFiQ18Nhnb2YJwk09f3a)
            # - track: "One Day" (spotify:track:15eJjGIuCDEtF6ph4Hd3eR)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTracks_SHUFFLE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTracks_SHUFFLE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "HAVM-SpotifyConnect"    # SpotifyConnect AddOn (librespot)
            #deviceId:str = "Bose-ST10-2"           # Bose SoundTouch device
            #deviceId:str = "Echo Dot 01"           # Amazon Echo Dot device
            #deviceId:str = "Nest Audio 01"         # Chromecast device
            #deviceId:str = "Sonos 01"              # Sonos device
            #deviceId:str = "*"                     # use DefaultDeviceId
            #deviceId:str = None                    # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play 20 tracks on the specified Spotify Connect device.
            uris:str='spotify:track:2VAtZmI9nCB97Kdnn9tMIF, spotify:track:6ZRKMJ7x5WGHuyUjoZjNEu, spotify:track:1u21AFQtqUHHlqePHk3qUL, spotify:track:4Wea9K8KRTsrlfIks5yepP, spotify:track:3ji2WLLlpJmvvSOlAyqB6p, spotify:track:3wFt2cfgRnGarpybCiCHj2, spotify:track:6FVg2subR7uoD80BmTOsdR, spotify:track:3rmzOry93Q6CQuHKVyBTQm, spotify:track:1RGV3trL1O9FgIrv8FcjRU, spotify:track:1z5YtEopKg5pyjCM3BEsr5, spotify:track:5hWtMn99mB2ckaLubacTuZ, spotify:track:2ZicbtrMnz97j3WyFf4So4, spotify:track:6OC3n631AkgqbWrrQbN1yH, spotify:track:7aIvVeBrvC7K3hYbpRXRdZ, spotify:track:6Dkou08rjWrgGijVmoAVZp, spotify:track:68x16tb33FQdWyiOaZYteP, spotify:track:1FlPIUDSRIxrulONSUQRaN, spotify:track:7KT088cs0FVVQum6IyT0X9, spotify:track:43yFiQ18Nhnb2YJwk09f3a, spotify:track:15eJjGIuCDEtF6ph4Hd3eR'
            print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
            spotify.PlayerMediaPlayTracks(uris, 0, deviceId, shuffle=None)
            
            #  Queue: (20 items)
            # - track: "Leaning On The Everlasting Arms / 'Tis So Sweet To Trust In Jesus - Medley" (spotify:track:2VAtZmI9nCB97Kdnn9tMIF)
            # - track: "Blessed Be Your Name" (spotify:track:6ZRKMJ7x5WGHuyUjoZjNEu)
            # - track: "Out Of My Hands" (spotify:track:1u21AFQtqUHHlqePHk3qUL)
            # - track: "Good God Almighty" (spotify:track:4Wea9K8KRTsrlfIks5yepP)
            # - track: "That Was Then, This Is Now" (spotify:track:3ji2WLLlpJmvvSOlAyqB6p)
            # - track: "I Got You" (spotify:track:3wFt2cfgRnGarpybCiCHj2)
            # - track: "Word of God Speak" (spotify:track:6FVg2subR7uoD80BmTOsdR)
            # - track: "Made New" (spotify:track:3rmzOry93Q6CQuHKVyBTQm)
            # - track: "King" (spotify:track:1RGV3trL1O9FgIrv8FcjRU)
            # - track: "Dead Man Walking" (spotify:track:1z5YtEopKg5pyjCM3BEsr5)
            # - track: "Holding Me Up" (spotify:track:5hWtMn99mB2ckaLubacTuZ)
            # - track: "O, For A Thousand Tongues To Sing" (spotify:track:2ZicbtrMnz97j3WyFf4So4)
            # - track: "Thank God For Sunday Morning" (spotify:track:6OC3n631AkgqbWrrQbN1yH)
            # - track: "Shake" (spotify:track:7aIvVeBrvC7K3hYbpRXRdZ)
            # - track: "My Story" (spotify:track:6Dkou08rjWrgGijVmoAVZp)
            # - track: "There Is Power" (spotify:track:68x16tb33FQdWyiOaZYteP)
            # - track: "Keep Me In The Moment" (spotify:track:1FlPIUDSRIxrulONSUQRaN)
            # - track: "You Love Me Anyway" (spotify:track:7KT088cs0FVVQum6IyT0X9)
            # - track: "Giants Fall" (spotify:track:43yFiQ18Nhnb2YJwk09f3a)
            # - track: "One Day" (spotify:track:15eJjGIuCDEtF6ph4Hd3eR)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTracks_BOSE02(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTracks_BOSE02"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play single track on the specified Spotify Connect device.
            uris:str='spotify:track:1kWUud3vY5ij5r62zxpTRy'  # Flawless
            print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
            spotify.PlayerMediaPlayTracks(uris, 0, deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTracks_SONOS01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTracks_SONOS01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play single track on the specified Spotify Connect device.
            uris:str='spotify:track:1kWUud3vY5ij5r62zxpTRy'  # Flawless
            print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
            spotify.PlayerMediaPlayTracks(uris, 0, deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTracks_HAVMSPOTIFYCONNECT(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTracks_HAVMSPOTIFYCONNECT"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            deviceId:str = "HAVM-SpotifyConnect"   # SpotifyConnect AddOn (librespot)
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play 20 tracks on the specified Spotify Connect device.
            uris:str='spotify:track:2VAtZmI9nCB97Kdnn9tMIF, spotify:track:6ZRKMJ7x5WGHuyUjoZjNEu, spotify:track:1u21AFQtqUHHlqePHk3qUL, spotify:track:4Wea9K8KRTsrlfIks5yepP, spotify:track:3ji2WLLlpJmvvSOlAyqB6p, spotify:track:3wFt2cfgRnGarpybCiCHj2, spotify:track:6FVg2subR7uoD80BmTOsdR, spotify:track:3rmzOry93Q6CQuHKVyBTQm, spotify:track:1RGV3trL1O9FgIrv8FcjRU, spotify:track:1z5YtEopKg5pyjCM3BEsr5, spotify:track:5hWtMn99mB2ckaLubacTuZ, spotify:track:2ZicbtrMnz97j3WyFf4So4, spotify:track:6OC3n631AkgqbWrrQbN1yH, spotify:track:7aIvVeBrvC7K3hYbpRXRdZ, spotify:track:6Dkou08rjWrgGijVmoAVZp, spotify:track:68x16tb33FQdWyiOaZYteP, spotify:track:1FlPIUDSRIxrulONSUQRaN, spotify:track:7KT088cs0FVVQum6IyT0X9, spotify:track:43yFiQ18Nhnb2YJwk09f3a, spotify:track:15eJjGIuCDEtF6ph4Hd3eR'
            # play single track on the specified Spotify Connect device.
            #uris:str='spotify:track:1kWUud3vY5ij5r62zxpTRy'  # Flawless
            print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
            spotify.PlayerMediaPlayTracks(uris, 0, deviceId, shuffle=True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTracks_NEST01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTracks_NEST01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play single track on the specified Spotify Connect device.
            uris:str='spotify:track:1kWUud3vY5ij5r62zxpTRy'  # Flawless
            print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
            spotify.PlayerMediaPlayTracks(uris, 0, deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - media should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaPlayTracks_Episode(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaPlayTracks_Episode"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # play episode on the specified Spotify Connect device.
            uris:str = 'spotify:episode:3F97boSWlXi8OzuhWClZHQ'  # Audiobook = Wyatt and Kurt Russsell (Armchair Expert with Dax Sheppard)
            print('\nPlaying episode on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris))
            spotify.PlayerMediaPlayTracks(uris, deviceId=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - episode should be playing', colorValue=SIColors.LightGreen)
            print('\nSuccess - episode should be playing')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaResume(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaResume"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Google Home 01" # Chromecast device
            #deviceId:str = "Google Group 01" # Chromecast device
            #deviceId:str = "Google Group 02" # Chromecast device
            deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Nest Group 01" # Chromecast device
            #deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # resume play on the specified Spotify Connect device.
            print('\nResume media on Spotify Connect device:\n- "%s" ...' % str(deviceId))
            spotify.PlayerMediaResume(deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media was resumed', colorValue=SIColors.LightGreen)
            print('\nSuccess - media was resumed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaResume_BOSE02(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaResume_BOSE02"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # resume play on the specified Spotify Connect device.
            print('\nResume media on default Spotify Connect device ...')
            spotify.PlayerMediaResume(deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media was resumed', colorValue=SIColors.LightGreen)
            print('\nSuccess - media was resumed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaResume_ECHODOT01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaResume_ECHODOT01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            deviceId:str = "Echo Dot 01"   # Amazon Echo Dot device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # resume play on the specified Spotify Connect device.
            print('\nResume media on default Spotify Connect device ...')
            spotify.PlayerMediaResume(deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media was resumed', colorValue=SIColors.LightGreen)
            print('\nSuccess - media was resumed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaResume_NONE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaResume_NONE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = None
            
            # set device to control.
            #deviceId:str = "THLUCASI9"     # Desktop Player
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # resume play on the specified Spotify Connect device.
            print('\nResume media on default Spotify Connect device ...')
            spotify.PlayerMediaResume(deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media was resumed', colorValue=SIColors.LightGreen)
            print('\nSuccess - media was resumed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaResume_FREE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaResume_FREE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_FREE()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # resume play on the specified Spotify Connect device.
            print('\nResume media on Spotify Connect device:\n- "%s" ...' % str(deviceId))
            spotify.PlayerMediaResume(deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - media was resumed', colorValue=SIColors.LightGreen)
            print('\nSuccess - media was resumed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaSeek(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaSeek"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # seek to the given position on the specified Spotify Connect device.
            #positionMS:int = 0
            positionMS:int = 25000
            print('\nSeeking to %d milliseconds on Spotify Connect device:\n- "%s" ...' % (positionMS, deviceId))
            spotify.PlayerMediaSeek(positionMS, deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - seek to position in track', colorValue=SIColors.LightGreen)
            print('\nSuccess - seek to position in track')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaSeek_Relative(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaSeek_Relative"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # seek ahead 5 seconds in the playing track.
            positionMS:int = 5000
            print('\nSeeking ahead by %d milliseconds on Spotify Connect device:\n- "%s" ...' % (positionMS, deviceId))
            spotify.PlayerMediaSeek(deviceId=deviceId, relativePositionMS=positionMS)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # seek behind 5 seconds in the playing track.
            positionMS:int = -5000
            print('\nSeeking behind by %d milliseconds on Spotify Connect device:\n- "%s" ...' % (positionMS, deviceId))
            spotify.PlayerMediaSeek(deviceId=deviceId, relativePositionMS=positionMS)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - seek to position in track', colorValue=SIColors.LightGreen)
            print('\nSuccess - seek to position in track')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaSeek_Relative_SONOS(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaSeek_Relative_SONOS"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # seek ahead 5 seconds in the playing track.
            positionMS:int = 5000
            print('\nSeeking ahead by %d milliseconds on Spotify Connect device:\n- "%s" ...' % (positionMS, deviceId))
            spotify.PlayerMediaSeek(deviceId=deviceId, relativePositionMS=positionMS)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # seek behind 5 seconds in the playing track.
            positionMS:int = -5000
            print('\nSeeking behind by %d milliseconds on Spotify Connect device:\n- "%s" ...' % (positionMS, deviceId))
            spotify.PlayerMediaSeek(deviceId=deviceId, relativePositionMS=positionMS)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - seek to position in track', colorValue=SIColors.LightGreen)
            print('\nSuccess - seek to position in track')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaSeek_Relative_DEFAULT(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaSeek_Relative_DEFAULT"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # seek ahead 5 seconds in the playing track.
            positionMS:int = 5000
            print('\nSeeking ahead by %d milliseconds on Spotify Connect device:\n- "%s" ...' % (positionMS, deviceId))
            spotify.PlayerMediaSeek(deviceId=deviceId, relativePositionMS=positionMS)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # seek behind 5 seconds in the playing track.
            positionMS:int = -5000
            print('\nSeeking behind by %d milliseconds on Spotify Connect device:\n- "%s" ...' % (positionMS, deviceId))
            spotify.PlayerMediaSeek(deviceId=deviceId, relativePositionMS=positionMS)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - seek to position in track', colorValue=SIColors.LightGreen)
            print('\nSuccess - seek to position in track')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaSkipNext(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaSkipNext"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Google Home 01" # Chromecast device
            #deviceId:str = "Google Group 01" # Chromecast device
            #deviceId:str = "Google Group 02" # Chromecast device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Nest Group 01" # Chromecast device
            #deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # skip to next track on the specified Spotify Connect device.
            print('\nSkip to next track on Spotify Connect device:\n- "%s" ...' % str(deviceId))
            spotify.PlayerMediaSkipNext(deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - skipped to next track', colorValue=SIColors.LightGreen)
            print('\nSuccess - skipped to next track')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerMediaSkipPrevious(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerMediaSkipPrevious"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Google Home 01" # Chromecast device
            #deviceId:str = "Google Group 01" # Chromecast device
            #deviceId:str = "Google Group 02" # Chromecast device
            deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Nest Group 01" # Chromecast device
            #deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # skip to previous track on the specified Spotify Connect device.
            print('\nSkip to previous track on Spotify Connect device:\n- "%s" ...' % str(deviceId))
            spotify.PlayerMediaSkipPrevious(deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - skipped to previous track', colorValue=SIColors.LightGreen)
            print('\nSuccess - skipped to previous track')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerSetRepeatMode(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerSetRepeatMode"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # set repeat mode CONTEXT for the user's current playback device.
            print('\nSet repeat mode CONTEXT for Spotify Connect device:\n- "%s" ...' % (str(deviceId)))
            spotify.PlayerSetRepeatMode('context', deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - repeat mode CONTEXT was set', colorValue=SIColors.LightGreen)
            print('\nSuccess - repeat mode CONTEXT was set')

            # set repeat mode TRACK for the user's current playback device.
            print('\nSet repeat mode to single track for Spotify Connect device:\n- "%s" ...' % (str(deviceId)))
            spotify.PlayerSetRepeatMode('track', deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - repeat mode TRACK was set', colorValue=SIColors.LightGreen)
            print('\nSuccess - repeat mode TRACK was set')

            # set repeat mode OFF for the user's current playback device.
            print('\nSet repeat mode OFF for Spotify Connect device:\n- "%s" ...' % (str(deviceId)))
            spotify.PlayerSetRepeatMode('off', deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - repeat mode OFF was set', colorValue=SIColors.LightGreen)
            print('\nSuccess - repeat mode OFF was set')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerSetShuffleMode(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerSetShuffleMode"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # set shuffle mode ON for the user's current playback device.
            print('\nSet shuffle mode ON for Spotify Connect device:\n- "%s" ...' % (str(deviceId)))
            spotify.PlayerSetShuffleMode(True, deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - shuffle mode ON was set', colorValue=SIColors.LightGreen)
            print('\nSuccess - shuffle mode ON was set')

            # set shuffle mode OFF for the user's current playback device.
            print('\nSet shuffle mode OFF for Spotify Connect device:\n- "%s" ...' % (str(deviceId)))
            spotify.PlayerSetShuffleMode(False, deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - shuffle mode OFF was set', colorValue=SIColors.LightGreen)
            print('\nSuccess - shuffle mode OFF was set')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerSetVolume(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerSetVolume"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Google Home 01" # Chromecast device
            #deviceId:str = "Google Group 01" # Chromecast device
            #deviceId:str = "Google Group 02" # Chromecast device
            deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Nest Group 01" # Chromecast device
            #deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # set the volume for the user's current playback device.
            volumePercent:int = 10
            print('\nSet %d%% volume on Spotify Connect device:\n- "%s" ...' % (volumePercent, str(deviceId)))
            spotify.PlayerSetVolume(volumePercent, deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - volume was set', colorValue=SIColors.LightGreen)
            print('\nSuccess - volume was set')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerSetVolume_BYNAME(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerSetVolume"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # set the volume for the user's current playback device.
            volumePercent:int = 10
            deviceId:str = "Bose-ST10-1"   # use specific device name
            print('\nSet %d%% volume on Spotify Connect device:\n- "%s" ...' % (volumePercent, str(deviceId)))
            spotify.PlayerSetVolume(volumePercent, deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - volume was set', colorValue=SIColors.LightGreen)
            print('\nSuccess - volume was set')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            deviceName:str = 'Web Player (Chrome)'
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceName))
            spotify.PlayerTransferPlayback(deviceName, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            deviceName:str = 'Bose-ST10-1'
            deviceId:str = '30fbc80e35598f3c242f2120413c943dfd9715fe'
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s"\nID:   %s ...' % (deviceName, deviceId))
            spotify.PlayerTransferPlayback(deviceId, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_BYNAME(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_BYNAME"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            #deviceName:str = 'Web Player (Chrome)'
            deviceName:str = 'Todds iPhone'
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % deviceName)
            spotify.PlayerTransferPlayback(deviceName, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            deviceName:str = 'bOSE-ST10-1'
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % deviceName)
            spotify.PlayerTransferPlayback(deviceName, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_Device_DEFAULT(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_DEFAULT"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-1"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to DefaultDeviceId.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_Device_DEFAULTNONE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_DEFAULTNONE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            spotify.DefaultDeviceId = None
            
            # set device to control.
            #deviceId:str = "Bose-ST10-1"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to DefaultDeviceId.
            spotify.DefaultDeviceId = None
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_FromDevice(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_FromDevice"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # set device to control.
            # deviceIdFrom:str = 'Bose-ST10-1'
            # deviceId:str = 'Office' # Sonos device.

            # deviceIdFrom:str = 'Office' # Sonos device.
            # deviceId:str = 'Bose-ST10-1'

            deviceIdFrom:str = 'Office' # Sonos device.
            deviceId:str = 'Nest Audio 01'

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True, deviceIdFrom=deviceIdFrom)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_FromDevice_FREE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_FromDevice_FREE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_FREE()

            # set device to control.
            # deviceIdFrom:str = 'Bose-ST10-1'
            # deviceId:str = 'Office' # Sonos device.

            # deviceIdFrom:str = 'Office' # Sonos device.
            # deviceId:str = 'Bose-ST10-1'

            deviceIdFrom:str = 'Office' # Sonos device.
            deviceId:str = 'Nest Audio 01'

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True, deviceIdFrom=deviceIdFrom)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_Device_BOSE01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_BOSE01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-1"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_Device_BOSE02(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_BOSE02"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True, deviceIdFrom=deviceId)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_Device_BOSE300(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_BOSE300"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            deviceId:str = "Bose-ST300"    # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_Device_HAVMSPOTIFYCONNECT(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_HAVMSPOTIFYCONNECT"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            deviceName:str = 'HAVM-SpotifyConnect'
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceName))
            spotify.PlayerTransferPlayback(deviceName, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_Device_ECHODOT01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_ECHODOT01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "a44f6798-5b19-467f-9b74-d11b517fcebe_amzn_1"   # Amazon Echo Dot device
            deviceId:str = "Echo Dot 01"   # Amazon Echo Dot device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True, refreshDeviceList=False, forceActivateDevice=False)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise

        finally:
            
            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)


    def test_PlayerTransferPlayback_Device_NEST01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_NEST01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "bddc76176455911f8d908c701012a3de"  # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True, refreshDeviceList=False, forceActivateDevice=False)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise

        finally:
            
            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)


    def test_PlayerTransferPlayback_Device_NEST01_BYID(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_NEST01_BYID"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "bddc76176455911f8d908c701012a3de"  # Chromecast device
            #deviceId:str = "c687da317f7df7fc94b3bc90c28f6169e5b3fcb9"  # SpotifyConnect device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True, refreshDeviceList=False, forceActivateDevice=False)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise

        finally:
            
            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)


    def test_PlayerTransferPlayback_Device_NEST01_FREE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_NEST01_FREE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_FREE()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True, refreshDeviceList=False, forceActivateDevice=False)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise

        finally:
            
            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)


    def test_PlayerTransferPlayback_Device_SONOS01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_Sonos01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
        finally:

            # stop Spotify Connect Directory task.
            if (spotify is not None):
                spotify.StopSpotifyConnectDirectoryTask(5)


    def test_PlayerTransferPlayback_Device_SONOS01_FREE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_SONOS01_FREE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_FREE()

            # if no active spotify player device, then use the specified device.
            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            deviceId:str = "Sonos 01"        # Sonos device
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_Device_SPOTIFYD(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_SPOTIFYD"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            deviceName:str = 'spotifyd-Debian-Linux'
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceName))
            spotify.PlayerTransferPlayback(deviceName, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_Device_WEBCHROME(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_WEBCHROME"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            deviceId:str = "Web Player (Chrome)"
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_Device_IPHONE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_IPHONE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            #spotify.DefaultDeviceId = "Bose-ST10-1"
            
            # set device to control.
            #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
            #deviceId:str = "Nest Audio 01" # Chromecast device
            #deviceId:str = "Sonos 01"      # Sonos device
            deviceId:str = "iPhone"        # iPhone
            #deviceId:str = "*"             # use DefaultDeviceId
            #deviceId:str = None            # use currently playing device

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceId))
            spotify.PlayerTransferPlayback(deviceId, True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayerTransferPlayback_Device_MULTIPLE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayerTransferPlayback_Device_MULTIPLE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState before: %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            deviceName:str = 'Bose-ST10-1'
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceName))
            spotify.PlayerTransferPlayback(deviceName, True, refreshDeviceList=True)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            deviceName:str = 'Office'
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceName))
            spotify.PlayerTransferPlayback(deviceName, True, refreshDeviceList=False)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            deviceName:str = 'Nest Audio 01'
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceName))
            spotify.PlayerTransferPlayback(deviceName, True, refreshDeviceList=False)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            # transfer Spotify Connect playback control to another device.
            # the device name and id can be retrieved from `GetPlayerDevices` method.
            deviceName:str = 'Bose-ST10-2'
            print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % (deviceName))
            spotify.PlayerTransferPlayback(deviceName, True, refreshDeviceList=False)

            # get player state.
            playerState:PlayerPlayState = spotify.GetPlayerPlaybackState(additionalTypes='episode')
            _logsi.LogObject(SILevel.Message, 'PlayerPlayState after:  %s' % (playerState.Summary), playerState, colorValue=SIColors.LightGreen, excludeNonPublic=True)

            _logsi.LogMessage('Success - control was transferred', colorValue=SIColors.LightGreen)
            print('\nSuccess - control was transferred')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
