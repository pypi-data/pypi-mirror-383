import sys
sys.path.append("..")

import unittest
from testVS_SpotifyClient_Base import Test_SpotifyClient_Base

# external package imports.
from smartinspectpython.siauto import *

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.models import *

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# SpotifyClient Tests - Tracks.
#
# Test Uri's:
# Uri="spotify:artist:6APm8EjxOHSYM5B4i3vT3q" - Artist="MercyMe"
# Uri="spotify:album:6vc9OTcyd3hyzabCmsdnwE"  - Artist="MercyMe", Album="Welcome to the New"
# Uri="spotify:track:1kWUud3vY5ij5r62zxpTRy"  - Artist="MercyMe", Album="Welcome to the New", Track="Flawless"
#
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Tracks(Test_SpotifyClient_Base):
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_CheckTrackFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckTrackFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # check if one or more tracks is already saved in the current Spotify user's 'Your Library'.
            trackIds:str = '1kWUud3vY5ij5r62zxpTRy,2takcwOaAZWiXQijPHIx7B,4eoYKv2kDwJS7gRGh5q6SK'
            print('\nChecking if tracks are saved by the current user: \n- %s' % trackIds.replace(',','\n- '))
            result:dict = spotify.CheckTrackFavorites(trackIds)
            
            _logsi.LogDictionary(SILevel.Message,'CheckTrackFavorites result', result, colorValue=SIColors.LightGreen)
            print('\nResults:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_CheckTrackFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckTrackFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # check if nowplaying track is saved in the current Spotify user's 'Your Library'.
            print('\nChecking if nowplaying track is saved by the current user ...')
            result:dict = spotify.CheckTrackFavorites()
            
            _logsi.LogDictionary(SILevel.Message,'CheckTrackFavorites result', result, colorValue=SIColors.LightGreen)
            print('\nResults:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTrackFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTrackFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the tracks saved in the current Spotify user's 'Your Library'.
            print('\nGetting saved tracks for current user ...\n')
            pageObj:TrackPageSaved = spotify.GetTrackFavorites()

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')
                _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetTracks(), colorValue=SIColors.LightGreen)
                print('Tracks in this page of results:')

                # display track details.
                trackSaved:TrackSaved
                for trackSaved in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'Track Object: "%s" (%s)' % (trackSaved.Track.Name, trackSaved.Track.Uri), trackSaved.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=trackSaved.Track.Name, uri=trackSaved.Track.Uri))

                    # use the following to display all object properties.
                    #print(str(trackSaved.Track))
                    #print('')
         
                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetTrackFavorites(offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTrackFavorites_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTrackFavorites_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the tracks saved in the current Spotify user's 'Your Library'.
            print('\nGetting ALL saved tracks for current user ...\n')
            pageObj:TrackPageSaved = spotify.GetTrackFavorites(limitTotal=1000)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetTracks(), colorValue=SIColors.LightGreen)
            print('\nTracks in this page of results (%d items):' % pageObj.ItemsCount)

            # display track details.
            trackSaved:TrackSaved
            for trackSaved in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'Track Object: "%s" (%s)' % (trackSaved.Track.Name, trackSaved.Track.Uri), trackSaved.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=trackSaved.Track.Name, uri=trackSaved.Track.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTrackFavorites_ByARTIST_ALBUM(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTrackFavorites_ByARTIST_ALBUM"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the tracks saved in the current Spotify user's 'Your Library'.
            print('\nGetting ALL saved tracks for current user ...\n')
            #pageObj:TrackPageSaved = spotify.GetTrackFavorites(limitTotal=1000)
            #pageObj:TrackPageSaved = spotify.GetTrackFavorites(limitTotal=1000, filterArtist="spotify:artist:5wpEBloInversG3zp3CVAk")  # Jeremy Camp
            pageObj:TrackPageSaved = spotify.GetTrackFavorites(limitTotal=1000, filterAlbum="spotify:album:3gSR4A397QFdzyvO2qihm3") # The Story's Not Over
            #pageObj:TrackPageSaved = spotify.GetTrackFavorites(limitTotal=1000, filterArtist="jeremy camp")
            #pageObj:TrackPageSaved = spotify.GetTrackFavorites(limitTotal=1000, filterAlbum="carried me")
            #pageObj:TrackPageSaved = spotify.GetTrackFavorites(limitTotal=1000, filterArtist="jeremy camp", filterAlbum="carried me")

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetTracks(), colorValue=SIColors.LightGreen)
            print('\nTracks in this page of results (%d items):' % pageObj.ItemsCount)

            # display track details.
            trackSaved:TrackSaved
            for trackSaved in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'Track Object: "%s" (%s)' % (trackSaved.Track.Name, trackSaved.Track.Uri), trackSaved.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=trackSaved.Track.Name, uri=trackSaved.Track.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTrack(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTrack"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            #spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a single track.
            trackId:str = '1kWUud3vY5ij5r62zxpTRy'
            print('\nGetting details for track "%s" ...\n' % trackId)
            track:Track = spotify.GetTrack(trackId)

            _logsi.LogObject(SILevel.Message,'Track Object: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Track: "%s" (%s) (Dictionary)' % (track.Name, track.Uri), track.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(track))

            print('\nArtists:')
            artist:ArtistSimplified
            for artist in track.Artists:
                print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

            print('')
            print(str(track.Album))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTrack_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTrack_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Spotify catalog information for the nowplaying track.
            print('\nGetting details for the nowplaying track ...\n')
            track:Track = spotify.GetTrack()

            _logsi.LogObject(SILevel.Message,'Track Object: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Track: "%s" (%s) (Dictionary)' % (track.Name, track.Uri), track.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(track))

            print('\nArtists:')
            artist:ArtistSimplified
            for artist in track.Artists:
                print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

            print('')
            print(str(track.Album))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTrack_MARKET_ES(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTrack_MARKET_ES"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            #spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a single track.
            trackId:str = '6kLCHFM39wkFjOuyPGLGeQ'  # "Heaven and Hell" by William Onyeabor is not available in the United States (market code US).
            market:str = 'ES'  
            print('\nGetting details for track "%s" ...\n' % trackId)
            track:Track = spotify.GetTrack(trackId, market)

            _logsi.LogObject(SILevel.Message,'Track Object: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Track: "%s" (%s) (Dictionary)' % (track.Name, track.Uri), track.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(track))

            print('\nArtists:')
            artist:ArtistSimplified
            for artist in track.Artists:
                print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

            print('')
            print(str(track.Album))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTrack_MARKET_US(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTrack_MARKET_US"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            #spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a single track.
            trackId:str = '6kLCHFM39wkFjOuyPGLGeQ'  # "Heaven and Hell" by William Onyeabor is not available in the United States (market code US).
            market:str = 'US'  
            print('\nGetting details for track "%s" ...\n' % trackId)
            track:Track = spotify.GetTrack(trackId, market)

            _logsi.LogObject(SILevel.Message,'Track Object: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Track: "%s" (%s) (Dictionary)' % (track.Name, track.Uri), track.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(track))

            print('\nArtists:')
            artist:ArtistSimplified
            for artist in track.Artists:
                print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

            print('')
            print(str(track.Album))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTrack_MARKET_NONE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTrack_MARKET_NONE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            #spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a single track.
            trackId:str = '6kLCHFM39wkFjOuyPGLGeQ'  # "Heaven and Hell" by William Onyeabor is not available in the United States (market code US).
            market:str = None
            print('\nGetting details for track "%s" ...\n' % trackId)
            track:Track = spotify.GetTrack(trackId, market)

            _logsi.LogObject(SILevel.Message,'Track Object: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Track: "%s" (%s) (Dictionary)' % (track.Name, track.Uri), track.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(track))

            print('\nArtists:')
            artist:ArtistSimplified
            for artist in track.Artists:
                print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

            print('')
            print(str(track.Album))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTrackAudioFeatures(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTrackAudioFeatures"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get audio feature information for a single track.
            trackId:str = '1kWUud3vY5ij5r62zxpTRy'
            print('\nGetting audio features for track "%s" ...\n' % trackId)
            audioFeatures:AudioFeatures = spotify.GetTrackAudioFeatures(trackId)

            _logsi.LogObject(SILevel.Message,'AudioFeatures Object: (%s)' % (audioFeatures.Uri), audioFeatures, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'AudioFeatures Object: (%s) (Dictionary)' % (audioFeatures.Uri), audioFeatures.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(audioFeatures))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTracks(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTracks"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a multiple tracks.
            trackIds:str = '1kWUud3vY5ij5r62zxpTRy,4eoYKv2kDwJS7gRGh5q6SK'
            print('\nGetting details for multiple tracks: \n- %s \n' % trackIds.replace(',','\n- '))
            tracks:list[Track] = spotify.GetTracks(trackIds)

            track:Track
            for track in tracks:
                
                _logsi.LogObject(SILevel.Message,'Track Object: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(track))

                print('\nArtist(s):')
                for artist in track.Artists:
                    print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

                print('')
                print(str(track.Album))
                print('')
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTracksAudioFeatures(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTracksAudioFeatures"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get audio features for multiple tracks based on their Spotify IDs.
            trackIds:str = '1kWUud3vY5ij5r62zxpTRy,4eoYKv2kDwJS7gRGh5q6SK'
            print('\nGetting audio features for multiple tracks: \n- %s \n' % trackIds.replace(',','\n- '))
            items:list[AudioFeatures] = spotify.GetTracksAudioFeatures(trackIds)

            audioFeatures:AudioFeatures
            for audioFeatures in items:
                
                _logsi.LogObject(SILevel.Message,'AudioFeatures Object: (%s)' % (audioFeatures.Uri), audioFeatures, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(audioFeatures))
                print('')
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTrackRecommendations_IWannaRock(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTrackRecommendations"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Spotify track recommendations for specified criteria.
            print('\nGetting track recommendations - I wanna rock!\n')
            recommendations:TrackRecommendations = spotify.GetTrackRecommendations(seedGenres='rock,hard-rock,rock-n-roll',minLoudness=-9.201,minTimeSignature=4,minEnergy=0.975)

            _logsi.LogObject(SILevel.Message,'TrackRecommendations Object', recommendations, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'TrackRecommendations Object (Dictionary)', recommendations.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(recommendations))
            print('')

            seed:RecommendationSeed
            for seed in recommendations.Seeds:
                
                _logsi.LogObject(SILevel.Message,'RecommendationSeed Object - Seed Id: "%s" (%s)' % (seed.Id, seed.Type), seed, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'RecommendationSeed Object - Seed Id: "%s" (%s) (Dictionary)' % (seed.Id, seed.Type), seed.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(seed))
                print('')

            print('Recommended Tracks:')
            track:Track
            for track in recommendations.Tracks:
                
                _logsi.LogObject(SILevel.Message,'Track: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))
                #print(str(track))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetTrackRecommendations_WindDown(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTrackRecommendations"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Spotify track recommendations for specified criteria.
            print('\nGetting track recommendations - Wind Down!\n')
            recommendations:TrackRecommendations = spotify.GetTrackRecommendations(seedArtists='3jdODvx7rIdq0UGU7BOVR3',seedGenres='piano',maxEnergy=0.175)

            _logsi.LogObject(SILevel.Message,'TrackRecommendations Object', recommendations, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'TrackRecommendations Object (Dictionary)', recommendations.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(recommendations))
            print('')

            seed:RecommendationSeed
            for seed in recommendations.Seeds:
                
                _logsi.LogObject(SILevel.Message,'RecommendationSeed Object - Seed Id: "%s" (%s)' % (seed.Id, seed.Type), seed, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'RecommendationSeed Object - Seed Id: "%s" (%s) (Dictionary)' % (seed.Id, seed.Type), seed.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(seed))
                print('')

            print('Recommended Tracks:')
            track:Track
            for track in recommendations.Tracks:
                
                _logsi.LogObject(SILevel.Message,'Track: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))
                #print(str(track))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemoveTrackFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemoveTrackFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove one or more tracks from the current user's 'Your Library'.
            trackIds:str = '1kWUud3vY5ij5r62zxpTRy,2takcwOaAZWiXQijPHIx7B,4eoYKv2kDwJS7gRGh5q6SK'
            print('\nRemoving saved track(s) from the current users profile: \n- %s' % trackIds.replace(',','\n- '))
            spotify.RemoveTrackFavorites(trackIds)
            
            _logsi.LogMessage('Success - track(s) were removed', colorValue=SIColors.LightGreen)
            print('\nSuccess - track(s) were removed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemoveTrackFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemoveTrackFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove nowplaying track from the current user's 'Your Library'.
            print('\nRemoving nowplaying track from the current users profile')
            spotify.RemoveTrackFavorites()
            
            _logsi.LogMessage('Success - track(s) were removed', colorValue=SIColors.LightGreen)
            print('\nSuccess - track(s) were removed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SaveTrackFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SaveTrackFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # save one or more tracks to the current user's 'Your Library'.
            trackIds:str = '1kWUud3vY5ij5r62zxpTRy,2takcwOaAZWiXQijPHIx7B,4eoYKv2kDwJS7gRGh5q6SK'
            print('\nAdding saved track(s) to the current users profile: \n- %s' % trackIds.replace(',','\n- '))
            spotify.SaveTrackFavorites(trackIds)
            
            _logsi.LogMessage('Success - track(s) were added', colorValue=SIColors.LightGreen)
            print('\nSuccess - track(s) were added')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SaveTrackFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SaveTrackFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # save nowplaying track to the current user's 'Your Library'.
            print('\nAdding nowplaying track favorite to current users profile')
            spotify.SaveTrackFavorites()
            
            _logsi.LogMessage('Success - track(s) were added', colorValue=SIColors.LightGreen)
            print('\nSuccess - track(s) were added')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchTracks(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchTracks"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Tracks that match a keyword string.
            criteria:str = 'Flawless'
            print('\nSearching for Tracks - criteria: "%s" ...\n' % criteria)
            searchResponse:SearchResponse = spotify.SearchTracks(criteria, limit=25)

            # display search response details.
            print(str(searchResponse))
            print('')

            # save initial search response total, as search next page response total 
            # will change with each page retrieved.  this is odd behavior, as it seems
            # that the spotify web api is returning a new result set each time rather 
            # than working off of a cached result set.
            pageObjInitialTotal:int = searchResponse.Tracks.Total

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:
                
                # only display track results for this example.
                pageObj:TrackPage = searchResponse.Tracks

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('\nTracks in this page of results:')

                # display track details.
                track:Track
                for track in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'Track Object: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))
         
                # for testing - don't return 1000 results!  
                # comment the following 3 lines of code if you want ALL results.
                if pageObj.Offset + pageObj.Limit >= 75:
                    print('\n*** Stopping paging loop after 75 entries for testing.')
                    break

                # anymore page results?
                if (pageObj.Next is None) or ((pageObj.Offset + pageObj.Limit) > pageObjInitialTotal):
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    searchResponse = spotify.SearchTracks(criteria, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchTracks_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchTracks_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Tracks that match a keyword string.
            criteria:str = 'Parliament Funkadelic'
            print('\nSearching for Tracks - criteria: "%s" ...\n' % criteria)
            pageObj:SearchResponse = spotify.SearchTracks(criteria, limitTotal=75)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results (Dictionary)' % methodName, pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print(str(pageObj.Tracks))
            print('\nTracks in this page of results (%d items):' % pageObj.Tracks.ItemsCount)

            # display track details.
            track:Track
            for track in pageObj.Tracks.Items:
        
                _logsi.LogObject(SILevel.Message,'Track: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchTracks_Criteria(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchTracks_Criteria"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # You can narrow down your search using field filters. 
            # The available filters are album, artist, track, year, upc, tag:hipster, tag:new, isrc, and genre. 
            # Each field filter only applies to certain result types.
            # The artist and year filters can be used while searching albums, artists and tracks. 
            # You can filter on a single year or a range (e.g. 1955-1960).
            # The album filter can be used while searching albums and tracks.
            # The genre filter can be used while searching artists and tracks.
            # The isrc and track filters can be used while searching tracks.
            # The upc, tag:new and tag:hipster filters can only be used while searching albums. 
            # The tag:new filter will return albums released in the past two weeks and tag:hipster can 
            # be used to return only albums with the lowest 10% popularity.
            # Example: q=remaster%2520track%3ADoxy%2520artist%3AMiles%2520Davis

            # %3A = :
            # %22 = "
            # %25 = %
            # %25 = %

            # get Spotify catalog information about Artists that match a keyword string.
            #criteria:str = '"Brandon Lake" Love'
            criteria:str = 'artist:"Brandon Lake" Love'
            print('\nSearching for Tracks - criteria: "%s" ...\n' % criteria)
            pageObj:SearchResponse = spotify.SearchTracks(criteria, limitTotal=75)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results (Dictionary)' % methodName, pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print(str(pageObj.Artists))
            print('\nArtists in this page of results (%d items):' % pageObj.Artists.ItemsCount)

            # display track details.
            track:Track
            for track in pageObj.Tracks.Items:
        
                _logsi.LogObject(SILevel.Message,'Track: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
