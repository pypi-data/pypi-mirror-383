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
# SpotifyClient Tests - Albums.
#
# Test Uri's:
# Uri="spotify:artist:6APm8EjxOHSYM5B4i3vT3q" - Artist="MercyMe"
# Uri="spotify:album:6vc9OTcyd3hyzabCmsdnwE"  - Artist="MercyMe", Album="Welcome to the New"
# Uri="spotify:track:1kWUud3vY5ij5r62zxpTRy"  - Artist="MercyMe", Album="Welcome to the New", Track="Flawless"
#
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Albums(Test_SpotifyClient_Base):
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_CheckAlbumFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckAlbumFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # check if one or more albums is already saved in the current Spotify user's 'Your Library'.
            albumIds:str = '382ObEPsp2rxGrnsizN5TX,6vc9OTcyd3hyzabCmsdnwE,382ObEPsp2rxGrnsizN5TY'
            print('\nChecking if albums are saved by the current user: \n- %s' % albumIds.replace(',','\n- '))
            result:dict = spotify.CheckAlbumFavorites(albumIds)
            
            _logsi.LogDictionary(SILevel.Message,'CheckAlbumFavorites result', result, colorValue=SIColors.LightGreen, prettyPrint=True)
            print('\nResults:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_CheckAlbumFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckAlbumFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # check if nowplaying album is saved in the current Spotify user's 'Your Library'.
            print('\nChecking if nowplaying album is saved by the current user ...')
            result:dict = spotify.CheckAlbumFavorites()
            
            _logsi.LogDictionary(SILevel.Message,'CheckAlbumFavorites result', result, colorValue=SIColors.LightGreen, prettyPrint=True)
            print('\nResults:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAlbum(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAlbum"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a single album.
            albumId:str = '6vc9OTcyd3hyzabCmsdnwE'
            print('\nGetting details for Album "%s" ...\n' % albumId)
            album:Album = spotify.GetAlbum(albumId)
            
            _logsi.LogObject(SILevel.Message,'Album: "%s" (%s)' % (album.Name, album.Uri), album, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Album: "%s" (%s) (Dictionary)' % (album.Name, album.Uri), album.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(album))

            print('\nArtists:')
            artist:ArtistSimplified
            for artist in album.Artists:
                print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

            print('\nTracks:')
            track:TrackSaved
            for track in album.Tracks.Items:
                print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))
    
            # download the cover image to the file system.
            outputPath:str = "./test/testdata/downloads/%s_%s{dotfileextn}" % (album.Type, album.Id)
            print('\nGetting cover image file:\n"%s"' % outputPath)
            spotify.GetCoverImageFile(album.Images, outputPath)
            # spotify.GetCoverImageFile(album.Images, outputPath, 640)
            # spotify.GetCoverImageFile(album.Images, outputPath, 300)
            # spotify.GetCoverImageFile(album.Images, outputPath, 64)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAlbum_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAlbum_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Spotify catalog information for nowplaying album.
            print('\nGetting details for nowplaying Album ...\n')
            album:Album = spotify.GetAlbum()
            
            _logsi.LogObject(SILevel.Message,'Album: "%s" (%s)' % (album.Name, album.Uri), album, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Album: "%s" (%s) (Dictionary)' % (album.Name, album.Uri), album.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(album))

            print('\nArtists:')
            artist:ArtistSimplified
            for artist in album.Artists:
                print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

            print('\nTracks:')
            track:TrackSaved
            for track in album.Tracks.Items:
                print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAlbum_UNICODE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAlbum_UNICODE"

        # this will test the processing of an album name that containe UNICODE characters.
        # see developer_notes.txt for more information.

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a single album.
            albumId:str = '0Sl4hjNHwOrVq6rnexErGu'
            print('\nGetting details for Album "%s" ...\n' % albumId)
            album:Album = spotify.GetAlbum(albumId)
            
            print('** Note - Album details contain UniCode characters ...')
            _logsi.LogObject(SILevel.Message,'Album: "%s" (%s)' % (album.Name, album.Uri), album, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Album: "%s" (%s) (Dictionary)' % (album.Name, album.Uri), album.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(album))

            print('\nArtists:')
            artist:ArtistSimplified
            for artist in album.Artists:
                print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

            print('\nTracks:')
            track:TrackSaved
            for track in album.Tracks.Items:
                print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_GetAlbums(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAlbums"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a multiple albums.
            albumIds:str = '6vc9OTcyd3hyzabCmsdnwE,382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc'
            print('\nGetting details for multiple albums: \n- %s \n' % albumIds.replace(',','\n- '))
            albums:list[Album] = spotify.GetAlbums(albumIds)

            album:Album
            for album in albums:
                
                _logsi.LogObject(SILevel.Message,'Album: "%s" (%s)' % (album.Name, album.Uri), album, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, 'Album: "%s" (%s) (Dictionary)' % (album.Name, album.Uri), album.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)                
                print(str(album))

                print('\nArtist(s):')
                for artist in album.Artists:
                    print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

                print('\nTracks:')
                track:TrackSaved
                for track in album.Tracks.Items:
                    print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))

                print('')
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAlbumNewReleases(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAlbumNewReleases"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get a list of new album releases featured in Spotify.
            print('\nGetting list of new album releases featured in Spotify ...\n')
            pageObj:AlbumPageSimplified = spotify.GetAlbumNewReleases()

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')
                print('Albums in this page of results:')

                # display album details.
                albumSimplified:AlbumSimplified
                for albumSimplified in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'AlbumSimplified Object: "%s" (%s)' % (albumSimplified.Name, albumSimplified.Uri), albumSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=albumSimplified.Name, uri=albumSimplified.Uri))

                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetAlbumNewReleases(offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAlbumNewReleases_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAlbumNewReleases_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get a list of new album releases featured in Spotify.
            print('\nGetting list of ALL new album releases featured in Spotify ...\n')
            pageObj:AlbumPageSimplified = spotify.GetAlbumNewReleases(limitTotal=1000)

            # display results.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.Items, colorValue=SIColors.LightGreen)
            print('\nAlbums in this page of results (%d items):' % pageObj.ItemsCount)

            # display album details.
            albumSimplified:AlbumSimplified
            for albumSimplified in pageObj.Items:

                _logsi.LogObject(SILevel.Message,'AlbumSimplified Object: "%s" (%s)' % (albumSimplified.Name, albumSimplified.Uri), albumSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=albumSimplified.Name, uri=albumSimplified.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAlbumTracks(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAlbumTracks"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information about an album's tracks.
            albumId:str = '6vc9OTcyd3hyzabCmsdnwE'
            print('\nGetting list of tracks for album id "%s" ...\n' % albumId)
            pageObj:TrackPageSimplified = spotify.GetAlbumTracks(albumId) 

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')
                print('Tracks in this page of results:')

                # display track details.
                trackSimplified:TrackPageSimplified
                for trackSimplified in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'TrackSimplified Object: "%s" (%s)' % (trackSimplified.Name, trackSimplified.Uri), trackSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=trackSimplified.Name, uri=trackSimplified.Uri))
                    
                    # or dump the entire object:
                    #print(str(trackSimplified))
                    #print('')

                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetAlbumTracks(albumId, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAlbumTracks_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAlbumTracks_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Spotify catalog information about the nowplaying album's tracks.
            print('\nGetting list of ALL tracks for nowplaying album ...\n')
            pageObj:TrackPageSimplified = spotify.GetAlbumTracks(limitTotal=1000) 

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('\nTracks in this page of results (%d items):' % pageObj.ItemsCount)

            # display track details.
            trackSimplified:TrackPageSimplified
            for trackSimplified in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'TrackSimplified Object: "%s" (%s)' % (trackSimplified.Name, trackSimplified.Uri), trackSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=trackSimplified.Name, uri=trackSimplified.Uri))
                    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAlbumTracks_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAlbumTracks_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information about an album's tracks.
            albumId:str = '6vc9OTcyd3hyzabCmsdnwE'
            print('\nGetting list of ALL tracks for album id "%s" ...\n' % albumId)
            pageObj:TrackPageSimplified = spotify.GetAlbumTracks(albumId, limitTotal=1000) 

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('\nTracks in this page of results (%d items):' % pageObj.ItemsCount)

            # display track details.
            trackSimplified:TrackPageSimplified
            for trackSimplified in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'TrackSimplified Object: "%s" (%s)' % (trackSimplified.Name, trackSimplified.Uri), trackSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=trackSimplified.Name, uri=trackSimplified.Uri))
                    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAlbumTracks_AutoPaging_100tracks(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAlbumTracks_AutoPaging_100tracks"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information about an album's tracks.
            albumId:str = '0nO5lyFdotlbbWdNkvB6Av'  # 100 Greatest Hits of the 90's
            print('\nGetting list of ALL tracks for album id "%s" ...\n' % albumId)
            pageObj:TrackPageSimplified = spotify.GetAlbumTracks(albumId, limitTotal=1000) 

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('\nTracks in this page of results (%d items):' % pageObj.ItemsCount)

            # display track details.
            trackSimplified:TrackPageSimplified
            for trackSimplified in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'TrackSimplified Object: "%s" (%s)' % (trackSimplified.Name, trackSimplified.Uri), trackSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=trackSimplified.Name, uri=trackSimplified.Uri))
                    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAlbumFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAlbumFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the albums saved in the current Spotify user's 'Your Library'.
            print('\nGetting saved albums for current user ...\n')
            pageObj:AlbumPageSaved = spotify.GetAlbumFavorites()

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')
                _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetAlbums(), colorValue=SIColors.LightGreen)
                print('Albums in this page of results:')

                # display album details.
                albumSaved:AlbumSaved
                for albumSaved in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'AlbumSaved Object: "%s" (%s)' % (albumSaved.Album.Name, albumSaved.Album.Uri), albumSaved.Album, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=albumSaved.Album.Name, uri=albumSaved.Album.Uri))

                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetAlbumFavorites(offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAlbumFavorites_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAlbumFavorites_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the albums saved in the current Spotify user's 'Your Library'.
            print('\nGetting ALL saved albums for current user ...\n')
            pageObj:AlbumPageSaved = spotify.GetAlbumFavorites(limitTotal=1000, sortResult=False)

            # display results.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetAlbums(), colorValue=SIColors.LightGreen)
            print('\nAlbums in this page of results (%d items):' % pageObj.ItemsCount)

            # display album details.
            albumSaved:AlbumSaved
            for albumSaved in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'AlbumSaved Object: "%s" (%s)' % (albumSaved.Album.Name, albumSaved.Album.Uri), albumSaved.Album, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=albumSaved.Album.Name, uri=albumSaved.Album.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemoveAlbumFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemoveAlbumFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove one or more albums from the current user's 'Your Library'.
            albumIds:str = '382ObEPsp2rxGrnsizN5TX,6vc9OTcyd3hyzabCmsdnwE,0hAvA0PQn6l17LHUA1EPQK'
            print('\nRemoving saved album(s) from the current users profile: \n- %s' % albumIds.replace(',','\n- '))
            spotify.RemoveAlbumFavorites(albumIds)
            
            _logsi.LogMessage('Success - album(s) were removed', colorValue=SIColors.LightGreen)
            print('\nSuccess - album(s) were removed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemoveAlbumFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemoveAlbumFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # remove nowplaying track album from the current user's 'Your Library'.
            print('\nRemoving nowplaying track album from the current users profile')
            spotify.RemoveAlbumFavorites()
            
            _logsi.LogMessage('Success - album(s) were removed', colorValue=SIColors.LightGreen)
            print('\nSuccess - album(s) were removed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SaveAlbumFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SaveAlbumFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # save one or more albums to the current user's 'Your Library'.
            albumIds:str = '382ObEPsp2rxGrnsizN5TX,6vc9OTcyd3hyzabCmsdnwE,0hAvA0PQn6l17LHUA1EPQK,1ssGLn8MxlaOnOoB2c47yl,78csIQhw9OOMGPpwCvXKgx'
            print('\nAdding saved album(s) to the current users profile: \n- %s' % albumIds.replace(',','\n- '))
            spotify.SaveAlbumFavorites(albumIds)
            
            _logsi.LogMessage('Success - album(s) were added', colorValue=SIColors.LightGreen)
            print('\nSuccess - album(s) were added')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_SaveAlbumFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SaveAlbumFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # save nowplaying track album to the current user's 'Your Library'.
            print('\nSaving nowplaying track album to the current users profile')
            spotify.SaveAlbumFavorites()
            
            _logsi.LogMessage('Success - album(s) were added', colorValue=SIColors.LightGreen)
            print('\nSuccess - album(s) were added')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_SearchAlbums(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchAlbums"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Albums that match a keyword string.
            criteria:str = 'Welcome to the New'
            print('\nSearching for Albums - criteria: "%s" ...\n' % criteria)
            searchResponse:SearchResponse = spotify.SearchAlbums(criteria, limit=25)

            # display search response details.
            print(str(searchResponse))
            print('')

            # save initial search response total, as search next page response total 
            # will change with each page retrieved.  this is odd behavior, as it seems
            # that the spotify web api is returning a new result set each time rather 
            # than working off of a cached result set.
            pageObjInitialTotal:int = searchResponse.Albums.Total

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:
                
                # only display album results for this example.
                pageObj:AlbumPageSimplified = searchResponse.Albums

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('\nAlbums in this page of results:')

                # display album details.
                album:AlbumSimplified
                for album in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'AlbumSimplified Object: "%s" (%s)' % (album.Name, album.Uri), album, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=album.Name, uri=album.Uri))
         
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
                    searchResponse = spotify.SearchAlbums(criteria, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchAlbums_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchAlbums_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Albums that match a keyword string.
            criteria:str = 'Welcome to the New'
            print('\nSearching for Albums - criteria: "%s" ...\n' % criteria)
            pageObj:SearchResponse = spotify.SearchAlbums(criteria, limitTotal=75)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results (Dictionary)' % methodName, pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print(str(pageObj.Albums))
            print('\nAlbums in this page of results (%d items):' % pageObj.Albums.ItemsCount)

            # display album details.
            album:AlbumSimplified
            for album in pageObj.Albums.Items:
        
                _logsi.LogObject(SILevel.Message,'AlbumSimplified: "%s" (%s)' % (album.Name, album.Uri), album, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=album.Name, uri=album.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
