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
# SpotifyClient Tests - Artists.
#
# Test Uri's:
# Uri="spotify:artist:6APm8EjxOHSYM5B4i3vT3q" - Artist="MercyMe"
# Uri="spotify:album:6vc9OTcyd3hyzabCmsdnwE"  - Artist="MercyMe", Album="Welcome to the New"
# Uri="spotify:track:1kWUud3vY5ij5r62zxpTRy"  - Artist="MercyMe", Album="Welcome to the New", Track="Flawless"
#
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Artists(Test_SpotifyClient_Base):
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_CheckArtistsFollowing(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckArtistsFollowing"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # check to see if the current user is following one or more artists.
            ids:str = '2CIMQHirSU0MQqyYHq0eOx,1IQ2e1buppatiN1bxUVkrk'
            print('\nChecking if these artists are followed by me:\n- %s\n' % (ids.replace(',','\n- ')))
            result:dict = spotify.CheckArtistsFollowing(ids)
            
            _logsi.LogDictionary(SILevel.Message,'CheckArtistsFollowing result', result, colorValue=SIColors.LightGreen)
            print('Results:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_CheckArtistsFollowing_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckArtistsFollowing_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # check to see if the current user is following currently playing artist.
            print('\nChecking if currently playing artist is followed by me ...')
            result:dict = spotify.CheckArtistsFollowing()
            
            _logsi.LogDictionary(SILevel.Message,'CheckArtistsFollowing result', result, colorValue=SIColors.LightGreen)
            print('Results:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_FollowArtists(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_FollowArtists"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # add the current user as a follower of one or more artists.
            ids:str = '2CIMQHirSU0MQqyYHq0eOx,1IQ2e1buppatiN1bxUVkrk'
            print('\nStart following these artists:\n- %s\n' % (ids.replace(',','\n- ')))
            spotify.FollowArtists(ids)
            
            _logsi.LogMessage('Success - artists are now followed', colorValue=SIColors.LightGreen)
            print('Success - artists are now followed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_FollowArtists_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_FollowArtists_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # add the current user as a follower of the currently playing artist.
            print('\nStart following the artist currently playing')
            spotify.FollowArtists()
            
            _logsi.LogMessage('Success - artist is now followed', colorValue=SIColors.LightGreen)
            print('Success - artist is now followed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtist(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtist"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a single artist.
            artistId:str = '6APm8EjxOHSYM5B4i3vT3q'
            print('\nGetting details for Artist "%s" ...\n' % artistId)
            artist:Artist = spotify.GetArtist(artistId)

            _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(artist).__name__, artist.Name, artist.Uri), artist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s: "%s" (%s) (Dictionary)' % (type(artist).__name__, artist.Name, artist.Uri), artist.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(artist))

            # download the cover image to the file system.
            outputPath:str = "./test/testdata/downloads/%s_%s{dotfileextn}" % (artist.Type, artist.Id)
            print('\nGetting cover image file:\n"%s"' % outputPath)
            spotify.GetCoverImageFile(artist.Images, outputPath)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtist_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtist_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Spotify catalog information for the nowplaying artist.
            print('\nGetting details for nowplaying Artist ...\n')
            artist:Artist = spotify.GetArtist()

            _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(artist).__name__, artist.Name, artist.Uri), artist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s: "%s" (%s) (Dictionary)' % (type(artist).__name__, artist.Name, artist.Uri), artist.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(artist))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtistAlbums(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtistAlbums"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information about an artist's albums.
            artistId:str = '6APm8EjxOHSYM5B4i3vT3q'
            includeGroups:str = 'album,single,appears_on,compilation'
            print('\nGetting albums for artist id "%s" ...\n' % artistId)
            pageObj:AlbumPageSimplified = spotify.GetArtistAlbums(artistId, includeGroups, limit=50)

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
        
                    _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(albumSimplified).__name__, albumSimplified.Name, albumSimplified.Uri), albumSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=albumSimplified.Name, uri=albumSimplified.Uri))

                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetArtistAlbums(artistId, includeGroups, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtistAlbums_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtistAlbums_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Spotify catalog information about the nowplaying artist's albums.
            includeGroups:str = 'album,single,appears_on,compilation'
            print('\nGetting ALL albums for nowplaying artist ...\n')
            pageObj:AlbumPageSimplified = spotify.GetArtistAlbums(None, includeGroups, limitTotal=1000)

            # display results.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.Items, colorValue=SIColors.LightGreen)
            print('\nArtists in this page of results (%d items):' % pageObj.ItemsCount)

            # display album details.
            albumSimplified:AlbumSimplified
            for albumSimplified in pageObj.Items:

                _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(albumSimplified).__name__, albumSimplified.Name, albumSimplified.Uri), albumSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=albumSimplified.Name, uri=albumSimplified.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtistAlbums_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtistAlbums_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information about an artist's albums.
            artistId:str = '6APm8EjxOHSYM5B4i3vT3q'
            includeGroups:str = 'album,single,appears_on,compilation'
            print('\nGetting ALL albums for artist id "%s" ...\n' % artistId)
            pageObj:AlbumPageSimplified = spotify.GetArtistAlbums(artistId, includeGroups, limitTotal=1000)

            # display results.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.Items, colorValue=SIColors.LightGreen)
            print('\nArtists in this page of results (%d items):' % pageObj.ItemsCount)

            # display album details.
            albumSimplified:AlbumSimplified
            for albumSimplified in pageObj.Items:

                _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(albumSimplified).__name__, albumSimplified.Name, albumSimplified.Uri), albumSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=albumSimplified.Name, uri=albumSimplified.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtistAlbums_ALBUMS_APPEARSON(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtistAlbums_ALBUMS_APPEARSON"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information about an artist's albums.
            artistId:str = '6APm8EjxOHSYM5B4i3vT3q'
            includeGroups:str = 'appears_on'
            #includeGroups:str = 'album,single,appears_on,compilation'
            print('\nGetting "%s" albums for artist id:\n- "%s" \n' % (includeGroups, artistId))
            pageObj:AlbumPageSimplified = spotify.GetArtistAlbums(artistId, includeGroups, limitTotal=100)

            # display results.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.Items, colorValue=SIColors.LightGreen)
            print('\nArtists in this page of results (%d items):' % pageObj.ItemsCount)

            # display album details.
            albumSimplified:AlbumSimplified
            for albumSimplified in pageObj.Items:

                _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(albumSimplified).__name__, albumSimplified.Name, albumSimplified.Uri), albumSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=albumSimplified.Name, uri=albumSimplified.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtistAlbums_ALBUMS_COMPILATION(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtistAlbums_ALBUMS_COMPILATION"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information about an artist's albums.
            artistId:str = '6APm8EjxOHSYM5B4i3vT3q'
            includeGroups:str = 'compilation'
            #includeGroups:str = 'album,single,appears_on,compilation'
            print('\nGetting "%s" albums for artist id:\n- "%s" \n' % (includeGroups, artistId))
            pageObj:AlbumPageSimplified = spotify.GetArtistAlbums(artistId, includeGroups, limitTotal=100)

            # display results.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.Items, colorValue=SIColors.LightGreen)
            print('\nArtists in this page of results (%d items):' % pageObj.ItemsCount)

            # display album details.
            albumSimplified:AlbumSimplified
            for albumSimplified in pageObj.Items:

                _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(albumSimplified).__name__, albumSimplified.Name, albumSimplified.Uri), albumSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=albumSimplified.Name, uri=albumSimplified.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtistAlbums_ALBUMS_SINGLE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtistAlbums_ALBUMS_SINGLE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information about an artist's albums.
            artistId:str = '6APm8EjxOHSYM5B4i3vT3q'
            includeGroups:str = 'single'
            #includeGroups:str = 'album,single,appears_on,compilation'
            print('\nGetting "%s" albums for artist id:\n- "%s" \n' % (includeGroups, artistId))
            pageObj:AlbumPageSimplified = spotify.GetArtistAlbums(artistId, includeGroups, limitTotal=100)

            # display results.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.Items, colorValue=SIColors.LightGreen)
            print('\nArtists in this page of results (%d items):' % pageObj.ItemsCount)

            # display album details.
            albumSimplified:AlbumSimplified
            for albumSimplified in pageObj.Items:

                _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(albumSimplified).__name__, albumSimplified.Name, albumSimplified.Uri), albumSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=albumSimplified.Name, uri=albumSimplified.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtistInfo(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtistInfo"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information for a single artist.
            #artistId = '6APm8EjxOHSYM5B4i3vT3q'   # MercyMe
            #artistId = '6kFLnclYFc3gzpNt13wim5'   # Seventh Day Slumber
            #artistId = '7sQ7ufWIlfao5lJOBJfgkS'   # AirKraft
            #artistId = '1LmsXfZSt1nutb8OCvt00G'   # Petra
            #artistId = '6eGXFEwOdfD1dIPyu6c5cG'   # Steve Green (former Whiteheart member)
            #artistId = '0sA93wBoY7nJUE8dSrOZay'   # Keith Green
            #artistId = '5Yu3b48Y29bZlI1cLPOZJz'   # Danny Gokey
            artistId = '0rvjqX7ttXeg3mTy8Xscbt'   # Journey
            print('\nGetting details for Artist "%s" ...\n' % artistId)
            artistInfo:ArtistInfo = spotify.GetArtistInfo(artistId)

            _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(artistInfo).__name__, artistInfo.Name, artistInfo.Uri), artistInfo, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s: "%s" (%s) (Dictionary)' % (type(artistInfo).__name__, artistInfo.Name, artistInfo.Uri), artistInfo.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(artistInfo))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtists(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtists"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for several artists.
            artistIds:str = '6APm8EjxOHSYM5B4i3vT3q,22sg0OT5BG5eWLBN97WPIZ,1LmsXfZSt1nutb8OCvt00G'
            print('\nGetting details for multiple artists: \n- %s \n' % artistIds.replace(',','\n- '))
            artists:list[Artist] = spotify.GetArtists(artistIds)

            artist:Artist
            for artist in artists:
                
                _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(artist).__name__, artist.Name, artist.Uri), artist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s: "%s" (%s) (Dictionary)' % (type(artist).__name__, artist.Name, artist.Uri), artist.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(artist))
                print('')
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex: 

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtistRelatedArtists(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtistRelatedArtists"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Spotify catalog information about artists similar to a given artist.
            artistId:str = '6APm8EjxOHSYM5B4i3vT3q'
            print('\nGetting artists similar to artist "%s" ...\n' % artistId)
            artists:list[Artist] = spotify.GetArtistRelatedArtists(artistId)

            artist:Artist
            for artist in artists:
                
                _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(artist).__name__, artist.Name, artist.Uri), artist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s: "%s" (%s) (Dictionary)' % (type(artist).__name__, artist.Name, artist.Uri), artist.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
                print(str(artist))
                print('')
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtistsFollowed(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtistsFollowed"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get the current user's followed artists.
            print('\nGetting current users followed artists ...\n')
            pageObj:ArtistPage = spotify.GetArtistsFollowed(limit=20)

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results - Artists %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('')
                print('Artists in this page of results:')
                
                # display artist details.
                artist:Artist
                for artist in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'Artist: "%s" (%s)' % (artist.Name, artist.Uri), artist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

                # anymore page results?
                if (pageObj.Next is None) \
                or (pageObj.IsCursor and pageObj.CursorAfter is None and pageObj.CursorBefore is None):
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of items ...\n')
                    pageObj = spotify.GetArtistsFollowed(after=artist.Id, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtistsFollowed_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtistsFollowed_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get the current user's followed artists.
            print('\nGetting ALL of the current users followed artists ...\n')
            pageObj:ArtistPage = spotify.GetArtistsFollowed(limitTotal=1000, sortResult=False)

            # display results.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.Items, colorValue=SIColors.LightGreen)
            print('\nArtists in this page of results (%d items):' % pageObj.ItemsCount)

            # display artist details.
            artist:Artist
            for artist in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'Artist: "%s" (%s)' % (artist.Name, artist.Uri), artist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetArtistTopTracks(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetArtistTopTracks"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information about an artist's top tracks by country.
            artistId:str = '6APm8EjxOHSYM5B4i3vT3q'
            print('\nGetting top tracks for artist id "%s" ...\n' % artistId)
            tracks:list[Track] = spotify.GetArtistTopTracks(artistId, 'ES', False)

            track:Track
            for track in tracks:
                
                _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(track).__name__, track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(track))
                print('')
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchArtists(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchArtists"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Artists that match a keyword string.
            criteria:str = 'MercyMe'
            print('\nSearching for Artists - criteria: "%s" ...\n' % criteria)
            searchResponse:SearchResponse = spotify.SearchArtists(criteria, limit=25)

            # display search response details.
            print(str(searchResponse))
            print('')

            # save initial search response total, as search next page response total 
            # will change with each page retrieved.  this is odd behavior, as it seems
            # that the spotify web api is returning a new result set each time rather 
            # than working off of a cached result set.
            pageObjInitialTotal:int = searchResponse.Artists.Total

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:
                
                # only display artist results for this example.
                pageObj:ArtistPage = searchResponse.Artists

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('\nArtists in this page of results:')

                # display artist details.
                artist:Artist
                for artist in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(artist).__name__, artist.Name, artist.Uri), artist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))
         
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
                    searchResponse = spotify.SearchArtists(criteria, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchArtists_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchArtists_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Artists that match a keyword string.
            criteria:str = 'MercyMe'
            print('\nSearching for Artists - criteria: "%s" ...\n' % criteria)
            pageObj:SearchResponse = spotify.SearchArtists(criteria, limitTotal=75)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results (Dictionary)' % methodName, pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print(str(pageObj.Artists))
            print('\nArtists in this page of results (%d items):' % pageObj.Artists.ItemsCount)

            # display artist details.
            artist:Artist
            for artist in pageObj.Artists.Items:
        
                _logsi.LogObject(SILevel.Message,'%s: "%s" (%s)' % (type(artist).__name__, artist.Name, artist.Uri), artist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_UnfollowArtists(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_UnfollowArtists"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove the current user as a follower of one or more artists.
            ids:str = '2CIMQHirSU0MQqyYHq0eOx,1IQ2e1buppatiN1bxUVkrk'
            print('\nStop following these artists:\n- %s\n' % (ids.replace(',','\n- ')))
            spotify.UnfollowArtists(ids)
            
            _logsi.LogMessage('Success - artists are now unfollowed', colorValue=SIColors.LightGreen)
            print('Success - artists are now unfollowed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_UnfollowArtists_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_UnfollowArtists_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # remove the current user as a follower of the nowplaying artist.
            print('\nStop following the nowplaying artist')
            spotify.UnfollowArtists()
            
            _logsi.LogMessage('Success - artist is now unfollowed', colorValue=SIColors.LightGreen)
            print('Success - artist is now unfollowed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
