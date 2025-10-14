import sys
sys.path.append("..")

import unittest
from testVS_Sonos_Base import Test_Sonos_Base

# external package imports.
from smartinspectpython.siauto import *
from soco import SoCo
from soco.plugins.sharelink import ShareLinkPlugin

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# AVTransport Tests.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_Sonos_AVTransport(Test_Sonos_Base): 
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_Pause(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_Pause"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            sonosDevice:SoCo = self._CreateSonosDevice_SONOS01()
            
            # send command to Sonos device.
            print('\nSending PAUSE command to Sonos device')
            sonosDevice.pause()
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_Play(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_Play"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            sonosDevice:SoCo = self._CreateSonosDevice_SONOS01()
            
            # send command to Sonos device.
            print('\nSending PLAY command to Sonos device')
            sonosDevice.play()
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayContext_Spotify_Album(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayContext_Spotify_Album"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            sonosDevice:SoCo = self._CreateSonosDevice_SONOS01()
            
            # send command to Sonos device.
            contextUri:str = 'spotify:album:1ssGLn8MxlaOnOoB2c47yl'
            print('\nClearing Sonos Queue')
            sonosDevice.clear_queue()
            print('\nSending ADD_SHARE_LINK_TO_QUEUE command to Sonos device:\nSpotify URI: %s' % (contextUri))
            sharelink = ShareLinkPlugin(sonosDevice)
            result = sharelink.add_share_link_to_queue(contextUri, 1)
            print("\nResult: %s" % result)
            print('\nPlaying from queue index position 0')
            sonosDevice.play_from_queue(index=0)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayContext_Spotify_Artist(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayContext_Spotify_Artist"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            sonosDevice:SoCo = self._CreateSonosDevice_SONOS01()
            
            # send command to Sonos device.
            contextUri:str = 'spotify:artist:6pRi6EIPXz4QJEOEsBaA0m'
            #result:SearchResponse = self.data.spotifyClient.SearchAlbums(criteria=contextUri, limitTotal=20)
            print('\nClearing Sonos Queue')
            sonosDevice.clear_queue()
            print('\nSending ADD_SHARE_LINK_TO_QUEUE command to Sonos device:\nSpotify URI: %s' % (contextUri))
            sharelink = ShareLinkPlugin(sonosDevice)
            result = sharelink.add_share_link_to_queue(contextUri, 1)
            print("\nResult: %s" % result)
            print('\nPlaying from queue index position 0')
            sonosDevice.play_from_queue(index=0)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_PlayContext_Spotify_Playlist(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_PlayContext_Spotify_Playlist"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            sonosDevice:SoCo = self._CreateSonosDevice_SONOS01()
            
            # send command to Sonos device.
            contextUri:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'
            print('\nClearing Sonos Queue')
            sonosDevice.clear_queue()
            print('\nSending ADD_SHARE_LINK_TO_QUEUE command to Sonos device:\nSpotify URI: %s' % (contextUri))
            sharelink = ShareLinkPlugin(sonosDevice)
            result = sharelink.add_share_link_to_queue(contextUri, 1)
            print("\nResult: %s" % result)
            print('\nPlaying from queue index position 0')
            sonosDevice.play_from_queue(index=0)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetCurrentMediaInfo(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetCurrentMediaInfo"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            sonosDevice:SoCo = self._CreateSonosDevice_SONOS01()
            
            # send command to Sonos device.
            print('\nQuerying Current Media Info from Sonos device')
            info:dict = sonosDevice.get_current_media_info()
            _logsi.LogDictionary(SILevel.Verbose, "Sonos get_current_media_info Results", info, colorValue=SIColors.LightGreen, prettyPrint=True)
            print("\nResults: %s" % str(info))
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetCurrentTrackInfo(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetCurrentTrackInfo"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            sonosDevice:SoCo = self._CreateSonosDevice_SONOS01()
            
            # send command to Sonos device.
            print('\nQuerying Current Track Info from Sonos device')
            info:dict = sonosDevice.get_current_track_info()
            _logsi.LogDictionary(SILevel.Verbose, "Sonos get_current_track_info Results", info, colorValue=SIColors.LightGreen, prettyPrint=True)
            print("\nResults: %s" % str(info))
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetCurrentTransportInfo(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetCurrentTransportInfo"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            sonosDevice:SoCo = self._CreateSonosDevice_SONOS01()
            
            # send command to Sonos device.
            print('\nQuerying Current Transport Info from Sonos device')
            info:dict = sonosDevice.get_current_transport_info()
            _logsi.LogDictionary(SILevel.Verbose, "Sonos get_current_transport_info Results", info, colorValue=SIColors.LightGreen, prettyPrint=True)
            print("\nResults: %s" % str(info))
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetQueue(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetQueue"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            sonosDevice:SoCo = self._CreateSonosDevice_SONOS01()
            
            # send command to Sonos device.
            print('\nQuerying Queue Info from Sonos device')
            info:dict = sonosDevice.get_queue()
            _logsi.LogDictionary(SILevel.Verbose, "Sonos get_queue Results", info, colorValue=SIColors.LightGreen, prettyPrint=True)
            print("\nResults: %s" % str(info))
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
