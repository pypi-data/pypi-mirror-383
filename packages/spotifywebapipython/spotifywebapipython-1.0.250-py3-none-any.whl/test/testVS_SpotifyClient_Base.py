import os
import sys
sys.path.append("..")

import time
import unittest

# external package imports.
from smartinspectpython.siauto import *
from xml.etree.ElementTree import Element

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.models import *

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# SpotifyClient Tests - base class from which all client tests inherit from.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_SpotifyClient_Base(unittest.TestCase):
    """
    Test client scenarios.
    """

    @classmethod
    def setUpClass(cls):
        
        try:

            #print("*******************************************************************************")
            #print("** unittest.TestCase - setUpClass() Started")

            # load SmartInspect settings from a configuration settings file.
            print("** Loading SmartInspect configuration settings")
            siConfigPath:str = "./test/smartinspect.cfg"
            SIAuto.Si.LoadConfiguration(siConfigPath)

            # start monitoring the configuration file for changes, and reload it when it changes.
            # this will check the file for changes every 60 seconds.
            print("** Starting SmartInspect configuration settings watchdog")
            siConfig:SIConfigurationTimer = SIConfigurationTimer(SIAuto.Si, siConfigPath)

            # get smartinspect logger reference and log basic system / domain details.
            _logsi:SISession = SIAuto.Main            
            _logsi.LogSeparator(SILevel.Fatal, colorValue=SIColors.LightGreen)
            _logsi.LogAppDomain(SILevel.Message, colorValue=SIColors.LightGreen)
            _logsi.LogSystem(SILevel.Message, colorValue=SIColors.LightGreen)

            print("** Current Work Dir: %s" % os.getcwd())
            

        except Exception as ex:

            print("\n** unittest.TestCase - Exception in setUpClass() method!\n" + str(ex))
            raise

        finally:

            pass
            #print("** unittest.TestCase - setUpClass() Complete")
            #print("*******************************************************************************")

    
    @classmethod
    def tearDownClass(cls):
        
        try:

            #print("*******************************************************************************")
            #print("** unittest.TestCase - tearDownClass() Started")

            # unwire events, and dispose of SmartInspect.
            #print("** Disposing of SmartInspect resources")
            SIAuto.Si.Dispose()
            
        except Exception as ex:

            print("\n** unittest.TestCase - Exception in tearDownClass() method!\n" + str(ex))
            raise

        finally:

            pass
            #print("** unittest.TestCase - tearDownClass() Complete")
            #print("*******************************************************************************")
                    
    
    def setUp(self):
        
        try:

            pass
            #print("*******************************************************************************")
            #print("** unittest.TestCase - setUp() Started")

            # nothing to do here.
            
        except Exception as ex:

            print("\n** unittest.TestCase - Exception in setUp() method!\n" + str(ex))
            raise

        finally:

            pass
            # print("** unittest.TestCase - setUp() Complete")
            # print("*******************************************************************************")

    
    def tearDown(self):
        
        try:

            # print("*******************************************************************************")
            # print("** unittest.TestCase - tearDown() Started")

            # nothing to do here.
            pass
            
        except Exception as ex:

            print("\n** unittest.TestCase - Exception in tearDown() method!\n" + str(ex))
            raise

        finally:

            # print("** unittest.TestCase - tearDown() Complete")
            # print("*******************************************************************************")
            pass
                    
    
    def _CreateApiClientUser(self) -> SpotifyClient:
        """
        Creates a new SpotifyClient instance that can access user details, and sets all properties for executing these test cases.

        Returns:
            An SpotifyClient instance.
        """
        _logsi:SISession = SIAuto.Main            

        try:

            # The following Player services are NOT permitted with a FREE account.
            # - AddPlayerQueueItem
            # - GetPlayerQueueInfo
            # - PlayerMediaPause
            # - PlayerMediaPlayContext
            # - PlayerMediaPlayTracks
            # - PlayerMediaResume
            # - PlayerMediaSeek
            # - PlayerMediaSkipNext
            # - PlayerMediaSkipPrevious
            # - PlayerSetRepeatMode
            # - PlayerSetShuffleMode
            # - PlayerSetVolume
            # - PlayerTransferPlayback

            CLIENT_ID:str = 'eab07793bc744770a706ecc68097a218'  # PREMIUM Account (thlucas2010@gmail.com)
            #CLIENT_ID:str = 'fd8d567505e742e5b576aa63aa5dc0c9'  # FREE Account (todd.lucas@cox.net)
            SPOTIFY_SCOPES:list = \
            [
                'playlist-modify-private',
                'playlist-modify-public',
                'playlist-read-collaborative',
                'playlist-read-private',
                'streaming',
                'ugc-image-upload',
                'user-follow-modify',
                'user-follow-read',
                'user-library-modify',
                'user-library-read',
                'user-modify-playback-state',
                'user-read-currently-playing',
                'user-read-email',
                'user-read-playback-position',
                'user-read-playback-state',
                'user-read-private',
                'user-read-recently-played',
                'user-top-read',
                # extra scopes used by spotify desktop player
                # 'app-remote-control',
                # 'playlist-modify',
                # 'playlist-read',
                # 'user-modify',
                # 'user-modify-private',
                # 'user-personalized',
                # 'user-read-birthdate',
                # 'user-read-play-history',
            ]
            
            spotifyConnectDirectoryEnabled:bool = False     # disable zeroconf directory browsing completely
            spotifyConnectDiscoveryTimeout:float = 0        # disable zeroconf directory browsing for Spotify Connect devices

            # create new spotify client instance.
            # disable zeroconf discovery for this client, as it does not use Spotify Connect features.
            spotify:SpotifyClient = SpotifyClient(
                tokenStorageDir='./test/testdata', 
                spotifyConnectDiscoveryTimeout=spotifyConnectDiscoveryTimeout,
                spotifyConnectDirectoryEnabled=spotifyConnectDirectoryEnabled,
                )

            # generate a spotify authorization code with PKCE access token.
            spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)

            # log authorization token info.
            _logsi.LogObject(SILevel.Message,'Authorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
            #print(spotify.AuthToken.ToString())

            # log user profile info.
            _logsi.LogObject(SILevel.Message,'User Profile: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))
                       
            # return instance to caller.
            return spotify

        except Exception as ex:

            _logsi.LogException("Exception in Test Method \"{0}\"".format(SISession.GetMethodName()), ex)
            print("** Exception: %s" % str(ex))
            raise


    def _CreateApiClientUser_PREMIUM(self) -> SpotifyClient:
        """
        Creates a new SpotifyClient instance that can access user details, and sets all properties for executing these test cases.

        Returns:
            An SpotifyClient instance.
        """
        _logsi:SISession = SIAuto.Main            

        try:

            # PREMIUM Account: thlucas2010@gmail.com
            # - Client ID     = eab07793bc744770a706ecc68097a218
            # - Client Secret = cc1f9b159e284a73b67689e98c5bd718

            CLIENT_ID:str = 'eab07793bc744770a706ecc68097a218'
            SPOTIFY_SCOPES:list = \
            [
                'playlist-modify-private',
                'playlist-modify-public',
                'playlist-read-collaborative',
                'playlist-read-private',
                'streaming',
                'ugc-image-upload',
                'user-follow-modify',
                'user-follow-read',
                'user-library-modify',
                'user-library-read',
                'user-modify-playback-state',
                'user-read-currently-playing',
                'user-read-email',
                'user-read-playback-position',
                'user-read-playback-state',
                'user-read-private',
                'user-read-recently-played',
                'user-top-read',
                # extra scopes used by spotify desktop player
                # 'app-remote-control',
                # 'playlist-modify',
                # 'playlist-read',
                # 'user-modify',
                # 'user-modify-private',
                # 'user-personalized',
                # 'user-read-birthdate',
                # 'user-read-play-history',
            ]

            # Spotify Connect credentials and timeout:
            spotifyConnectUsername:str = 'thlucas2010@gmail.com'
            spotifyConnectPassword:str = 'Crazy$1spot'
            spotifyConnectLoginId:str  = '31l77y2al5lnn7mxfrmd4bpfhqke'
            # spotifyWebPlayerCookieSpdc:str = "AQD_SXyRWnWC2UbmTzKvbCl_vZyGaZPKF7p2ZJxXwRqjYDy5rlEgzeE5VFR-PjfWQUy8xckJDUvDRLpOgsuXfozFzi7ITAQpzLPuHM2-Qu_MvM3CmePEPE2RpR08xfuIu1OwBfDMWbZmdygERSComzn_w9hRAblzj9YxuULB50cDqD-YaGuPCDr3f5UfK4HlLwoLxvhane5Lgz5eLw"
            # spotifyWebPlayerCookieSpkey:str = "2a1cf00a-a2b6-4c53-a671-03121e9dc6ac"
            spotifyConnectDiscoveryTimeout:float = 15.0  # seconds

            # create new spotify client instance.
            spotify:SpotifyClient = SpotifyClient(
                tokenStorageDir='./test/testdata', 
                spotifyConnectUsername=spotifyConnectUsername, 
                spotifyConnectPassword=spotifyConnectPassword, 
                spotifyConnectLoginId=spotifyConnectLoginId,
                spotifyConnectDiscoveryTimeout=spotifyConnectDiscoveryTimeout,
                # spotifyWebPlayerCookieSpdc=spotifyWebPlayerCookieSpdc,
                # spotifyWebPlayerCookieSpkey=spotifyWebPlayerCookieSpkey,
                )

            # generate a spotify authorization code with PKCE access token.
            spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)

            # log authorization token info.
            _logsi.LogObject(SILevel.Message,'Authorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
            #print(spotify.AuthToken.ToString())

            # log user profile info.
            _logsi.LogObject(SILevel.Message,'User Profile: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

            # return instance to caller.
            return spotify

        except Exception as ex:

            _logsi.LogException("Exception in Test Method \"{0}\"".format(SISession.GetMethodName()), ex)
            print("** Exception: %s" % str(ex))
            raise


    def _CreateApiClientUser_PREMIUM_NoDiscovery(self) -> SpotifyClient:
        """
        Creates a new SpotifyClient instance that can access user details, and sets all properties for executing these test cases.

        Turns off SpotifyConnect device discovery so that time is not wasted waiting for devices.

        Use this for testing functionality that does not require devices.

        Returns:
            An SpotifyClient instance.
        """
        _logsi:SISession = SIAuto.Main            

        try:

            # PREMIUM Account: thlucas2010@gmail.com
            # - Client ID     = eab07793bc744770a706ecc68097a218
            # - Client Secret = cc1f9b159e284a73b67689e98c5bd718

            CLIENT_ID:str = 'eab07793bc744770a706ecc68097a218'
            SPOTIFY_SCOPES:list = \
            [
                'playlist-modify-private',
                'playlist-modify-public',
                'playlist-read-collaborative',
                'playlist-read-private',
                'streaming',
                'ugc-image-upload',
                'user-follow-modify',
                'user-follow-read',
                'user-library-modify',
                'user-library-read',
                'user-modify-playback-state',
                'user-read-currently-playing',
                'user-read-email',
                'user-read-playback-position',
                'user-read-playback-state',
                'user-read-private',
                'user-read-recently-played',
                'user-top-read',
                # extra scopes used by spotify desktop player
                # 'app-remote-control',
                # 'playlist-modify',
                # 'playlist-read',
                # 'user-modify',
                # 'user-modify-private',
                # 'user-personalized',
                # 'user-read-birthdate',
                # 'user-read-play-history',
            ]

            # Spotify Connect credentials and timeout:
            spotifyConnectUsername:str = 'thlucas2010@gmail.com'
            spotifyConnectPassword:str = 'Crazy$1spot'
            spotifyConnectLoginId:str  = '31l77y2al5lnn7mxfrmd4bpfhqke'
            spotifyConnectDiscoveryTimeout:float = 0  # seconds
            spotifyConnectDirectoryEnabled:bool = False

            # create new spotify client instance.
            spotify:SpotifyClient = SpotifyClient(
                tokenStorageDir='./test/testdata', 
                spotifyConnectUsername=spotifyConnectUsername, 
                spotifyConnectPassword=spotifyConnectPassword, 
                spotifyConnectLoginId=spotifyConnectLoginId,
                spotifyConnectDiscoveryTimeout=spotifyConnectDiscoveryTimeout,
                spotifyConnectDirectoryEnabled=spotifyConnectDirectoryEnabled
                )

            # generate a spotify authorization code with PKCE access token.
            spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)

            # log authorization token info.
            _logsi.LogObject(SILevel.Message,'Authorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
            #print(spotify.AuthToken.ToString())

            # log user profile info.
            _logsi.LogObject(SILevel.Message,'User Profile: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

            # return instance to caller.
            return spotify

        except Exception as ex:

            _logsi.LogException("Exception in Test Method \"{0}\"".format(SISession.GetMethodName()), ex)
            print("** Exception: %s" % str(ex))
            raise


    def _CreateApiClientUser_FREE(self) -> SpotifyClient:
        """
        Creates a new SpotifyClient instance that can access user details, and sets all properties for executing these test cases.

        Returns:
            An SpotifyClient instance.
        """
        _logsi:SISession = SIAuto.Main            

        try:

            # FREE Account: todd.lucas@cox.net
            # - Client ID = fd8d567505e742e5b576aa63aa5dc0c9
            # - Client Secret = 65f2ffb50d37488d917e4925b8076833

            CLIENT_ID:str = 'fd8d567505e742e5b576aa63aa5dc0c9'
            SPOTIFY_SCOPES:list = \
            [
                'playlist-modify-private',
                'playlist-modify-public',
                'playlist-read-collaborative',
                'playlist-read-private',
                'streaming',
                'ugc-image-upload',
                'user-follow-modify',
                'user-follow-read',
                'user-library-modify',
                'user-library-read',
                'user-modify-playback-state',
                'user-read-currently-playing',
                'user-read-email',
                'user-read-playback-position',
                'user-read-playback-state',
                'user-read-private',
                'user-read-recently-played',
                'user-top-read',
                # extra scopes used by spotify desktop player
                # 'app-remote-control',
                # 'playlist-modify',
                # 'playlist-read',
                # 'user-modify',
                # 'user-modify-private',
                # 'user-personalized',
                # 'user-read-birthdate',
                # 'user-read-play-history',
            ]

            # Spotify Connect credentials and timeout:
            spotifyConnectUsername:str = 'todd.lucas@cox.net'
            spotifyConnectPassword:str = 'Thlucas$1spot'
            spotifyConnectLoginId:str  = '31dutb2cjtmf7uns4jtqpmwen7iq'
            spotifyConnectDiscoveryTimeout:float = 3.0  # 3 seconds

            # create new spotify client instance.
            spotify:SpotifyClient = SpotifyClient(
                tokenStorageDir='./test/testdata', 
                spotifyConnectUsername=spotifyConnectUsername, 
                spotifyConnectPassword=spotifyConnectPassword, 
                spotifyConnectLoginId=spotifyConnectLoginId,
                spotifyConnectDiscoveryTimeout=spotifyConnectDiscoveryTimeout
                )

            # generate a spotify authorization code with PKCE access token.
            spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)

            # log authorization token info.
            _logsi.LogObject(SILevel.Message,'Authorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
            #print(spotify.AuthToken.ToString())

            # log user profile info.
            _logsi.LogObject(SILevel.Message,'User Profile: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))
                       
            # return instance to caller.
            return spotify

        except Exception as ex:

            _logsi.LogException("Exception in Test Method \"{0}\"".format(SISession.GetMethodName()), ex)
            print("** Exception: %s" % str(ex))
            raise


    def _CreateApiClientPublic(self) -> SpotifyClient:
        """
        Creates a new SpotifyClient instance that will access public data, 
        and sets all properties for executing these test cases.

        Returns:
            An SpotifyClient instance.
        """
        _logsi:SISession = SIAuto.Main            

        try:

            CLIENT_ID:str = 'eab07793bc744770a706ecc68097a218'
            CLIENT_SECRET:str = 'cc1f9b159e284a73b67689e98c5bd718'

            # create new spotify client instance.
            spotify:SpotifyClient = SpotifyClient(tokenStorageDir='./test/testdata')

            # generate a spotify client credentials access token.
            spotify.SetAuthTokenClientCredentials(CLIENT_ID, CLIENT_SECRET)

            # log authorization token info.
            _logsi.LogObject(SILevel.Message,'Authorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))

            # log user profile info.
            _logsi.LogObject(SILevel.Message,'User Profile: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))
                       
            # return instance to caller.
            return spotify

        except Exception as ex:

            _logsi.LogException("Exception in Test Method \"{0}\"".format(SISession.GetMethodName()), ex)
            print("** Exception: %s" % str(ex))
            raise


# execute unit tests.
if __name__ == '__main__':
    unittest.main()
