import sys
sys.path.append("..")

import unittest
from testVS_SpotifyClient_Base import Test_SpotifyClient_Base

# external package imports.
from smartinspectpython.siauto import *
import logging

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *
from spotifywebapipython.const import SPOTIFY_DESKTOP_APP_CLIENT_ID

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# Spotify Authorization Token Tests.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_AuthTokens(Test_SpotifyClient_Base): 
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def test_SpotifyDesktopApp_TokenGenerator_FREE(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_SpotifyDesktopApp_TokenGenerator_FREE"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # Spotify Desktop Client only requires `streaming` scope for Spotify Connect functionality.
            SPOTIFY_SCOPES:list = \
            [
                'streaming',
                # # extra scopes used by spotify desktop player
                # 'app-remote-control',
                # 'playlist-modify',
                # 'playlist-read',
                # 'user-modify',
                # 'user-modify-private',
                # 'user-personalized',
                # 'user-read-birthdate',
                # 'user-read-play-history',
            ]
            
            # set token profile parameters.
            tokenStorageDir:str = './test/testdata'
            tokenProfileId:str = '31dutb2cjtmf7uns4jtqpmwen7iq' # Spotify Login ID (canonical format)
            redirectUriHost:str = '127.0.0.1'
            redirectUriPort:int = 4381
            redirectUriPath:str = '/login'
    
            # create new spotify client instance.
            spotify:SpotifyClient = SpotifyClient(tokenStorageDir=tokenStorageDir)

            # generate a spotify authorization code with PKCE access token.
            spotify.SetAuthTokenAuthorizationCodePKCE(
                SPOTIFY_DESKTOP_APP_CLIENT_ID, 
                SPOTIFY_SCOPES, 
                tokenProfileId=tokenProfileId, 
                redirectUriHost=redirectUriHost, 
                redirectUriPort=redirectUriPort, 
                redirectUriPath=redirectUriPath)
    
            # log authorization token.
            _logsi.LogObject(SILevel.Verbose,'Authorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)), spotify.AuthToken, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\n%s' % (spotify.AuthToken.ToString()))

            # log authorization user profile info.
            _logsi.LogObject(SILevel.Verbose,'User Profile Object: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nUser: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SpotifyDesktopApp_TokenGenerator(self):
        
        _logsi:SISession = SIAuto.Main
        methodName:str = "test_SpotifyDesktopApp_TokenGenerator"
        
        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            SPOTIFY_SCOPES:list = \
            [
                'streaming',
            ]
            
            # set token profile parameters.
            tokenStorageDir:str = './test/testdata'
            tokenProfileId:str = '31l77y2al5lnn7mxfrmd4bpfhqke' # Spotify Login ID (canonical format)
            redirectUriHost:str = '127.0.0.1'
            redirectUriPort:int = 4381
            redirectUriPath:str = '/login'
    
            # create new spotify client instance.
            spotify:SpotifyClient = SpotifyClient(tokenStorageDir=tokenStorageDir)

            # generate a spotify authorization code with PKCE access token.
            spotify.SetAuthTokenAuthorizationCodePKCE(
                SPOTIFY_DESKTOP_APP_CLIENT_ID, 
                SPOTIFY_SCOPES, 
                tokenProfileId=tokenProfileId, 
                redirectUriHost=redirectUriHost, 
                redirectUriPort=redirectUriPort, 
                redirectUriPath=redirectUriPath,
                forceAuthorize=True)
    
            # log authorization token.
            _logsi.LogObject(SILevel.Verbose,'Authorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)), spotify.AuthToken, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\n%s' % (spotify.AuthToken.ToString()))

            # log authorization user profile info.
            _logsi.LogObject(SILevel.Verbose,'User Profile Object: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nAuthorized User:')
            print(' Spotify Account="%s"' % (spotify.UserProfile.DisplayName))
            
            print('\nToken saved in the following location:')
            print('- Directory = %s' % spotify.TokenStorageDir)
            print('- File Name = %s' % spotify.TokenStorageFile)
            
            print('\nCopy the following to the SpotifyPlus token.json file:\n')
            print('SpotifyWebApiAuthCodePkce/%s/%s: ' % (spotify.ClientId, spotify.TokenProfileId))
            print(spotify.AuthToken.ToDictionaryString())

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_SpotifyDesktopApp_TokenGenerator_DESKTOP(self):
        
        _logsi:SISession = SIAuto.Main
        methodName:str = "test_SpotifyDesktopApp_TokenGenerator"
        
        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            SPOTIFY_SCOPES:list = \
            [
                'streaming',
                # extra scopes used by spotify desktop player
                'app-remote-control',
                'playlist-modify',
                'playlist-read',
                'user-modify',
                'user-modify-private',
                'user-personalized',
                'user-read-birthdate',
                'user-read-play-history',
            ]
            
            # set token profile parameters.
            tokenStorageDir:str = './test/testdata'
            tokenProfileId:str = 'testuser' # Spotify Login ID (canonical format)
            redirectUriHost:str = '127.0.0.1'
            redirectUriPort:int = 4381
            redirectUriPath:str = '/login'
    
            # create new spotify client instance.
            spotify:SpotifyClient = SpotifyClient(tokenStorageDir=tokenStorageDir)

            # generate a spotify authorization code with PKCE access token.
            spotify.SetAuthTokenAuthorizationCodePKCE(
                SPOTIFY_DESKTOP_APP_CLIENT_ID, 
                SPOTIFY_SCOPES, 
                tokenProfileId=tokenProfileId, 
                redirectUriHost=redirectUriHost, 
                redirectUriPort=redirectUriPort, 
                redirectUriPath=redirectUriPath,
                forceAuthorize=True)
    
            # log authorization token.
            _logsi.LogObject(SILevel.Verbose,'Authorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)), spotify.AuthToken, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\n%s' % (spotify.AuthToken.ToString()))

            # log authorization user profile info.
            _logsi.LogObject(SILevel.Verbose,'User Profile Object: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nAuthorized User:')
            print(' Spotify Account="%s"' % (spotify.UserProfile.DisplayName))
            
            print('\nToken saved in the following location:')
            print('- Directory = %s' % spotify.TokenStorageDir)
            print('- File Name = %s' % spotify.TokenStorageFile)
            
            print('\nCopy the following to the SpotifyPlus token.json file:\n')
            print('SpotifyWebApiAuthCodePkce/%s/%s: ' % (spotify.ClientId, spotify.TokenProfileId))
            print(spotify.AuthToken.ToDictionaryString())

            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
