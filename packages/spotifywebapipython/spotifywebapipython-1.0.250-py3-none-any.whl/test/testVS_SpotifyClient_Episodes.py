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
# SpotifyClient Tests - Episodes.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Episodes(Test_SpotifyClient_Base): 
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_CheckEpisodeFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckEpisodeFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # check if one or more episodes is already saved in the current Spotify user's 'Your Library'.
            episodeIds:str = '1hPX5WJY6ja6yopgVPBqm4,3F97boSWlXi8OzuhWClZHQ'
            print('\nChecking if episodes are saved by the current user: \n- %s' % episodeIds.replace(',','\n- '))
            result:dict = spotify.CheckEpisodeFavorites(episodeIds)
            
            _logsi.LogDictionary(SILevel.Message,'CheckEpisodeFavorites result', result, colorValue=SIColors.LightGreen)
            print('\nResults:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_CheckEpisodeFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckEpisodeFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # check if nowplaying episode is already saved in the current Spotify user's 'Your Library'.
            print('\nChecking if nowplaying episode is saved by the current user ...')
            result:dict = spotify.CheckEpisodeFavorites()
            
            _logsi.LogDictionary(SILevel.Message,'CheckEpisodeFavorites result', result, colorValue=SIColors.LightGreen)
            print('\nResults:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetEpisode(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetEpisode"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information for a single episode.
            episodeId:str = '26c0zVyOv1lzfYpBXdh1zC'
            print('\nGetting details for episode id "%s" ...\n' % episodeId)
            episode:Episode = spotify.GetEpisode(episodeId)

            _logsi.LogObject(SILevel.Message,'Episode: "%s" (%s)' % (episode.Name, episode.Uri), episode, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Episode: "%s" (%s) (Dictionary)' % (episode.Name, episode.Uri), episode.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(episode))
            
            # download the cover image to the file system.
            outputPath:str = "./test/testdata/downloads/%s_%s{dotfileextn}" % (episode.Type, episode.Id)
            print('\nGetting cover image file:\n"%s"' % outputPath)
            spotify.GetCoverImageFile(episode.Images, outputPath)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetEpisode_NowPlaying(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetEpisode_NowPlaying"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Spotify catalog information for the nowplaying episode.
            print('\nGetting details for nowplaying episode ...\n')
            episode:Episode = spotify.GetEpisode()

            _logsi.LogObject(SILevel.Message,'Episode: "%s" (%s)' % (episode.Name, episode.Uri), episode, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Episode: "%s" (%s) (Dictionary)' % (episode.Name, episode.Uri), episode.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(episode))
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetEpisodes(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetEpisodes"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information for a multiple episodes.
            episodeIds:str = '16OUc3NwQe7kJNaH8zmzfP,1hPX5WJY6ja6yopgVPBqm4,3F97boSWlXi8OzuhWClZHQ'
            print('\nGetting details for multiple episodes: \n- %s \n' % episodeIds.replace(',','\n- '))
            episodes:list[Episode] = spotify.GetEpisodes(episodeIds)

            episode:Episode
            for episode in episodes:
                
                _logsi.LogObject(SILevel.Message,'Episode: "%s" (%s)' % (episode.Name, episode.Uri), episode, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(episode))
                print('')
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetEpisodeFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetEpisodeFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the episodes saved in the current Spotify user's 'Your Library'.
            print('\nGetting saved episodes for current user ...\n')
            pageObj:EpisodePageSaved = spotify.GetEpisodeFavorites()

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')
                _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetEpisodes(), colorValue=SIColors.LightGreen)
                print('Episodes in this page of results:')

                # display episode details.
                episodeSaved:EpisodeSaved
                for episodeSaved in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'EpisodeSimplified Object: "%s" (%s)' % (episodeSaved.Episode.Name, episodeSaved.Episode.Uri), episodeSaved.Episode, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=episodeSaved.Episode.Name, uri=episodeSaved.Episode.Uri))

                    # use the following to display all object properties.
                    #print(str(episodeSaved.Episode))
                    #print('')
         
                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetEpisodeFavorites(offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetEpisodeFavorites_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetEpisodeFavorites_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the episodes saved in the current Spotify user's 'Your Library'.
            print('\nGetting ALL saved episodes for current user ...\n')
            pageObj:EpisodePageSaved = spotify.GetEpisodeFavorites(limitTotal=1000)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetEpisodes(), colorValue=SIColors.LightGreen)
            print('\nEpisodes in this page of results (%d items):' % pageObj.ItemsCount)

            # display episode details.
            episodeSaved:EpisodeSaved
            for episodeSaved in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'EpisodeSimplified Object: "%s" (%s)' % (episodeSaved.Episode.Name, episodeSaved.Episode.Uri), episodeSaved.Episode, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=episodeSaved.Episode.Name, uri=episodeSaved.Episode.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemoveEpisodeFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemoveEpisodeFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove one or more episodes from the current user's 'Your Library'.
            episodeIds:str = '1hPX5WJY6ja6yopgVPBqm4,3F97boSWlXi8OzuhWClZHQ'
            print('\nRemoving saved episode(s) from the current users profile: \n- %s' % episodeIds.replace(',','\n- '))
            spotify.RemoveEpisodeFavorites(episodeIds)
            
            _logsi.LogMessage('Success - episode(s) were removed', colorValue=SIColors.LightGreen)
            print('\nSuccess - episode(s) were removed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemoveEpisodeFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemoveEpisodeFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove currently playing episode from the current user's 'Your Library'.
            print('\nRemoving currently playing episode from the current users profile ...')
            spotify.RemoveEpisodeFavorites()
            
            _logsi.LogMessage('Success - episode was removed', colorValue=SIColors.LightGreen)
            print('\nSuccess - episode was removed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SaveEpisodeFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SaveEpisodeFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # save one or more episodes to the current user's 'Your Library'.
            episodeIds:str = '1hPX5WJY6ja6yopgVPBqm4,3F97boSWlXi8OzuhWClZHQ'
            print('\nAdding saved episode(s) to the current users profile: \n- %s' % episodeIds.replace(',','\n- '))
            spotify.SaveEpisodeFavorites(episodeIds)
            
            _logsi.LogMessage('Success - episode(s) were added', colorValue=SIColors.LightGreen)
            print('\nSuccess - episode(s) were added')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SaveEpisodeFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SaveEpisodeFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # save currently playing episode to the current user's 'Your Library'.
            print('\nAdding nowplaying episode to the current users profile')
            spotify.SaveEpisodeFavorites()
            
            _logsi.LogMessage('Success - episode was added', colorValue=SIColors.LightGreen)
            print('\nSuccess - episode was added')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchEpisodes(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchEpisodes"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Episodes that match a keyword string.
            # note - use an Authorization type of token or the `market` argument for this
            # method, otherwise the item result are all null.
            criteria:str = 'The LOL Podcast'
            print('\nSearching for Episodes - criteria: "%s" ...\n' % criteria)
            searchResponse:SearchResponse = spotify.SearchEpisodes(criteria, limit=25)

            # display search response details.
            print(str(searchResponse))
            print('')

            # save initial search response total, as search next page response total 
            # will change with each page retrieved.  this is odd behavior, as it seems
            # that the spotify web api is returning a new result set each time rather 
            # than working off of a cached result set.
            pageObjInitialTotal:int = searchResponse.Episodes.Total

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:
                
                # only display episode results for this example.
                pageObj:EpisodePageSimplified = searchResponse.Episodes

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('\nEpisodes in this page of results:')

                # display episode details.
                episode:EpisodeSimplified
                for episode in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'EpisodeSimplified Object: "%s" (%s)' % (episode.Name, episode.Uri), episode, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=episode.Name, uri=episode.Uri))
         
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
                    searchResponse = spotify.SearchEpisodes(criteria, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchEpisodes_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchEpisodes_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Episodes that match a keyword string.
            # note - use an Authorization type of token or the `market` argument for this
            # method, otherwise the item result are all null.
            criteria:str = 'The LOL Podcast'
            print('\nSearching for Episodes - criteria: "%s" ...\n' % criteria)
            pageObj:SearchResponse = spotify.SearchEpisodes(criteria, limitTotal=75)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results (Dictionary)' % methodName, pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print(str(pageObj.Episodes))
            print('\nEpisodes in this page of results (%d items):' % pageObj.Episodes.ItemsCount)

            # display episode details.
            episode:EpisodeSimplified
            for episode in pageObj.Episodes.Items:
        
                _logsi.LogObject(SILevel.Message,'Episode: "%s" (%s)' % (episode.Name, episode.Uri), episode, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=episode.Name, uri=episode.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
