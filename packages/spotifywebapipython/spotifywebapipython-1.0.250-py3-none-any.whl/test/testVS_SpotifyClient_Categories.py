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
# SpotifyClient Tests - Categories.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Categories(Test_SpotifyClient_Base):
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_GetBrowseCategory(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetBrowseCategory"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get a single category used to tag items in Spotify.
            categoryId:str = '0JQ5DACFo5h0jxzOyHOsIo' # "Christian and Gospel" category id
            #categoryId:str = '0JQ5DAt0tbjZptfcdMSKl3' # "Made For You" category id
            print('\nGetting details for category "%s" ...\n' % categoryId)
            category:Category = spotify.GetBrowseCategory(categoryId)

            _logsi.LogObject(SILevel.Message,'Category: "%s" (%s)' % (category.Name, category.Id), category, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, 'Category: "%s" (%s) (Dictionary)' % (category.Name, category.Id), category.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)           
            print(str(category))
            
            print('\nIcons(s):')
            for icon in category.Icons:
                print(str(icon))

            # get cached configuration, refreshing from device if needed.
            spotify.GetBrowseCategorys()  # load cache
            category:Category = spotify.GetBrowseCategory(categoryId, refresh=False)
            print("\nCached configuration:\n%s" % str(category))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetBrowseCategorys(self):
        
        _logsi:SISession = SIAuto.Main
        methodName:str = "test_GetBrowseCategorys"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get a list of categories used to tag items in Spotify.
            print('\nGetting browse categories ...\n')
            pageObj:CategoryPage = spotify.GetBrowseCategorys(limit=50)

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # display paging details.
                _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
                print(str(pageObj))
                print('')
                print('Categories in this page of results:')

                # display category details.
                category:Category
                for category in pageObj.Items:

                    _logsi.LogObject(SILevel.Message,'Category: "%s" (%s)' % (category.Name, category.Id), category, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                    print('- "{name}" ({uri})'.format(name=category.Name, uri=category.Id))
        
                    # uncomment to dump Category object:
                    #print(str(category))
                    #print('')

                # anymore page results?
                if pageObj.Next is None:
                    # no - all pages were processed.
                    break
                else:
                    # yes - retrieve the next page of results.
                    print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
                    pageObj = spotify.GetBrowseCategorys(offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetBrowseCategorys_AutoPaging(self):
        
        _logsi:SISession = SIAuto.Main
        methodName:str = "test_GetBrowseCategorys_AutoPaging"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get a list of categories used to tag items in Spotify.
            print('\nGetting ALL browse categories ...\n')
            pageObj:CategoryPage = spotify.GetBrowseCategorys(limitTotal=100)

            # display paging details.
            _logsi.LogObject(SILevel.Message, '%s Results %s' % (methodName, pageObj.PagingInfo), pageObj, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            _logsi.LogDictionary(SILevel.Message, '%s Results %s (Dictionary)' % (methodName, pageObj.PagingInfo), pageObj.ToDictionary(), colorValue=SIColors.LightGreen, prettyPrint=True)
            print(str(pageObj))
            print('\nCategories in this page of results (%d items):' % pageObj.ItemsCount)

            # display category details.
            category:Category
            for category in pageObj.Items:

                _logsi.LogObject(SILevel.Message,'Category: "%s" (%s)' % (category.Name, category.Id), category, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=category.Name, uri=category.Id))
        
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetBrowseCategorysList(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetBrowseCategorysList"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Spotify client instance.
            spotify:SpotifyClient = self._CreateApiClientPublic()

            # get a sorted list of all categories used to tag items in Spotify.
            print('\nGetting list of all browse categories ...')
            categories:list[Category] = spotify.GetBrowseCategorysList()

            # display category details.
            print('\nAll Browse Categories (sorted by name - %d items):' % len(categories))
            category:Category
            for category in categories:

                _logsi.LogObject(SILevel.Message,'Category: "%s" (%s)' % (category.Name, category.Id), category, colorValue=SIColors.LightGreen, excludeNonPublic=True)
                print('- "{name}" ({uri})'.format(name=category.Name, uri=category.Id))

            # get cached configuration, refreshing from device if needed.
            categories:list[Category] = spotify.GetBrowseCategorysList(refresh=False)
            print("\nCached configuration (count): %d" % len(categories))

            # get cached configuration directly from the configuration manager dictionary.
            if "GetBrowseCategorysList" in spotify.ConfigurationCache:
                categories:list[Category] = spotify.ConfigurationCache["GetBrowseCategorysList"]
                print("\nCached configuration direct access (count): %d" % len(categories))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
