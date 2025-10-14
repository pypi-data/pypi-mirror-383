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
# SpotifyClient Tests - Shows.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Shows(Test_SpotifyClient_Base): 
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_CheckShowFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckShowFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # check if one or more shows is already saved in the current Spotify user's 'Your Library'.
            showIds:str = '6kAsbP8pxwaU2kPibKTuHE,4rOoJ6Egrf8K2IrywzwOMk,1y3SUbFMUSESC1N43tBleK'
            print('\nChecking if shows are saved by the current user: \n- %s' % showIds.replace(',','\n- '))
            result:dict = spotify.CheckShowFavorites(showIds)
            
            _logsi.LogDictionary(SILevel.Message,'CheckShowFavorites result', result, colorValue=SIColors.LightGreen)
            print('\nResults:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_CheckShowFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckShowFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # check if nowplaying show is saved in the current Spotify user's 'Your Library'.
            print('\nChecking if nowplaying show is saved by the current user ...')
            result:dict = spotify.CheckShowFavorites()
            
            _logsi.LogDictionary(SILevel.Message,'CheckShowFavorites result', result, colorValue=SIColors.LightGreen)
            print('\nResults:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetShow(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetShow"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a single show.
            showId:str = '6E1u3kxII5CbbFR4VObax4'
            print('\nGetting details for show id "%s" ...\n' % showId)
            show:Show = spotify.GetShow(showId)

            _logsi.LogObject(SILevel.Message,'Show: "%s" (%s)' % (show.Name, show.Uri), show, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Show: "%s" (%s) (Dictionary)' % (show.Name, show.Uri), show.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(show))
            print('')
            
            # prepare to retrieve all episodes.
            pageObj:EpisodePageSimplified = show.Episodes
            
            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results - Episodes %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('')
                print('Episodes in this page of results:')

                # display episode details.
                episodeSimplified:EpisodeSimplified
                for episodeSimplified in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'EpisodeSimplified: "%s" (%s)' % (episodeSimplified.Name, episodeSimplified.Uri), episodeSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=episodeSimplified.Name, uri=episodeSimplified.Uri))

                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetShowEpisodes(show.Id, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            # download the cover image to the file system.
            outputPath:str = "./test/testdata/downloads/%s_%s{dotfileextn}" % (show.Type, show.Id)
            print('\nGetting cover image file:\n"%s"' % outputPath)
            spotify.GetCoverImageFile(show.Images, outputPath)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetShowEpisodes(self) -> None:
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetShowEpisodes"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about a show's episodes.
            showId:str = '6E1u3kxII5CbbFR4VObax4'
            print('\nGetting list of episodes for show id "%s" ...\n' % showId)
            pageObj:EpisodePageSimplified = spotify.GetShowEpisodes(showId) 

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')
                print('Episodes in this page of results:')

                # display episode details.
                episodeSimplified:EpisodePageSimplified
                for episodeSimplified in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'EpisodeSimplified Object: "%s" (%s)' % (episodeSimplified.Name, episodeSimplified.Uri), episodeSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=episodeSimplified.Name, uri=episodeSimplified.Uri))
                    
                    # or dump the entire object:
                    #print(str(episodeSimplified))
                    #print('')

                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetShowEpisodes(showId, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
                

    def test_GetShowEpisodes_AutoPaging(self) -> None:
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetShowEpisodes_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()
            
            # spotify:show:4QwUbrMJZ27DpjuYmN4Tun

            # get Spotify catalog information about a show's episodes.
            #showId:str = '6E1u3kxII5CbbFR4VObax4'  # Tagesschau (daily news) 
            showId:str = '4QwUbrMJZ27DpjuYmN4Tun'
            print('\nGetting list of ALL episodes for show id "%s" ...\n' % showId)
            pageObj:EpisodePageSimplified = spotify.GetShowEpisodes(showId, limitTotal=100) 

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('\nEpisodes in this page of results (%d items):' % pageObj.ItemsCount)

            # display episode details.
            episodeSimplified:EpisodePageSimplified
            for episodeSimplified in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'EpisodeSimplified Object: "%s" (%s)' % (episodeSimplified.Name, episodeSimplified.Uri), episodeSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=episodeSimplified.Name, uri=episodeSimplified.Uri))
                    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
                

    def test_GetShows(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetShows"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a multiple shows.
            showIds:str = '6kAsbP8pxwaU2kPibKTuHE,5yX0eiyk7OVq1TpNt8Owkh,6m5al8OnkyVCunFq56qwRE,6E1u3kxII5CbbFR4VObax4'
            print('\nGetting details for multiple shows: \n- %s \n' % showIds.replace(',','\n- '))
            shows:list[ShowSimplified] = spotify.GetShows(showIds)

            show:ShowSimplified
            for show in shows:
                
                _logsi.LogObject(SILevel.Message,'ShowSimplified: "%s" (%s)' % (show.Name, show.Uri), show, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(show))
                print('')
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetShowFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetShowFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the shows saved in the current Spotify user's 'Your Library'.
            print('\nGetting saved shows for current user ...\n')
            pageObj:ShowPageSaved = spotify.GetShowFavorites()

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')
                _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetShows(), colorValue=SIColors.LightGreen)
                print('Shows in this page of results:')

                # display show details.
                showSaved:ShowSaved
                for showSaved in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'ShowSimplified Object: "%s" (%s)' % (showSaved.Show.Name, showSaved.Show.Uri), showSaved.Show, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=showSaved.Show.Name, uri=showSaved.Show.Uri))

                    # use the following to display all object properties.
                    #print(str(showSaved.Show))
                    #print('')

                    # download cover image.
                    # outputPath:str = "./test/testdata/downloads/%s_%s({imagewidth}){dotfileextn}" % (showSaved.Show.Type, showSaved.Show.Id)
                    # print('\nGetting cover image file:\n"%s"' % outputPath)
                    # spotify.GetCoverImageFile(showSaved.Show.Images, outputPath)
                    # spotify.GetCoverImageFile(showSaved.Show.Images, outputPath, 640)
                    # spotify.GetCoverImageFile(showSaved.Show.Images, outputPath, 300)
                    # spotify.GetCoverImageFile(showSaved.Show.Images, outputPath, 64)
                    # spotify.GetCoverImageFile(showSaved.Show.Images[0].Url, outputPath)

                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetShowFavorites(offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetShowFavorites_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetShowFavorites_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the shows saved in the current Spotify user's 'Your Library'.
            print('\nGetting ALL saved shows for current user ...\n')
            pageObj:ShowPageSaved = spotify.GetShowFavorites(limitTotal=1000, sortResult=False)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            _logsi.LogArray(SILevel.Message, '%s Results %s (all Items for page)' % (methodName, pageObj.PagingInfo), pageObj.GetShows(), colorValue=SIColors.LightGreen)
            print('\nShows in this page of results (%d items):' % pageObj.ItemsCount)

            # display show details.
            showSaved:ShowSaved
            for showSaved in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'ShowSimplified Object: "%s" (%s)' % (showSaved.Show.Name, showSaved.Show.Uri), showSaved.Show, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=showSaved.Show.Name, uri=showSaved.Show.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemoveShowFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemoveShowFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove one or more shows from the current user's 'Your Library'.
            showIds:str = '6kAsbP8pxwaU2kPibKTuHE,4rOoJ6Egrf8K2IrywzwOMk,1y3SUbFMUSESC1N43tBleK'
            #showIds:str = '3u26tlz7A3WyWRtXliX9a9'
            print('\nRemoving saved show(s) from the current users profile: \n- %s' % showIds.replace(',','\n- '))
            spotify.RemoveShowFavorites(showIds)
            
            _logsi.LogMessage('Success - show(s) were removed', colorValue=SIColors.LightGreen)
            print('\nSuccess - show(s) were removed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemoveShowFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemoveShowFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove currently playing show from the current user's 'Your Library'.
            print('\nRemoving currently playing show from the current users profile ...')
            spotify.RemoveShowFavorites()
            
            _logsi.LogMessage('Success - show was removed', colorValue=SIColors.LightGreen)
            print('\nSuccess - show was removed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SaveShowFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SaveShowFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # save one or more shows to the current user's 'Your Library'.
            showIds:str = '6kAsbP8pxwaU2kPibKTuHE,4rOoJ6Egrf8K2IrywzwOMk,1y3SUbFMUSESC1N43tBleK'
            #showIds:str = '6kAsbP8pxwaU2kPibKTuHE'
            print('\nAdding saved show(s) to the current users profile: \n- %s' % showIds.replace(',','\n- '))
            spotify.SaveShowFavorites(showIds)
            
            _logsi.LogMessage('Success - show(s) were added', colorValue=SIColors.LightGreen)
            print('\nSuccess - show(s) were added')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SaveShowFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SaveShowFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # save currently playing show to the current user's 'Your Library'.
            print('\nAdding currently playing show to the current users profile ...')
            spotify.SaveShowFavorites()
            
            _logsi.LogMessage('Success - show was added', colorValue=SIColors.LightGreen)
            print('\nSuccess - show was added')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchShows(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchShows"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Shows that match a keyword string.
            # note - use an Authorization type of token or the `market` argument for this
            # method, otherwise the item result are all null.
            criteria:str = 'Joe Rogan'
            print('\nSearching for Shows - criteria: "%s" ...\n' % criteria)
            searchResponse:SearchResponse = spotify.SearchShows(criteria, limit=25)

            # display search response details.
            print(str(searchResponse))
            print('')

            # save initial search response total, as search next page response total 
            # will change with each page retrieved.  this is odd behavior, as it seems
            # that the spotify web api is returning a new result set each time rather 
            # than working off of a cached result set.
            pageObjInitialTotal:int = searchResponse.Shows.Total

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:
                
                # only display show results for this example.
                pageObj:ShowPageSimplified = searchResponse.Shows

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('\nShows in this page of results:')

                # display show details.
                show:ShowSimplified
                for show in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'ShowSimplified Object: "%s" (%s)' % (show.Name, show.Uri), show, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=show.Name, uri=show.Uri))
         
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
                    searchResponse = spotify.SearchShows(criteria, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchShows_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchShows_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Shows that match a keyword string.
            # note - use an Authorization type of token or the `market` argument for this
            # method, otherwise the item result are all null.
            criteria:str = 'Joe Rogan'
            print('\nSearching for Shows - criteria: "%s" ...\n' % criteria)
            pageObj:SearchResponse = spotify.SearchShows(criteria, limitTotal=75)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results (Dictionary)' % methodName, pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print(str(pageObj.Shows))
            print('\nShows in this page of results (%d items):' % pageObj.Shows.ItemsCount)

            # display show details.
            show:ShowSimplified
            for show in pageObj.Shows.Items:
        
                _logsi.LogObject(SILevel.Message,'Show: "%s" (%s)' % (show.Name, show.Uri), show, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=show.Name, uri=show.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise


# execute unit tests.
if __name__ == '__main__':
    unittest.main()
