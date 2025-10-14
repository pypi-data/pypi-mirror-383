import sys
sys.path.append("..")

import unittest
from testVS_Sonos_Base import Test_Sonos_Base
from testVS_Sonos_AvTransport import *

# external package imports.
from smartinspectpython.siauto import *
from soco import SoCo
from soco.data_structures import DidlItem, DidlResource
from soco.music_services import MusicService

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# MusicServices Spotify Tests.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_Sonos_MusicService_Spotify(Test_Sonos_Base): 
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    @staticmethod
    def add_from_service(item_id, service, device, is_track=True):


        # The DIDL item_id is made of the track_id (url escaped), but with an 8
        # (hex) digit prefix. It is not clear what this is for, but it doesn't
        # seem to matter (too much) what it is. We can use junk (thought the
        # first digit must be 0 or 1), and the player seems to do the right
        # thing. Real DIDL items sent to a player also have a title and a
        # parent_id (usually the id of the relevant album), but they are not
        # necessary. The flow charts at http://musicpartners.sonos.com/node/421
        # and http://musicpartners.sonos.com/node/422 suggest that it is the job
        # of the player, not the controller, to call get_metadata with a track
        # id, so this might explain why no metadata is needed at this stage.

        # NB: quote_url will break if given unicode on Py2.6, and early 2.7. So
        # we need to encode.


        #item_id = quote_url(item_id.encode('utf-8'))
        #item_id = item_id.encode('utf-8')
        didl_item_id = "0fffffff{0}".format(item_id)

        # For an album:
        if not is_track:
            uri = 'x-rincon-cpcontainer:' + didl_item_id

        else:
            # For a track:
            uri = service.sonos_uri_from_id(item_id)

        res = [DidlResource(uri=uri, protocol_info="DUMMY")]
        didl = DidlItem(title="DUMMY",
            # This is ignored. Sonos gets the title from the item_id
            parent_id="DUMMY",  # Ditto
            item_id=didl_item_id,
            desc=service.desc,
            resources=res)

        device.add_to_queue(didl)
    



    def test_AddUrisToQueue(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_AddUrisToQueue"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            device = SoCo("192.168.1.91")                       # <------ Your IP here
            service = MusicService("Spotify")                   # <------ Your Music Service here
            album_id = "spotify:album:5qo7iEWkMEaSXEZ7fuPvC3"   # <------ an album
            track_id = "spotify:track:2qs5ZcLByNTctJKbhAZ9JE"   # <------ a track

            # add queue item.
            print('\nAdding track id to queue')
            Test_Sonos_MusicService_Spotify.add_from_service(track_id, service, device, True)
            print('\nAdding album id to queue')
            Test_Sonos_MusicService_Spotify.add_from_service(album_id, service, device, False)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_getProperty_MusicSource(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_getProperty_MusicSource"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            sonosDevice:SoCo = self._CreateSonosDevice_SONOS01()
            
            # send command to Sonos device.
            print('\nRetrieving Sonos music_source')
            result:str = sonosDevice.music_source
            _logsi.LogString(SILevel.Verbose, "Sonos music_source", result, colorValue=SIColors.LightGreen)
            print("\nResults: %s" % result)
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_MusicSource_Spotify(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_MusicSource_Spotify"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            sonosDevice:SoCo = self._CreateSonosDevice_SONOS01()

            print('\nRetrieving Sonos music_source')
            result:str = sonosDevice.music_source
            _logsi.LogString(SILevel.Verbose, "Sonos music_source", result, colorValue=SIColors.LightGreen)
            print("\nResults: %s" % result)
            
            # send command to Sonos device.
            print('\nSending SETAVTRANSPORTURI command to Sonos device')
            #sonosDevice.music_source = 'SPOTIFY_CONNECT'
            #contextId:str = 'spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE'
            sonosDevice.avTransport.SetAVTransportURI(
                [
                    ("InstanceID", 0),
                    ("CurrentURI", "x-sonos-spotify:spotify%3atrack%3a17GmwQ9Q3MTAz05OokmNNB?sid=12&amp;flags=8232&amp;sn=2"),
                    #("CurrentURI", "x-sonos-vli:RINCON_38420B909DC801400:2,spotify:9e38417f1e06652389d96c30ce96b0eb"),
                    ("CurrentURIMetaData", ""),
                ]
            )
            #x-sonos-spotify:spotify%3atrack%3a17GmwQ9Q3MTAz05OokmNNB?sid=12&amp;flags=8232&amp;sn=2
            
            print('\nSending PAUSE command to Sonos device')
            sonosDevice.pause()
            
            print('\nRetrieving Sonos music_source')
            result:str = sonosDevice.music_source
            _logsi.LogString(SILevel.Verbose, "Sonos music_source", result, colorValue=SIColors.LightGreen)
            print("\nResults: %s" % result)

            print('\nSending PLAY command to Sonos device')
            sonosDevice.play()
            
            print('\nRetrieving Sonos music_source')
            result:str = sonosDevice.music_source
            _logsi.LogString(SILevel.Verbose, "Sonos music_source", result, colorValue=SIColors.LightGreen)
            print("\nResults: %s" % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
