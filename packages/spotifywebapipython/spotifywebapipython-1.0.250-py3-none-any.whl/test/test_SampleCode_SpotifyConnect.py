# external package imports.
from smartinspectpython.siauto import *

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.models import *
#from spotifywebapipython.spotifyconnect import *

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
_logsi.LogSeparator(SILevel.Fatal)
_logsi.LogAppDomain(SILevel.Message)
_logsi.LogSystem(SILevel.Message)

print("** Test Starting")

try:

    # this sample requires an authorization token, as it accesses protected data.
    # the SetAuthTokenAuthorizationCodePKCE() method must be used to establish the authorization token.

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
    ]

    # Spotify Connect credentials and timeout:
    spotifyConnectUsername:str = 'thlucas2010@gmail.com'
    spotifyConnectPassword:str = 'Crazy$1spot'
    spotifyConnectLoginId:str  = '31l77y2al5lnn7mxfrmd4bpfhqke'
    spotifyConnectDiscoveryTimeout:float = 4.0  # seconds

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

    # log user profile info.
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # if using for SampleCode testing, then code starts after this line.

    # get active device info.
    print('\nGetting active player device ...\n')
    scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetActiveDevice()

    if scDevice is not None:
        print(str(scDevice))
    else:
        print("No active device")

except Exception as ex:

    print("\n** Exception: %s" % str(ex))
    
finally:

    print("\n** Test Completed")

    # stop Spotify Connect Directory task.
    if (spotify is not None):
        spotify.StopSpotifyConnectDirectoryTask()

    # unwire events, and dispose of SmartInspect.
    print("** Disposing of SmartInspect resources")
    SIAuto.Si.Dispose()
