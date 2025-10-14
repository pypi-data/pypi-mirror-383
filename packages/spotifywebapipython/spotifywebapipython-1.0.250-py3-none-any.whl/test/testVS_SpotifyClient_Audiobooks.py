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
# SpotifyClient Tests - Audiobooks.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Audiobooks(Test_SpotifyClient_Base): 
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    # test uri's:
    # 74aydHJKgYz3AIq3jjBSv1 = Terry Brooks, The Elfstones of Shannara
    # 4nfQ1hBJWjD0Jq9sK3YRW8 = Terry Brooks, The Sword of Shannara (annotated)
    # 7iHfbu1YPACw6oZPAFJtqe = Frank Herbert, Dune
    # 3PFyizE2tGCSRLusl2Qizf = Anne McCaffrey, Dragonsong


    def test_CheckAudiobookFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckAudiobookFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # check if one or more audiobooks is already saved in the current Spotify user's 'Your Library'.
            audiobookIds:str = '74aydHJKgYz3AIq3jjBSv1,4nfQ1hBJWjD0Jq9sK3YRW8,3PFyizE2tGCSRLusl2Qizf'
            print('\nChecking if audiobooks are saved by the current user: \n- %s' % audiobookIds.replace(',','\n- '))
            result:dict = spotify.CheckAudiobookFavorites(audiobookIds)
            
            _logsi.LogDictionary(SILevel.Message,'CheckAudiobookFavorites result', result, colorValue=SIColors.LightGreen)
            print('\nResults:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_CheckAudiobookFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_CheckAudiobookFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # check if nowplaying audiobook is saved in the current Spotify user's 'Your Library'.
            print('\nChecking if nowplaying audiobook is saved by the current user ...')
            result:dict = spotify.CheckAudiobookFavorites()
            
            _logsi.LogDictionary(SILevel.Message,'CheckAudiobookFavorites result', result, colorValue=SIColors.LightGreen)
            print('\nResults:')
            for key in result.keys():
                print('- %s = %s' % (key, result[key]))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAudiobook(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAudiobook"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a single audiobook.
            audiobookId:str = '7iHfbu1YPACw6oZPAFJtqe'
            print('\nGetting details for audiobook id "%s" ...\n' % audiobookId)
            audiobook:Audiobook = spotify.GetAudiobook(audiobookId)

            _logsi.LogObject(SILevel.Message,'Audiobook: "%s" (%s)' % (audiobook.Name, audiobook.Uri), audiobook, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Audiobook: "%s" (%s) (Dictionary)' % (audiobook.Name, audiobook.Uri), audiobook.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(audiobook))
            print('')
            
            # prepare to retrieve all chapters.
            pageObj:ChapterPageSimplified = audiobook.Chapters
            
            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results - Chapters %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('')
                print('Chapters in this page of results:')

                # display chapter details.
                chapterSimplified:ChapterSimplified
                for chapterSimplified in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'ChapterSimplified: "%s" (%s)' % (chapterSimplified.Name, chapterSimplified.Uri), chapterSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=chapterSimplified.Name, uri=chapterSimplified.Uri))

                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetAudiobookChapters(audiobook.Id, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            # download the cover image to the file system.
            outputPath:str = "./test/testdata/downloads/%s_%s{dotfileextn}" % (audiobook.Type, audiobook.Id)
            print('\nGetting cover image file:\n"%s"' % outputPath)
            spotify.GetCoverImageFile(audiobook.Images, outputPath)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAudiobook_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAudiobook_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Spotify catalog information for the nowplaying audiobook.
            print('\nGetting details for nowplaying audiobook ...\n')
            audiobook:Audiobook = spotify.GetAudiobook()

            _logsi.LogObject(SILevel.Message,'Audiobook: "%s" (%s)' % (audiobook.Name, audiobook.Uri), audiobook, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Audiobook: "%s" (%s) (Dictionary)' % (audiobook.Name, audiobook.Uri), audiobook.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(audiobook))
            print('')
            
        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAudiobookChapters(self) -> None:
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAudiobookChapters"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about a audiobook's chapters.
            audiobookId:str = '7iHfbu1YPACw6oZPAFJtqe'  # <- Dune - Author=Frank Herbert
            print('\nGetting list of chapters for audiobook id "%s" ...\n' % audiobookId)
            pageObj:ChapterPageSimplified = spotify.GetAudiobookChapters(audiobookId) 

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')
                print('Chapters in this page of results:')

                # display chapter details.
                chapterSimplified:ChapterPageSimplified
                for chapterSimplified in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'ChapterSimplified Object: "%s" (%s)' % (chapterSimplified.Name, chapterSimplified.Uri), chapterSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=chapterSimplified.Name, uri=chapterSimplified.Uri))
                    
                    # or dump the entire object:
                    #print(str(chapterSimplified))
                    #print('')

                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetAudiobookChapters(audiobookId, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
                

    def test_GetAudiobookChapters_AutoPaging(self) -> None:
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAudiobookChapters_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about a audiobook's chapters.
            #audiobookId:str = '7iHfbu1YPACw6oZPAFJtqe'  # <- Dune - Author=Frank Herbert
            audiobookId:str = '2kbbNqAvJZxwGyCukHoTLA'  # <- The Wishsong of Shannarra - Author=Terry Brooks
            print('\nGetting list of ALL chapters for audiobook id "%s" ...\n' % audiobookId)
            pageObj:ChapterPageSimplified = spotify.GetAudiobookChapters(audiobookId, limitTotal=1000) 

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('\nChapters in this page of results (%d items):' % pageObj.ItemsCount)

            # display chapter details.
            chapterSimplified:ChapterPageSimplified
            for chapterSimplified in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'ChapterSimplified Object: "%s" (%s)' % (chapterSimplified.Name, chapterSimplified.Uri), chapterSimplified, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=chapterSimplified.Name, uri=chapterSimplified.Uri))
                    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
                

    def test_GetAudiobookFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAudiobookFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the audiobooks saved in the current Spotify user's 'Your Library'.
            print('\nGetting saved audiobooks for current user ...\n')
            pageObj:AudiobookPageSimplified = spotify.GetAudiobookFavorites()

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')
                print('Audiobooks in this page of results:')

                # display audiobook details.
                audiobook:AudiobookSimplified
                for audiobook in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'AudiobookSimplified Object: "%s" (%s)' % (audiobook.Name, audiobook.Uri), audiobook, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=audiobook.Name, uri=audiobook.Uri))

                    # use the following to display all object properties.
                    #print(str(audiobook))
                    #print('')
         
                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetAudiobookFavorites(offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
    
    def test_GetAudiobookFavorites_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAudiobookFavorites_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get a list of the audiobooks saved in the current Spotify user's 'Your Library'.
            print('\nGetting ALL saved audiobooks for current user ...\n')
            pageObj:AudiobookPageSimplified = spotify.GetAudiobookFavorites(limitTotal=1000, sortResult=True)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('\nAudiobooks in this page of results (%d items):' % pageObj.ItemsCount)

            # display audiobook details.
            audiobook:AudiobookSimplified
            for audiobook in pageObj.Items:
        
                _logsi.LogObject(SILevel.Message,'AudiobookSimplified Object: "%s" (%s)' % (audiobook.Name, audiobook.Uri), audiobook, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=audiobook.Name, uri=audiobook.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        
    
    def test_GetAudiobooks(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAudiobooks"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a multiple audiobooks.
            audiobookIds:str = '74aydHJKgYz3AIq3jjBSv1,4nfQ1hBJWjD0Jq9sK3YRW8'
            print('\nGetting details for multiple audiobooks: \n- %s \n' % audiobookIds.replace(',','\n- '))
            audiobooks:list[AudiobookSimplified] = spotify.GetAudiobooks(audiobookIds)

            audiobook:AudiobookSimplified
            for audiobook in audiobooks:
                
                _logsi.LogObject(SILevel.Message,'AudiobookSimplified: "%s" (%s)' % (audiobook.Name, audiobook.Uri), audiobook, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(audiobook))
                print('')
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemoveAudiobookFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemoveAudiobookFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove one or more audiobooks from the current user's 'Your Library'.
            audiobookIds:str = '3PFyizE2tGCSRLusl2Qizf,7iHfbu1YPACw6oZPAFJtqe'
            print('\nRemoving saved audiobook(s) from the current users profile: \n- %s' % audiobookIds.replace(',','\n- '))
            spotify.RemoveAudiobookFavorites(audiobookIds)
            
            _logsi.LogMessage('Success - audiobook(s) were removed', colorValue=SIColors.LightGreen)
            print('\nSuccess - audiobook(s) were removed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_RemoveAudiobookFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_RemoveAudiobookFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # remove currently playing audiobook from the current user's 'Your Library'.
            print('\nRemoving currently playing audiobook from the current users profile ...')
            spotify.RemoveAudiobookFavorites()
            
            _logsi.LogMessage('Success - audiobook was removed', colorValue=SIColors.LightGreen)
            print('\nSuccess - audiobook was removed')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SaveAudiobookFavorites(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SaveAudiobookFavorites"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # save one or more audiobooks to the current user's 'Your Library'.
            audiobookIds:str = '3PFyizE2tGCSRLusl2Qizf,7iHfbu1YPACw6oZPAFJtqe'
            print('\nAdding saved audiobook(s) to the current users profile: \n- %s' % audiobookIds.replace(',','\n- '))
            spotify.SaveAudiobookFavorites(audiobookIds)
            
            _logsi.LogMessage('Success - audiobook(s) were added', colorValue=SIColors.LightGreen)
            print('\nSuccess - audiobook(s) were added')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SaveAudiobookFavorites_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SaveAudiobookFavorites_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # save currently playing audiobook to the current user's 'Your Library'.
            print('\nAdding currently playing audiobook to the current users profile')
            spotify.SaveAudiobookFavorites()
            
            _logsi.LogMessage('Success - audiobook was added', colorValue=SIColors.LightGreen)
            print('\nSuccess - audiobook was added')

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchAudiobooks(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchAudiobooks"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Audiobooks that match a keyword string.
            criteria:str = 'Terry Brooks'
            print('\nSearching for Audiobooks - criteria: "%s" ...\n' % criteria)
            searchResponse:SearchResponse = spotify.SearchAudiobooks(criteria, limit=25)

            # display search response details.
            print(str(searchResponse))
            print('')

            # save initial search response total, as search next page response total 
            # will change with each page retrieved.  this is odd behavior, as it seems
            # that the spotify web api is returning a new result set each time rather 
            # than working off of a cached result set.
            pageObjInitialTotal:int = searchResponse.Audiobooks.Total

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:
                
                # only display audiobook results for this example.
                pageObj:AudiobookPageSimplified = searchResponse.Audiobooks

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(pageObj))
                print('\nAudiobooks in this page of results:')

                # display audiobook details.
                audiobook:AudiobookSimplified
                for audiobook in pageObj.Items:
        
                    _logsi.LogObject(SILevel.Message,'AudiobookSimplified Object: "%s" (%s)' % (audiobook.Name, audiobook.Uri), audiobook, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=audiobook.Name, uri=audiobook.Uri))
         
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
                    searchResponse = spotify.SearchAudiobooks(criteria, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SearchAudiobooks_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SearchAudiobooks_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser()

            # get Spotify catalog information about Audiobooks that match a keyword string.
            criteria:str = 'Terry Brooks'
            print('\nSearching for Audiobooks - criteria: "%s" ...\n' % criteria)
            pageObj:SearchResponse = spotify.SearchAudiobooks(criteria, limitTotal=75)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results' % (methodName), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results (Dictionary)' % methodName, pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print(str(pageObj.Audiobooks))
            print('\nAudiobooks in this page of results (%d items):' % pageObj.Audiobooks.ItemsCount)

            # display audiobook details.
            audiobook:Audiobook
            for audiobook in pageObj.Audiobooks.Items:
        
                _logsi.LogObject(SILevel.Message,'Audiobook: "%s" (%s)' % (audiobook.Name, audiobook.Uri), audiobook, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=audiobook.Name, uri=audiobook.Uri))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
