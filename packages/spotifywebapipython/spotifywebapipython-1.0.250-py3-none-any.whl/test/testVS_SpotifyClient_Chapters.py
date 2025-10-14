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
# SpotifyClient Tests - Chapters.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Chapters(Test_SpotifyClient_Base): 
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_GetChapter(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetChapter"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a single chapter.
            #chapterId:str = '0D5wENdkdwbqlrHoaJ9g29'
            chapterId:str = '3V0yw9UDrYAfkhAvTrvt9Y'
            print('\nGetting details for chapter id "%s" ...\n' % chapterId)
            chapter:Chapter = spotify.GetChapter(chapterId)

            _logsi.LogObject(SILevel.Message,'Chapter: "%s" (%s)' % (chapter.Name, chapter.Uri), chapter, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Chapter: "%s" (%s) (Dictionary)' % (chapter.Name, chapter.Uri), chapter.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(chapter))
            print('')

            _logsi.LogObject(SILevel.Message,'Audiobook: "%s" (%s)' % (chapter.Audiobook.Name, chapter.Audiobook.Uri), chapter.Audiobook, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(chapter.Audiobook))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetChapter_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetChapter_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # get Spotify catalog information for a single chapter.
            print('\nGetting details for nowplaying chapter id ...\n')
            chapter:Chapter = spotify.GetChapter()

            _logsi.LogObject(SILevel.Message,'Chapter: "%s" (%s)' % (chapter.Name, chapter.Uri), chapter, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Chapter: "%s" (%s) (Dictionary)' % (chapter.Name, chapter.Uri), chapter.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(chapter))
            print('')

            _logsi.LogObject(SILevel.Message,'Audiobook: "%s" (%s)' % (chapter.Audiobook.Name, chapter.Audiobook.Uri), chapter.Audiobook, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print(str(chapter.Audiobook))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetChapters(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetChapters"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get Spotify catalog information for a multiple chapters.
            chapterIds:str = '0D5wENdkdwbqlrHoaJ9g29,0PMQAsGZ8f9tSTd9moghJs'
            print('\nGetting details for multiple chapters: \n- %s \n' % chapterIds.replace(',','\n- '))
            chapters:list[ChapterSimplified] = spotify.GetChapters(chapterIds)

            chapter:ChapterSimplified
            for chapter in chapters:
                
                _logsi.LogObject(SILevel.Message,'ChapterSimplified: "%s" (%s)' % (chapter.Name, chapter.Uri), chapter, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print(str(chapter))
                print('')
    
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_IsChapterEpisode(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_IsChapterEpisode"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # is episode id an audiobook chapter?
            episodeId:str = '1mbA4ji7bRh83EqxWFni3L'
            print('\nChecking if episode ID is an audiobook chapter: \n- %s \n' % episodeId)
            result:bool = spotify.IsChapterEpisode(episodeId)

            _logsi.LogValue(SILevel.Message, 'IsChapterEpisode', result, colorValue=SIColors.LightGreen)
            print('IsChapterEpisode = %s' % str(result))
            print('')
            
        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_IsChapterEpisode_NOWPLAYING(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_IsChapterEpisode_NOWPLAYING"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientUser_PREMIUM()

            # is nowplaying item an audiobook chapter episode?
            print('\nChecking if nowplaying episode is an audiobook chapter ...\n')
            result:bool = spotify.IsChapterEpisode()

            _logsi.LogValue(SILevel.Message, 'IsChapterEpisode', result, colorValue=SIColors.LightGreen)
            print('IsChapterEpisode = %s' % str(result))
            print('')
            
        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
