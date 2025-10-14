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
# SpotifyClient Tests - Miscellaneous.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Miscellaneous(Test_SpotifyClient_Base):
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_GetGenres(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetGenres"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get a list of available genre seed parameter values for recommendations.
            print('\nGetting list of genres ...')
            genres:list[str] = spotify.GetGenres()

            # display genre details.
            _logsi.LogArray(SILevel.Message,'Genres list', genres, colorValue=SIColors.LightGreen)
            print('\nAll Genres (sorted by name - %d items):' % len(genres))
            genre:str
            for genre in genres:

                print('- "{name}"'.format(name=genre))

            # get cached configuration, refreshing from device if needed.
            genres:list[str] = spotify.GetGenres(refresh=False)
            print("\nCached configuration (count): %d" % len(genres))

            # get cached configuration directly from the configuration manager dictionary.
            if "GetGenres" in spotify.ConfigurationCache:
                genres:list[str] = spotify.ConfigurationCache["GetGenres"]
                print("\nCached configuration direct access (count): %d" % len(genres))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetIdFromUri(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetIdFromUri"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen) 

            # get Id portion of a spotify Uri.
            uri:str = 'spotify:track:1kWUud3vY5ij5r62zxpTRy'
            print('\nGetting Id portion of Spotify Uri value:\n- "%s"' % uri)
            result:str = SpotifyClient.GetIdFromUri(uri)

            _logsi.LogValue(SILevel.Message, 'Id', result, colorValue=SIColors.LightGreen)
            print('result: "%s"' % result)

            # get Id portion of a spotify Uri.
            uri:str = 'spotify:track:'
            print('\nGetting Id portion of Spotify Uri value:\n- "%s"' % uri)
            result:str = SpotifyClient.GetIdFromUri(uri)

            _logsi.LogValue(SILevel.Message, 'Id', result, colorValue=SIColors.LightGreen)
            print('result: "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_GetImagePaletteColors(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetImagePaletteColors"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen) 

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM_NoDiscovery()

            # get the palette colors for an image https url.
            imageSource:str = "https://i.scdn.co/image/ab67616d0000b2733deaee5f76ab2da15dd8db86"
            print('\nGetting palette colors for image https url:\n- "%s" ...' % imageSource)
            result:ImagePaletteColors = spotify.GetImagePaletteColors(imageSource)
            _logsi.LogObject(SILevel.Message,'Image Palette Colors', result, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Image Palette Colors (dict)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(result.ToString())

            # get the palette colors for an image http url.
            imageSource:str = "http://i.scdn.co/image/ab67616d0000b2733deaee5f76ab2da15dd8db86"
            print('\nGetting palette colors for image http url:\n- "%s" ...' % imageSource)
            result:ImagePaletteColors = spotify.GetImagePaletteColors(imageSource)
            _logsi.LogObject(SILevel.Message,'Image Palette Colors', result, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Image Palette Colors (dict)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(result.ToString())

            # get the palette colors for an image on the file system.
            imageSource:str = './test/testdata/PlaylistCoverImage.jpg'
            print('\nGetting palette colors for image file:\n- "%s" ...' % imageSource)
            result:ImagePaletteColors = spotify.GetImagePaletteColors(imageSource)
            _logsi.LogObject(SILevel.Message,'Image Palette Colors', result, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Image Palette Colors (dict)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(result.ToString())

            # # get the palette colors for the currently playing Spotify item image url.
            # print('\nGetting palette colors for currently playing image url ...')
            # result:ImagePaletteColors = spotify.GetImagePaletteColors()
            # _logsi.LogObject(SILevel.Message,'Image Palette Colors', result, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            # _logsi.LogDictionary(SILevel.Message,'Image Palette Colors (dict)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            # print(result.ToString())

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_GetImagePaletteColors_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetImagePaletteColors_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen) 

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM_NoDiscovery()

            # get the palette colors for the currently playing Spotify item image url.
            print('\nGetting palette colors for currently playing image url ...')
            result:ImagePaletteColors = spotify.GetImagePaletteColors()
            _logsi.LogObject(SILevel.Message,'Image Palette Colors', result, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Image Palette Colors (dict)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(result.ToString())

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_GetImagePaletteColors_1URL(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetImagePaletteColors_1URL"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen) 

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM_NoDiscovery()

            #imageSource:str = "https://i.scdn.co/image/ab67616d0000b273b3f691a43c5d139895f8cc3d"   # Jeremy Camp, Restored (spotify:track:7rcgBqWrTTSgt4wSuzq2rk)
            #imageSource:str = "https://i.scdn.co/image/ab67616d0000b2730c255b1049c859f19b55ff66"   # Matthew West, The Story of Your Life (spotify:track:xxxxx)
            #imageSource:str = "https://i.scdn.co/image/ab67616d0000b27374b19c16057d91830979d43d"   # Francis Lai Laven, La lecon particuliere (`spotify:track:3NWRapFZSlpHXO38LW21rw`)
            #imageSource:str = "https://i.scdn.co/image/ab67616d0000b27336eaa88d33968ee025d0b3d1"   # Dezko, Ascend (`spotify:track:199wv1uOJYZ1XyK8FTzwh2`)
            #imageSource:str = "https://i.scdn.co/image/ab67616d0000b2739a69906b91b18801e18e42c2"   # Orbit, Summer Someday (`spotify:track:2uETu1hY79BdvX9wRqQgrh`)

            # from Ben's test playlist: https://open.spotify.com/playlist/10zDRUNVBUnxMRkXPQTr9X?si=1WA65tZgRWq5qD7xP2Vfpg&pi=vL45YVPwR9ia3
            #imageSource:str = "https://i.scdn.co/image/ab67616d0000b273a310d79b3ab4304e7d363afe"   # Forrester, MoonLight (`spotify:track:1y2PkgJWyNF39Djta5BaPe`)
            #imageSource:str = "https://i.scdn.co/image/ab67616d0000b27333d63fa24cabd82d6c7c676f"   # The MidNight, Days of Thunder (`spotify:track:4loXMor75kKVBB03ygwDlh`)
            #imageSource:str = "https://i.scdn.co/image/ab67616d0000b2731ce9547e2191494e0a7313d5"   # Know Good, Fire Inside (`spotify:track:3An32L74nhnYRDJrx1fW6O`)
            #imageSource:str = "https://i.scdn.co/image/ab67616d0000b273bb4325d269632efa08956036"   # HeyZ, Turn the Tide (`spotify:track:7r5s7HP6dJvcQjYrb0ZsoK`)
            #imageSource:str = "https://i.scdn.co/image/ab67616d0000b27347941121dc059eb9412ca872"   # Barry Can't Swim, When Will We Land (`spotify:track:1WaiCFnNlnpy6NFf3Ga00R`)
            #imageSource:str = "https://i.scdn.co/image/ab67616d0000b2734e8dbbdfe7768629efce4a03"   # Last Island, Don't Even Think About It (`spotify:track:5nZaDgnU3rcqwDlVYOOItT`)

            # get the palette colors for a url image.
            imageSource:str = "https://i.scdn.co/image/ab67616d0000b2733deaee5f76ab2da15dd8db86"   # Dezko, Ascend (`spotify:track:199wv1uOJYZ1XyK8FTzwh2`)
            print('\nGetting Palette colors for image url:\n- "%s" ...' % imageSource)
            result:ImagePaletteColors = spotify.GetImagePaletteColors(imageSource, 10, 2, 200, 600, 20)
            _logsi.LogObject(SILevel.Message,'Image Palette Colors', result, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Image Palette Colors (dict)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(result.ToString())

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_GetImagePaletteColors_1FILE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetImagePaletteColors_1FILE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen) 

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM_NoDiscovery()

            # get the palette colors for an image on the file system.
            imageSource:str = './test/testdata/PlaylistCoverImage.jpg'
            print('\nGetting Palette colors for image file:\n- "%s" ...' % imageSource)
            result:ImagePaletteColors = spotify.GetImagePaletteColors(imageSource)
            _logsi.LogObject(SILevel.Message,'Image Palette Colors', result, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Image Palette Colors (dict)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(result.ToString())

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_GetImageVibrantColors(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetImageVibrantColors"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen) 

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM_NoDiscovery()

            # get the vibrant colors for an image https url.
            imageSource:str = "https://i.scdn.co/image/ab67616d0000b2733deaee5f76ab2da15dd8db86"
            print('\nGetting vibrant colors for image https url:\n- "%s" ...' % imageSource)
            result:ImageVibrantColors = spotify.GetImageVibrantColors(imageSource)
            _logsi.LogObject(SILevel.Message,'Image Vibrant Colors', result, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Image Vibrant Colors (dict)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(result.ToString())

            # get the vibrant colors for an image http url.
            imageSource:str = "http://i.scdn.co/image/ab67616d0000b2733deaee5f76ab2da15dd8db86"
            print('\nGetting vibrant colors for image http url:\n- "%s" ...' % imageSource)
            result:ImageVibrantColors = spotify.GetImageVibrantColors(imageSource)
            _logsi.LogObject(SILevel.Message,'Image Vibrant Colors', result, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Image Vibrant Colors (dict)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(result.ToString())

            # get the vibrant colors for an image on the file system.
            imageSource:str = './test/testdata/PlaylistCoverImage.jpg'
            print('\nGetting vibrant colors for image file:\n- "%s" ...' % imageSource)
            result:ImageVibrantColors = spotify.GetImageVibrantColors(imageSource)
            _logsi.LogObject(SILevel.Message,'Image Vibrant Colors', result, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Image Vibrant Colors (dict)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(result.ToString())

            # # get the vibrant colors for the currently playing Spotify item image url.
            # print('\nGetting vibrant colors for currently playing image url ...')
            # result:ImageVibrantColors = spotify.GetImageVibrantColors()
            # _logsi.LogObject(SILevel.Message,'Image Vibrant Colors', result, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            # _logsi.LogDictionary(SILevel.Message,'Image Vibrant Colors (dict)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            # print(result.ToString())

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_GetImageVibrantColors_1File(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetImageVibrantColors_1File"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen) 

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM_NoDiscovery()

            # get the vibrant colors for an image on the file system.
            imageSource:str = './test/testdata/PlaylistCoverImage.jpg'
            print('\nGetting vibrant colors for image file:\n- "%s" ...' % imageSource)
            result:ImageVibrantColors = spotify.GetImageVibrantColors(imageSource)
            _logsi.LogObject(SILevel.Message,'Image Vibrant Colors', result, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Image Vibrant Colors (dict)', result.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(result.ToString())

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_GetMarkets(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetMarkets"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen) 

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get the list of markets where Spotify is available.
            print('\nGetting list of markets ...')
            markets:list[str] = spotify.GetMarkets()

            # display genre details.
            _logsi.LogArray(SILevel.Message,'Markets list', markets, colorValue=SIColors.LightGreen)
            print('\nAll Markets (sorted by id - %d items):' % len(markets))
            market:str
            for market in markets:

                print('- "{name}"'.format(name=market))

            # get cached configuration, refreshing from device if needed.
            markets:list[str] = spotify.GetMarkets(refresh=False)
            print("\nCached configuration (count): %d" % len(markets))

            # get cached configuration directly from the configuration manager dictionary.
            if "GetMarkets" in spotify.ConfigurationCache:
                markets:list[str] = spotify.ConfigurationCache["GetMarkets"]
                print("\nCached configuration direct access (count): %d" % len(markets))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_GetTypeFromUri(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetTypeFromUri"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen) 

            # get Type portion of a spotify Uri.
            uri:str = 'spotify:track:1kWUud3vY5ij5r62zxpTRy'
            print('\nGetting Type portion of Spotify Uri value:\n- "%s"' % uri)
            result:str = SpotifyClient.GetTypeFromUri(uri)

            _logsi.LogValue(SILevel.Message, 'Id', result, colorValue=SIColors.LightGreen)
            print('result: "%s"' % result)

            # get Type portion of a spotify Uri.
            uri:str = 'spotify:track:'
            print('\nGetting Type portion of Spotify Uri value:\n- "%s"' % uri)
            result:str = SpotifyClient.GetTypeFromUri(uri)

            _logsi.LogValue(SILevel.Message, 'Id', result, colorValue=SIColors.LightGreen)
            print('result: "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_GetSpotifyClientVersion(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetSpotifyClientVersion"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # display SpotifyClient version details.
            _logsi.LogString(SILevel.Message,'SpotifyClient version', spotify.Version, colorValue=SIColors.LightGreen)
            print('\nSpotifyClient version: %s:' % spotify.Version)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_Search(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_Search"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about objects that match a keyword string.
            criteria:str = 'Welcome to the New'
            criteriaType:str = 'album,artist,track,playlist'
            print('\nSearch criteria types: "%s"')
            print('\nSearching for criteria: "%s" ...' % criteria)
            searchResp:SearchResponse = spotify.Search(criteria, criteriaType, limitTotal=5)

            # display search results.
            item:SearchResultBase
            print('\nAlbums (%d items):' % searchResp.AlbumsCount)
            _logsi.LogMessage('Albums (%d items):' % searchResp.AlbumsCount, colorValue=SIColors.LightGreen)
            for item in searchResp.Albums.Items:
                _logsi.LogObject(SILevel.Message,'SearchResultBase: "%s" (%s)' % (item.Name, item.Uri), item, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

            print('\nArtists (%d items):' % searchResp.ArtistsCount)
            _logsi.LogMessage('Artists (%d items):' % searchResp.ArtistsCount, colorValue=SIColors.LightGreen)
            for item in searchResp.Artists.Items:
                _logsi.LogObject(SILevel.Message,'SearchResultBase: "%s" (%s)' % (item.Name, item.Uri), item, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

            print('\nAudiobooks (%d items):' % searchResp.AudiobooksCount)
            _logsi.LogMessage('Audiobooks (%d items):' % searchResp.AudiobooksCount, colorValue=SIColors.LightGreen)
            for item in searchResp.Audiobooks.Items:
                _logsi.LogObject(SILevel.Message,'SearchResultBase: "%s" (%s)' % (item.Name, item.Uri), item, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

            print('\nEpisodes (%d items):' % searchResp.EpisodesCount)
            _logsi.LogMessage('Episodes (%d items):' % searchResp.EpisodesCount, colorValue=SIColors.LightGreen)
            for item in searchResp.Episodes.Items:
                _logsi.LogObject(SILevel.Message,'SearchResultBase: "%s" (%s)' % (item.Name, item.Uri), item, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

            print('\nPlaylists (%d items):' % searchResp.PlaylistsCount)
            _logsi.LogMessage('Playlists (%d items):' % searchResp.PlaylistsCount, colorValue=SIColors.LightGreen)
            for item in searchResp.Playlists.Items:
                _logsi.LogObject(SILevel.Message,'SearchResultBase: "%s" (%s)' % (item.Name, item.Uri), item, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

            print('\nShows (%d items):' % searchResp.ShowsCount)
            _logsi.LogMessage('Shows (%d items):' % searchResp.ShowsCount, colorValue=SIColors.LightGreen)
            for item in searchResp.Shows.Items:
                _logsi.LogObject(SILevel.Message,'SearchResultBase: "%s" (%s)' % (item.Name, item.Uri), item, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

            print('\nTracks (%d items):' % searchResp.TracksCount)
            _logsi.LogMessage('Tracks (%d items):' % searchResp.TracksCount, colorValue=SIColors.LightGreen)
            for item in searchResp.Tracks.Items:
                _logsi.LogObject(SILevel.Message,'SearchResultBase: "%s" (%s)' % (item.Name, item.Uri), item, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
