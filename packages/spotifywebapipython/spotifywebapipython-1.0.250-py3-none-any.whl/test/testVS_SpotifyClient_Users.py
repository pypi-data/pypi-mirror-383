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
# SpotifyClient Tests - Users.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Users(Test_SpotifyClient_Base): 
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_CheckUsersFollowing(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckUsersFollowing"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # check to see if the current user is following one or more users.
            ids:str = 'smedjan, smedjan123'
            print('\nChecking if these users are followed by me:\n- %s\n' % (ids.replace(',','\n- ')))
            result:dict = spotify.CheckUsersFollowing(ids)
            
            _logsi.LogDictionary(SILevel.Message,'CheckUsersFollowing result', result, colorValue=SIColors.LightGreen)
            print('Results:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_FollowUsers(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_FollowUsers"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # add the current user as a follower of one or more users.
            ids:str = 'smedjan'
            print('\nStart following these users:\n- %s\n' % (ids.replace(',','\n- ')))
            spotify.FollowUsers(ids)
            
            _logsi.LogMessage('Success - users are now followed', colorValue=SIColors.LightGreen)
            print('Success - users are now followed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetUsersCurrentProfile(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetUsersCurrentProfile"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get detailed profile information about the current user.
            print('\nGetting user profile for current user ...\n')
            userProfile:UserProfile = spotify.GetUsersCurrentProfile()

            _logsi.LogObject(SILevel.Message, 'UserProfile: "%s" (%s)' % (userProfile.DisplayName, userProfile.Uri), userProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'UserProfile: "%s" (%s) (Dictionary)' % (userProfile.DisplayName, userProfile.Uri), userProfile.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(userProfile))

            # get cached configuration, refreshing from device if needed.
            userProfile:UserProfile = spotify.GetUsersCurrentProfile(refresh=False)
            print("\nCached configuration:\n%s" % str(userProfile))

            # get cached configuration directly from the configuration manager dictionary.
            if "GetUsersCurrentProfile" in spotify.ConfigurationCache:
                userProfile:UserProfile = spotify.ConfigurationCache["GetUsersCurrentProfile"]
                print("\nCached configuration direct access:\n%s" % str(userProfile))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetUsersPublicProfile(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetUsersPublicProfile"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get public profile information about a Spotify user.
            userId:str = 'smedjan'
            print('\nGetting public user profile for user id "%s" ...\n' % userId)
            userProfile:UserProfileSimplified = spotify.GetUsersPublicProfile(userId)

            _logsi.LogObject(SILevel.Message, 'UserProfileSimplified: "%s" (%s)' % (userProfile.DisplayName, userProfile.Uri), userProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'UserProfileSimplified: "%s" (%s) (Dictionary)' % (userProfile.DisplayName, userProfile.Uri), userProfile.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(userProfile))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetUsersTopArtists(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetUsersTopArtists"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get current user's top artists based on calculated affinity.
            affinity:str = 'long_term'
            print('\nGetting current user top artists for "%s" affinity ...\n' % affinity)
            pageObj:ArtistPage = spotify.GetUsersTopArtists(affinity)

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
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetUsersTopArtists(affinity, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetUsersTopArtists_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetUsersTopArtists_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get current user's top artists based on calculated affinity.
            affinity:str = 'long_term'
            print('\nGetting ALL current user top artists for "%s" affinity ...\n' % affinity)
            pageObj:ArtistPage = spotify.GetUsersTopArtists(affinity, limitTotal=1000)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results - Artists %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(pageObj))
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
        

    def test_GetUsersTopTracks(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetUsersTopTracks"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get current user's top tracks based on calculated affinity.
            affinity:str = 'long_term'
            print('\nGetting current user top tracks for "%s" affinity ...\n' % affinity)
            pageObj:TrackPage = spotify.GetUsersTopTracks(affinity)

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results - Tracks %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('')
                print('Tracks in this page of results:')

                # display track details.
                track:Track
                for track in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'Track: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))

                # trace track uri list.
                _logsi.LogText(SILevel.Message,'Track Uris', pageObj.GetUris(), colorValue=SIColors.LightGreen)

                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetUsersTopTracks(affinity, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetUsersTopTracks_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetUsersTopTracks_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get current user's top tracks based on calculated affinity.
            affinity:str = 'long_term'
            print('\nGetting ALL current user top tracks for "%s" affinity ...\n' % affinity)
            pageObj:TrackPage = spotify.GetUsersTopTracks(affinity, limitTotal=100)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results - Tracks %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(pageObj))
            print('\nTracks in this page of results (%d items):' % pageObj.ItemsCount)

            # display track details.
            track:Track
            for track in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'Track: "%s" (%s)' % (track.Name, track.Uri), track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))

            # trace track uris.
            _logsi.LogText(SILevel.Message,'Track Uris', pageObj.GetUris(), colorValue=SIColors.LightGreen)
            _logsi.LogText(SILevel.Message,'Track Uris (after uri spotify:track:10Oysheh7uae9koVLRp3pX)', pageObj.GetUris("spotify:track:10Oysheh7uae9koVLRp3pX"), colorValue=SIColors.LightGreen)
            _logsi.LogText(SILevel.Message,'Track Uris (after uri spotify:track:notexists)', pageObj.GetUris("spotify:track:notexists"), colorValue=SIColors.LightGreen)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_UnfollowUsers(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_UnfollowUsers"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove the current user as a follower of one or more users.
            ids:str = 'smedjan'
            print('\nStop following this user(s):\n- %s\n' % (ids.replace(',','\n- ')))
            spotify.UnfollowUsers(ids)
            
            _logsi.LogMessage('Success - user(s) is now unfollowed', colorValue=SIColors.LightGreen)
            print('Success - user(s) is now unfollowed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()

