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
# SpotifyClient Tests - Playlists.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Playlists(Test_SpotifyClient_Base):
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_AddPlaylistCoverImage(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_AddPlaylistCoverImage"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # upload playlist cover image for specified playlist id.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            imagePath:str = '/test/testdata/PlaylistCoverImage.jpg'
            print('\nUpdating cover image for playlist id "%s" ...\nFrom path: "%s"' % (playlistId, imagePath))
            spotify.AddPlaylistCoverImage(playlistId, imagePath)

            _logsi.LogMessage('Success - cover image was uploaded', colorValue=SIColors.LightGreen)
            print('\nSuccess - cover image was uploaded')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_AddPlaylistItems(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_AddPlaylistItems"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # add items to end of a playlist.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            itemUris:str = 'spotify:track:2takcwOaAZWiXQijPHIx7B, spotify:track:4eoYKv2kDwJS7gRGh5q6SK'
            print('\nAdding items to end of playlist id "%s" ...\n' % playlistId)
            result:str = spotify.AddPlaylistItems(playlistId, itemUris)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('Playlist updated successfully:\n- snapshot ID = "%s"' % result)

            # add items to begining of a playlist.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            itemUris:str = 'spotify:track:1kWUud3vY5ij5r62zxpTRy'
            print('\nAdding items to beginning of playlist id "%s" ...\n' % playlistId)
            result:str = spotify.AddPlaylistItems(playlistId, itemUris, 0)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('Playlist updated successfully:\n- snapshot ID = "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_AddPlaylistItems_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_AddPlaylistItems_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # add currently playing item to end of a playlist.
            playlistId:str = '2hFfHs68giBGT4eMVnqVPt'
            print('\nAdding nowplaying item to end of playlist id "%s" ...\n' % playlistId)
            result:str = spotify.AddPlaylistItems(playlistId, None)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('Playlist updated successfully:\n- snapshot ID = "%s"' % result)

            # add currently playing item to begining of a playlist.
            playlistId:str = '2hFfHs68giBGT4eMVnqVPt'
            print('\nAdding nowplaying item to beginning of playlist id "%s" ...\n' % playlistId)
            result:str = spotify.AddPlaylistItems(playlistId, None, 0)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('Playlist updated successfully:\n- snapshot ID = "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_AddPlaylistItems_LINKEDFROM(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_AddPlaylistItems_LINKEDFROM"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # add items to end of a playlist.
            playlistId:str = '3UdYCRgF3umbO7vmb3kh74'  # Prive Playlist 09
            itemUris:str = 'spotify:track:6kLCHFM39wkFjOuyPGLGeQ'  # "Heaven and Hell" by William Onyeabor, not available in the United States
            print('\nAdding items to end of playlist id "%s" ...\n' % playlistId)
            result:str = spotify.AddPlaylistItems(playlistId, itemUris)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('Playlist updated successfully:\n- snapshot ID = "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_ChangePlaylistDetails(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_ChangePlaylistDetails"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # change playlist details.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            imagePath:str = './test/testdata/PlaylistCoverImage.jpg'
            print('\nChanging playlist details for id "%s" ...\n' % playlistId)
            #spotify.ChangePlaylistDetails(playlistId, 'My New Playlist 04 updated')
            spotify.ChangePlaylistDetails(playlistId, 
                                          name='My Updated Playlist Name',
                                          description='This is an updated playlist description with a unicode copyright \u00A9 character in it - update 2.',
                                          public=False,
                                          collaborative=True,
                                          imagePath=imagePath)

            _logsi.LogMessage('Success - playlist details were updated', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist details were updated')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_CheckPlaylistFollowers(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckPlaylistFollowers"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # check to see if one or more users are following a specified playlist.
            playlistId:str = '3cEYpjA9oz9GiPac4AsH4n'
            userIds:str = spotify.UserProfile.Id  # 'jmperezperez,thelinmichael,wizzler'
            print('\nChecking followers of playlist id "%s":\n- %s' % (playlistId, userIds.replace(',','\n- ')))
            result:dict = spotify.CheckPlaylistFollowers(playlistId, userIds)
            
            _logsi.LogDictionary(SILevel.Message,'CheckPlaylistFollowers result', result, colorValue=SIColors.LightGreen)
            print('\nResults:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_ClearPlaylistItems(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_ClearPlaylistItems"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove (clear) all items items in a playlist.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            print('\nRemoving all items in playlist id "%s" ...\n' % playlistId)
            result:str = spotify.ClearPlaylistItems(playlistId)

            _logsi.LogMessage('Playlist items cleared - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('Playlist items cleared successfully:\n- snapshot ID = "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_CreatePlaylist(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CreatePlaylist"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # create a playlist for the current user.
            userId:str = spotify.UserProfile.Id
            imagePath:str = './test/testdata/PlaylistCoverImage.jpg'
            print('\nCreating new (empty) playlist for user "%s" ...\n' % userId)
            playlist:Playlist = spotify.CreatePlaylist(userId, 'My New Playlist 99',"Created from the SpotifyWebApiPython's library - test unicode \u00A9.", False, False, imagePath)

            _logsi.LogObject(SILevel.Message,'Playlist: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(playlist))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_CreatePlaylist_PRIVATE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CreatePlaylist"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # create a playlist for the current user.
            userId:str = spotify.UserProfile.Id
            imagePath:str = './test/testdata/PlaylistCoverImage.jpg'
            print('\nCreating new (empty) private playlist for user "%s" ...\n' % userId)
            playlist:Playlist = spotify.CreatePlaylist(userId, 'Private Playlist 09',"Created from the SpotifyWebApiPython's library - test unicode \u00A9.", False, False, imagePath)

            _logsi.LogObject(SILevel.Message,'Playlist: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(playlist))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    # per Spotify Developer API, deleting a playlist is not supported via the Spotify Web API.
    # this is odd though, as the playlist CAN be deleted via the Spotify Web UI!

    # def test_DeletePlaylist(self):
        
    #     _logsi:SISession = SIAuto.Main            
    #     methodName:str = "test_CreatePlaylist"

    #     try:

    #         print("Test Starting:  %s" % methodName)
    #         _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

    #         # create Spotify client instance.
    #         spotify:SpotifyClient = self._CreateApiClientUser()

    #         # create a playlist for the current user.
    #         userId:str = spotify.UserProfile.Id
    #         playlistId:str = '5AC9ZXA7nJ7oGWO911FuDG'
    #         print('\nDeleting playlist id "%s" for user "%s" ...\n' % (playlistId, userId))
    #         spotify.DeletePlaylist(userId, playlistId)

    #         _logsi.LogMessage('Success - playlist was deleted', colorValue=SIColors.LightGreen)
    #         print('\nSuccess - playlist was deleted')

    #         print("\nTest Completed: %s" % methodName)

    #     except Exception as ex:

    #         _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
    #         print("** Exception: %s" % str(ex))
    #         raise
        
        
    def test_FollowPlaylist(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_FollowPlaylist"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # add the current user as a follower of a playlist.
            playlistId:str = '3cEYpjA9oz9GiPac4AsH4n'
            print('\nFollowing playlist id "%s" ...' % playlistId)
            spotify.FollowPlaylist(playlistId, False)
            
            _logsi.LogMessage('Success - playlist is now followed', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist is now followed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_FollowPlaylist_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_FollowPlaylist_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # add the current user as a follower of a nowplaying playlist.
            print('\nFollowing nowplaying playlist ...')
            spotify.FollowPlaylist()
            
            _logsi.LogMessage('Success - nowplaying playlist is now followed', colorValue=SIColors.LightGreen)
            print('\nSuccess - nowplaying playlist is now followed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetCategoryPlaylists(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetCategoryPlaylists"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get a list of Spotify playlists tagged with a particular category.
            categoryId:str = '0JQ5DAqbMKFy0OenPG51Av' # 'toplists' # 'pop'
            print('\nGetting playlists for category "%s" ...\n' % categoryId)
            pageObj:PlaylistPageSimplified
            pageObj, message = spotify.GetCategoryPlaylists(categoryId)

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print('Playlist Results Type: "%s"\n' % str(message))
                print(str(pageObj))
                print('')
                print('Playlists in this page of results:')

                # display playlist details.
                playlist:PlaylistSimplified
                for playlist in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'PlaylistSimplified Object: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))
                    
                    # use the following to display all object properties.
                    #print(str(playlist))
                    #print('')
         
                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj, message = spotify.GetCategoryPlaylists(categoryId, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetCategoryPlaylists_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetCategoryPlaylists_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get a list of Spotify playlists tagged with a particular category.
            categoryId:str = '0JQ5DAqbMKFy0OenPG51Av' # 'toplists' # 'pop'
            print('\nGetting ALL playlists for category "%s" ...\n' % categoryId)
            pageObj:PlaylistPageSimplified
            pageObj, message = spotify.GetCategoryPlaylists(categoryId, country='US', limitTotal=1000)

            # display results.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print('Playlist Results Type: "%s"\n' % str(message))
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.Items, colorValue=SIColors.LightGreen)
            print('\nPlaylists in this page of results (%d items):' % pageObj.ItemsCount)

            # display playlist details.
            playlist:PlaylistSimplified
            for playlist in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'PlaylistSimplified Object: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetCategoryPlaylists_MadeForYou(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetCategoryPlaylists_MadeForYou"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get a list of Spotify playlists tagged with a particular category.
            categoryId:str = '0JQ5DAt0tbjZptfcdMSKl3' # special hidden category id "Made For You"
            print('\nGetting ALL playlists for category "%s" ...\n' % categoryId)
            pageObj:PlaylistPageSimplified
            pageObj, message = spotify.GetCategoryPlaylists(categoryId, limitTotal=1000)

            # display results.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print('Playlist Results Type: "%s"\n' % str(message))
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.Items, colorValue=SIColors.LightGreen)
            print('\nPlaylists in this page of results (%d items):' % pageObj.ItemsCount)

            # display playlist details.
            playlist:PlaylistSimplified
            for playlist in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'PlaylistSimplified Object: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


    def test_GetFeaturedPlaylists(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetFeaturedPlaylists"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get a list of Spotify featured playlists.
            print('\nGetting Spotify featured playlists ...\n')
            pageObj:PlaylistPageSimplified
            pageObj, message = spotify.GetFeaturedPlaylists()

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print('Playlist Results Type: "%s"\n' % str(message))
                print(str(pageObj))
                print('')
                print('Playlists in this page of results:')

                # display playlist details.
                playlist:PlaylistSimplified
                for playlist in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'PlaylistSimplified Object: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))
                    
                    # use the following to display all object properties.
                    #print(str(playlist))
                    #print('')
         
                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj, message = spotify.GetFeaturedPlaylists(offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
        
    def test_GetFeaturedPlaylists_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetFeaturedPlaylists_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get a list of Spotify featured playlists.
            print('\nGetting ALL Spotify featured playlists ...\n')
            pageObj:PlaylistPageSimplified
            pageObj, message = spotify.GetFeaturedPlaylists(limitTotal=1000)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print('Playlist Results Type: "%s"\n' % str(message))
            print(str(pageObj))
            print('\nPlaylists in this page of results (%d items):' % pageObj.ItemsCount)

            # display playlist details.
            playlist:PlaylistSimplified
            for playlist in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'PlaylistSimplified Object: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))
                    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        


    def test_GetCoverImageFile(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetCoverImageFile"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get the current image details associated with a specific playlist.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            print('\nGetting cover image details for playlist id "%s" ...\n' % playlistId)
            imageObj:ImageObject = spotify.GetPlaylistCoverImage(playlistId)

            _logsi.LogObject(SILevel.Message,'ImageObject: "%s"' % (imageObj.Url), imageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(imageObj))

            # download the cover image to the file system.
            outputPath:str = "./test/testdata/downloads/playlist_" + playlistId + "{dotfileextn}"
            print('\nGetting cover image file:\n"%s"' % outputPath)
            spotify.GetCoverImageFile(imageObj.Url, outputPath)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylist(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylist"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get a playlist owned by a Spotify user.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS' # '5v5ETK9WFXAnGQ3MRubKuE' # <- worship playlist - don't delete or modify.
            print('\nGetting details for playlist "%s" ...\n' % playlistId)
            playlist:Playlist = spotify.GetPlaylist(playlistId)

            _logsi.LogObject(SILevel.Message,'Playlist: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Playlist: "%s" (%s) (Dictionary)' % (playlist.Name, playlist.Uri), playlist.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(playlist))
            print('')

            _logsi.LogArray(SILevel.Message, 'PlaylistPage: "%s" (%s) (all Tracks for page)' % (playlist.Name, playlist.Uri), playlist.GetTracks(), colorValue=SIColors.LightGreen)
            _logsi.LogObject(SILevel.Message,'PlaylistPage: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist.Tracks, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(playlist.Tracks))

            print('\nTracks:')
            playlistTrack:PlaylistTrack
            for playlistTrack in playlist.Tracks.Items:

                _logsi.LogObject(SILevel.Message,'Playlist Track: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylist(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylist"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get a playlist owned by a Spotify user.
            playlistId:str = '1XhVM7jWPrGLTiNiAy97Za' # '37i9dQZF1E39DIjrju3A9t'
            print('\nGetting details for playlist "%s" ...\n' % playlistId)
            playlist:Playlist = spotify.GetPlaylist(playlistId)

            _logsi.LogObject(SILevel.Message,'Playlist: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Playlist: "%s" (%s) (Dictionary)' % (playlist.Name, playlist.Uri), playlist.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(playlist))
            print('')

            _logsi.LogArray(SILevel.Message, 'PlaylistPage: "%s" (%s) (all Tracks for page)' % (playlist.Name, playlist.Uri), playlist.GetTracks(), colorValue=SIColors.LightGreen)
            _logsi.LogObject(SILevel.Message,'PlaylistPage: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist.Tracks, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(playlist.Tracks))

            print('\nTracks:')
            playlistTrack:PlaylistTrack
            for playlistTrack in playlist.Tracks.Items:

                _logsi.LogObject(SILevel.Message,'Playlist Track: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri))

            # download the cover image to the file system.
            outputPath:str = "./test/testdata/downloads/%s_%s{dotfileextn}" % (playlist.Type, playlist.Id)
            print('\nGetting cover image file:\n"%s"' % outputPath)
            spotify.GetCoverImageFile(playlist.Images, outputPath)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
        

    def test_GetPlaylist_TEMP(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylist_TEMP"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get a playlist owned by a Spotify user.
            playlistId:str = '2ToocXxe5xsOIu6jMp4FvA'
            print('\nGetting details for playlist "%s" ...\n' % playlistId)
            playlist:Playlist = spotify.GetPlaylist(playlistId)

            _logsi.LogObject(SILevel.Message,'Playlist: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Playlist: "%s" (%s) (Dictionary)' % (playlist.Name, playlist.Uri), playlist.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(playlist))
            print('')

            _logsi.LogArray(SILevel.Message, 'PlaylistPage: "%s" (%s) (all Tracks for page)' % (playlist.Name, playlist.Uri), playlist.GetTracks(), colorValue=SIColors.LightGreen)
            _logsi.LogObject(SILevel.Message,'PlaylistPage: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist.Tracks, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(playlist.Tracks))

            print('\nTracks:')
            playlistTrack:PlaylistTrack
            for playlistTrack in playlist.Tracks.Items:

                _logsi.LogObject(SILevel.Message,'Playlist Track: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylist_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylist_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get nowplaying playlist owned by a Spotify user.
            print('\nGetting details for nowplaying playlist ...\n')
            playlist:Playlist = spotify.GetPlaylist()

            _logsi.LogObject(SILevel.Message,'Playlist: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Playlist: "%s" (%s) (Dictionary)' % (playlist.Name, playlist.Uri), playlist.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(playlist))
            print('')

            _logsi.LogArray(SILevel.Message, 'PlaylistPage: "%s" (%s) (all Tracks for page)' % (playlist.Name, playlist.Uri), playlist.GetTracks(), colorValue=SIColors.LightGreen)
            _logsi.LogObject(SILevel.Message,'PlaylistPage: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist.Tracks, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(playlist.Tracks))

            print('\nTracks:')
            playlistTrack:PlaylistTrack
            for playlistTrack in playlist.Tracks.Items:

                _logsi.LogObject(SILevel.Message,'Playlist Track: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylist_SpotifyDJ(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylist_SpotifyDJ"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get a playlist owned by a Spotify user.
            playlistId:str = '37i9dQZF1EYkqdzj48dyYq' # '37i9dQZF1EYkqdzj48dyYq' = Spotify DJ AI Playlist
            print('\nGetting details for playlist "%s" ...\n' % playlistId)
            playlist:Playlist = spotify.GetPlaylist(playlistId)

            _logsi.LogObject(SILevel.Message,'Playlist: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Playlist: "%s" (%s) (Dictionary)' % (playlist.Name, playlist.Uri), playlist.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(playlist))
            print('')

            _logsi.LogArray(SILevel.Message, 'PlaylistPage: "%s" (%s) (all Tracks for page)' % (playlist.Name, playlist.Uri), playlist.GetTracks(), colorValue=SIColors.LightGreen)
            _logsi.LogObject(SILevel.Message,'PlaylistPage: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist.Tracks, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(playlist.Tracks))

            print('\nTracks:')
            playlistTrack:PlaylistTrack
            for playlistTrack in playlist.Tracks.Items:

                _logsi.LogObject(SILevel.Message,'Playlist Track: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylist_MADEFORYOU(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylist_MADEFORYOU"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get a playlist owned by a Spotify user.
            playlistId:str = '37i9dQZF1E39DIjrju3A9t' # '37i9dQZF1E39DIjrju3A9t' = Spotify Daily Mix 1 Playlist
            print('\nGetting details for playlist "%s" ...\n' % playlistId)
            playlist:Playlist = spotify.GetPlaylist(playlistId)

            _logsi.LogObject(SILevel.Message,'Playlist: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message,'Playlist: "%s" (%s) (Dictionary)' % (playlist.Name, playlist.Uri), playlist.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(playlist))
            print('')

            _logsi.LogArray(SILevel.Message, 'PlaylistPage: "%s" (%s) (all Tracks for page)' % (playlist.Name, playlist.Uri), playlist.GetTracks(), colorValue=SIColors.LightGreen)
            _logsi.LogObject(SILevel.Message,'PlaylistPage: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist.Tracks, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(playlist.Tracks))

            print('\nTracks:')
            playlistTrack:PlaylistTrack
            for playlistTrack in playlist.Tracks.Items:

                _logsi.LogObject(SILevel.Message,'Playlist Track: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistCoverImage(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistCoverImage"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get the current image details associated with a specific playlist.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            print('\nGetting cover image details for playlist id "%s" ...\n' % playlistId)
            imageObj:ImageObject = spotify.GetPlaylistCoverImage(playlistId)

            _logsi.LogObject(SILevel.Message,'ImageObject: "%s"' % (imageObj.Url), imageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(imageObj))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistCoverImage_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistCoverImage_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get the current image details associated with a specific playlist.
            print('\nGetting cover image details for nowplaying playlist id ...')
            imageObj:ImageObject = spotify.GetPlaylistCoverImage()

            _logsi.LogObject(SILevel.Message,'ImageObject: "%s"' % (imageObj.Url), imageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(imageObj))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistCoverImage_DAILYMIX01(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistCoverImage_DAILYMIX01"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get the current image details associated with a specific playlist.
            playlistId:str = '37i9dQZF1E39DIjrju3A9t'
            print('\nGetting cover image details for playlist id "%s" ...\n' % playlistId)
            imageObj:ImageObject = spotify.GetPlaylistCoverImage(playlistId)

            _logsi.LogObject(SILevel.Message,'ImageObject: "%s"' % (imageObj.Url), imageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(imageObj))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistItems(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistItems"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get full details of the items of a playlist owned by a Spotify user.
            playlistId:str = '5v5ETK9WFXAnGQ3MRubKuE'
            print('\nGetting item details for playlist "%s" ...\n' % playlistId)
            pageObj:PlaylistPage = spotify.GetPlaylistItems(playlistId)

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
                playlistTrack:PlaylistTrack
                for playlistTrack in pageObj.Items:

                    _logsi.LogObject(SILevel.Message,'Playlist Track Object: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri}), added on {added} '.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri, added=playlistTrack.AddedAt))
        
                    # uncomment to dump PlaylistTrack and Track objects:
                    # _logsi.LogObject(SILevel.Message,'PlaylistTrack Object: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    # print(str(playlistTrack))
                    # print('')

                    # _logsi.LogObject(SILevel.Message,'Track Object: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    # print(str(playlistTrack.Track))

                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetPlaylistItems(playlistId, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistItems_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistItems_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get full details of the items of a playlist owned by a Spotify user.
            playlistId:str = '5v5ETK9WFXAnGQ3MRubKuE'
            print('\nGetting item details for playlist "%s" ...\n' % playlistId)
            pageObj:PlaylistPage = spotify.GetPlaylistItems(playlistId, limitTotal=1000)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('')
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetTracks(), colorValue=SIColors.LightGreen)
            print('\nTrack Item results: (%d items)' % pageObj.ItemsCount)

            # display track details.
            playlistTrack:PlaylistTrack
            for playlistTrack in pageObj.Items:

                _logsi.LogObject(SILevel.Message,'Playlist Track Object: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri}), added on {added} '.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri, added=playlistTrack.AddedAt))
        
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistItems_Fields(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistItems_Fields"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get partial details of the items of a playlist owned by a Spotify user.
            #playlistId:str = '5v5ETK9WFXAnGQ3MRubKuE'
            playlistId:str = '0kl269xqAoGBgJeHm6b4tc'  # Old Christmas Music (166 items)
            #playlistId:str = '1XhVM7jWPrGLTiNiAy97Za'  # largest playlist on spotify (4700+ items)
            #fields:str = "items(track(name,id,uri,type,duration_ms,album(name,uri),artists(name,uri)))"
            fields:str = "items(track(name,uri))"
            #fields:str = None
            additionalTypes:str = 'track'
            additionalTypes:str = None
            print('\nGetting item details for playlist "%s" ...\n' % playlistId)
            pageObj:PlaylistPage = spotify.GetPlaylistItems(playlistId, fields=fields, additionalTypes=additionalTypes, limitTotal=1000)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('')
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetTracks(), colorValue=SIColors.LightGreen)
            print('\nTrack Item results: (%d items)' % pageObj.ItemsCount)

            # display track details.
            playlistTrack:PlaylistTrack
            for playlistTrack in pageObj.Items:

                _logsi.LogObject(SILevel.Message,'Playlist Track Object: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri}), added on {added} '.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri, added=playlistTrack.AddedAt))
        
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistItems_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistItems_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get full details of the items of the nowplaying playlist.
            print('\nGetting item details for nowplaying playlist ...\n')
            pageObj:PlaylistPage = spotify.GetPlaylistItems(limitTotal=100)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('')
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetTracks(), colorValue=SIColors.LightGreen)
            print('\nTrack Item results: (%d items)' % pageObj.ItemsCount)

            # display track details.
            playlistTrack:PlaylistTrack
            for playlistTrack in pageObj.Items:

                _logsi.LogObject(SILevel.Message,'Playlist Track Object: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri}), added on {added} '.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri, added=playlistTrack.AddedAt))
        
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistItems_DAILYMIX1(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistItems_DAILYMIX1"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get full details of the items of a playlist owned by a Spotify user.
            playlistId:str = '37i9dQZF1E39vTG3GurFPW'
            print('\nGetting item details for playlist "%s" ...\n' % playlistId)
            pageObj:PlaylistPage = spotify.GetPlaylistItems(playlistId, limitTotal=1000)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('')
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetTracks(), colorValue=SIColors.LightGreen)
            print('\nTrack Item results: (%d items)' % pageObj.ItemsCount)

            # display track details.
            playlistTrack:PlaylistTrack
            for playlistTrack in pageObj.Items:

                _logsi.LogObject(SILevel.Message,'Playlist Track Object: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri}), added on {added} '.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri, added=playlistTrack.AddedAt))
        
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistItems_LINKEDFROM(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistItems_LINKEDFROM"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get full details of the items of a playlist owned by a Spotify user.
            playlistId:str = '3UdYCRgF3umbO7vmb3kh74'  # Prive Playlist 09, "Heaven and Hell" by William Onyeabor, not available in the United States
            market:str = 'ES'
            print('\nGetting item details for playlist "%s" ...\n' % playlistId)
            pageObj:PlaylistPage = spotify.GetPlaylistItems(playlistId, market=market, limitTotal=10)
            #pageObj:PlaylistPage = spotify.GetPlaylistItems(playlistId, limitTotal=10)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('')
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetTracks(), colorValue=SIColors.LightGreen)
            print('\nTrack Item results: (%d items)' % pageObj.ItemsCount)

            # display track details.
            playlistTrack:PlaylistTrack
            for playlistTrack in pageObj.Items:

                _logsi.LogObject(SILevel.Message,'Playlist Track Object: "%s" (%s)' % (playlistTrack.Track.Name, playlistTrack.Track.Uri), playlistTrack.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri}), added on {added} '.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri, added=playlistTrack.AddedAt))
        
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the playlists owned or followed by the current Spotify user.
            print('\nGetting playlists for current user ...\n')
            pageObj:PlaylistPageSimplified = spotify.GetPlaylistFavorites()

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')

                # display playlist details.
                playlist:PlaylistSimplified
                for playlist in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'PlaylistSimplified Object: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print(str(playlist))
                    print('')
         
                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('Getting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetPlaylistFavorites(offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            # # test convert to dictionary and back again.
            # testDict:dict = pageObj.ToDictionary()
            # testObj:PlaylistPageSimplified = PlaylistPageSimplified(root=testDict)
            # _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            # _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            # print(str(pageObj))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistFavorites_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistFavorites_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()
            #spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the playlists owned or followed by the current Spotify user.
            print('\nGetting ALL playlists for current user ...\n')
            pageObj:PlaylistPageSimplified = spotify.GetPlaylistFavorites(limitTotal=1000)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('\nPlaylists in this page of results (%d items):' % pageObj.ItemsCount)

            # display playlist details.
            playlist:PlaylistSimplified
            for playlist in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'PlaylistSimplified Object: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))
         
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistsForUser(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistsForUser"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the playlists owned or followed by a Spotify user.
            userId:str = 'smedjan'
            print('\nGetting playlists for user "%s" ...\n' % userId)
            pageObj:PlaylistPageSimplified = spotify.GetPlaylistsForUser(userId)

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')

                # display playlist details.
                playlist:PlaylistSimplified
                for playlist in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'PlaylistSimplified: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print(str(playlist))
                    print('')
         
                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('Getting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetPlaylistsForUser(userId, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistsForUser_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistsForUser_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the playlists owned or followed by a Spotify user.
            #userId:str = 'smedjan'
            userId:str = '31l77y2al5lnn7mxfrmd4bpfhqke'           
            print('\nGetting ALL playlists for user "%s" ...\n' % userId)
            pageObj:PlaylistPageSimplified = spotify.GetPlaylistsForUser(userId, limitTotal=1000)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('\nPlaylists in this page of results (%d items):' % pageObj.ItemsCount)

            # display playlist details.
            playlist:PlaylistSimplified
            for playlist in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'PlaylistSimplified Object: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))
         
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetPlaylistsForUser_SPOTIFY(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetPlaylistsForUser"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the playlists owned or followed by a Spotify user.
            userId:str = 'spotify'
            print('\nGetting playlists for user "%s" ...\n' % userId)
            pageObj:PlaylistPageSimplified = spotify.GetPlaylistsForUser(userId, limit=50)

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')

                # display playlist details.
                playlist:PlaylistSimplified
                for playlist in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'PlaylistSimplified: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print(str(playlist))
                    print('')
         
                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('Getting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetPlaylistsForUser(userId, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemovePlaylist(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemovePlaylist"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove playlist.
            playlistId:str = '0SCS09IHoma30gNEHpTZLJ'
            print('\nRemoving playlist id "%s"' % playlistId)
            result:str = spotify.RemovePlaylist(playlistId)

            _logsi.LogMessage('Playlist removed - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('\nPlaylist removed successfully:\n- snapshot ID = "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemovePlaylistItems(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemovePlaylistItems"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove items from current playlist.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            itemUris:str = 'spotify:track:2takcwOaAZWiXQijPHIx7B, spotify:track:4eoYKv2kDwJS7gRGh5q6SK, spotify:track:1kWUud3vY5ij5r62zxpTRy'
            print('\nRemoving items from playlist id "%s": \n- %s' % (playlistId, itemUris.replace(',','\n- ')))
            result:str = spotify.RemovePlaylistItems(playlistId, itemUris)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemovePlaylistItems_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemovePlaylistItems_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove items from current playlist.
            playlistId:str = '2hFfHs68giBGT4eMVnqVPt'
            print('\nRemoving nowplaying item from playlist id "%s"' % (playlistId))
            result:str = spotify.RemovePlaylistItems(playlistId, None)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemovePlaylistItems_Snapshot(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemovePlaylistItems_Snapshot"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove items from a playlist snapshot.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            snapshotId:str = 'NDQsMGI2ZjJhMTcyNWY3NmMyZDZhNTkxNTc5ODI0ZGFjOWRkYWM2N2QyMw===='
            itemUris:str = 'spotify:track:2takcwOaAZWiXQijPHIx7B,spotify:track:4eoYKv2kDwJS7gRGh5q6SK'
            print('\nRemoving items from snapshot playlist id "%s": \n- %s' % (playlistId, itemUris.replace(',','\n- ')))
            result:str = spotify.RemovePlaylistItems(playlistId, itemUris, snapshotId)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemovePlaylistItems_LINKEDFROM(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemovePlaylistItems_LINKEDFROM"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove items from current playlist.
            playlistId:str = '3UdYCRgF3umbO7vmb3kh74'  # Prive Playlist 09
            #itemUris:str = 'spotify:track:6ozxplTAjWO0BlUxN8ia0A'  # "Heaven and Hell" by William Onyeabor, not available in the United States (assigned item)
            itemUris:str = 'spotify:track:6kLCHFM39wkFjOuyPGLGeQ'  # "Heaven and Hell" by William Onyeabor, not available in the United States (linked_from track id)
            print('\nRemoving items from playlist id "%s": \n- %s' % (playlistId, itemUris.replace(',','\n- ')))
            result:str = spotify.RemovePlaylistItems(playlistId, itemUris)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_ReorderPlaylistItems(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_ReorderPlaylistItems"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # reorder items in current playlist - move track #5 to position #1 in the list.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            print('\nReordering items in playlist id "%s": \n- move track #5 to position #1 in the list' % (playlistId))
            result:str = spotify.ReorderPlaylistItems(playlistId, 5, 1)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

            # reorder items in current playlist - move tracks #5,6,7 to position #1 in the list.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            print('\nReordering items in playlist id "%s": \n- move tracks #5,6,7 to position #1 in the list' % (playlistId))
            result:str = spotify.ReorderPlaylistItems(playlistId, 5, 1, 3)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

            # reorder items in current playlist - move track #7 to position #6 in the list.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            print('\nReordering items in playlist id "%s": \n- move track #7 to position #6 in the list' % (playlistId))
            result:str = spotify.ReorderPlaylistItems(playlistId, 7, 6)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

            # reorder items in current playlist - move track #5 to position #10 in the list.
            playlistId:str = '4yptcTKnXjCu3V92tVVafS'
            print('\nReordering items in playlist id "%s": \n- move track #5 to position #10 in the list' % (playlistId))
            result:str = spotify.ReorderPlaylistItems(playlistId, 5, 10)

            _logsi.LogMessage('Playlist updated - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_ReplacePlaylistItems(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_ReplacePlaylistItems"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # replace items in a playlist.
            playlistId:str = '5VX6t7cVxy8Wae4qcXuPKR'
            itemUris:str = 'spotify:track:2takcwOaAZWiXQijPHIx7B, spotify:track:4eoYKv2kDwJS7gRGh5q6SK'
            print('\nReplacing items in playlist id "%s" ...\n' % playlistId)
            result:str = spotify.ReplacePlaylistItems(playlistId, itemUris)

            _logsi.LogMessage('Playlist items replaced - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('Playlist items replaced successfully:\n- snapshot ID = "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_ReplacePlaylistItems_CLEARLIST(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_ReplacePlaylistItems_CLEARLIST"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # clear items in a playlist.
            playlistId:str = '5VX6t7cVxy8Wae4qcXuPKR'
            print('\nClearing items in playlist id "%s" ...\n' % playlistId)
            result:str = spotify.ReplacePlaylistItems(playlistId)

            _logsi.LogMessage('Playlist items replaced - snapshot ID = "%s"' % result, colorValue=SIColors.LightGreen)
            print('Playlist items replaced successfully:\n- snapshot ID = "%s"' % result)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchPlaylists(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchPlaylists"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Playlists that match a keyword string.
            criteria:str = 'MercyMe'
            print('\nSearching for Playlists - criteria: "%s" ...\n' % criteria)
            searchResponse:SearchResponse = spotify.SearchPlaylists(criteria, limit=25)

            # display search response details.
            print(str(searchResponse))
            print('')

            # save initial search response total, as search next page response total 
            # will change with each page retrieved.  this is odd behavior, as it seems
            # that the spotify web api is returning a new result set each time rather 
            # than working off of a cached result set.
            pageObjInitialTotal:int = searchResponse.Playlists.Total

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:
                
                # only display playlist results for this example.
                pageObj:PlaylistPageSimplified = searchResponse.Playlists

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('\nPlaylists in this page of results:')

                # display playlist details.
                playlist:PlaylistSimplified
                for playlist in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'PlaylistSimplified Object: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))
         
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
                    searchResponse = spotify.SearchPlaylists(criteria, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchPlaylists_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchPlaylists_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Playlists that match a keyword string.
            #criteria:str = 'MercyMe'
            criteria:str = 'DJ'
            print('\nSearching for Playlists - criteria: "%s" ...\n' % criteria)
            pageObj:SearchResponse = spotify.SearchPlaylists(criteria, limitTotal=75)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results (Dictionary)' % methodName, pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print(str(pageObj.Playlists))
            print('\nPlaylists in this page of results (%d items):' % pageObj.Playlists.ItemsCount)

            # display playlist details.
            playlist:PlaylistSimplified
            for playlist in pageObj.Playlists.Items:
        
                _logsi.LogObject(SILevel.Message,'Playlist: "%s" (%s)' % (playlist.Name, playlist.Uri), playlist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
                

    def test_UnfollowPlaylist(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_UnfollowPlaylist"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove the current user as a follower of a playlist.
            playlistId:str = '3cEYpjA9oz9GiPac4AsH4n'
            print('\nUnfollowing playlist id "%s" ...' % playlistId)
            spotify.UnfollowPlaylist(playlistId)
            
            _logsi.LogMessage('Success - playlist is now unfollowed', colorValue=SIColors.LightGreen)
            print('\nSuccess - playlist is now unfollowed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_UnfollowPlaylist_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_UnfollowPlaylist_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove the current user as a follower of the nowplaying playlist.
            print('\nUnfollowing nowplaying playlist ...')
            spotify.UnfollowPlaylist()
            
            _logsi.LogMessage('Success - nowplaying playlist is now unfollowed', colorValue=SIColors.LightGreen)
            print('\nSuccess - nowplaying playlist is now unfollowed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
