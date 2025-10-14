# external package imports.
from smartinspectpython.siauto import *
import time

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.models import *

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

print("** Test Starting\n")

try:

    #CLIENT_ID_BOSE = '79ebcb219e8e4e9a892e796607931810'

    CLIENT_ID:str = 'eab07793bc744770a706ecc68097a218'
    SPOTIFY_SCOPES:list = \
    [
        'playlist-modify-private',
        'playlist-modify-public',
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

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient(tokenStorageDir='./test/testdata')

    # generate a spotify authorization code with PKCE access token.
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    
    # log authorization token and user profile info.
    _logsi.LogObject(SILevel.Verbose,'Authorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)), spotify.AuthToken, colorValue=SIColors.LightGreen, excludeNonPublic=True)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    _logsi.LogObject(SILevel.Verbose,'User Profile: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # loop 150 times, as we want to get as close to the token expiration as possible.
    for loopCnt in range(0, 150):
        
        # get all tracks played within the past 1 hour.
        afterMS:int = GetUnixTimestampMSFromUtcNow(hours=-1)

        # get tracks from current user's recently played tracks.
        print('\nGetting recently played tracks for current user ...\n')
        pageObj:PlayHistoryPage = spotify.GetPlayerRecentTracks(after=afterMS, limit=50)

        # display paging details.
        print(str(pageObj))
        print('')
        print('Tracks in this page of results:')
                
        # display history details.
        history:PlayHistory
        for history in pageObj.Items:
        
            _logsi.LogObject(SILevel.Verbose,'Track: %s %s - "%s" (%s)' % (history.PlayedAt, history.PlayedAtMS, history.Track.Name, history.Track.Uri), history.Track, colorValue=SIColors.LightGreen, excludeNonPublic=True)
            print('- {played_at} {played_atMS}: "{name}" ({uri})'.format(played_at=history.PlayedAt, played_atMS=history.PlayedAtMS, name=history.Track.Name, uri=history.Track.Uri))

        # wait x seconds before next attempt.
        waitSecs:int = 60
        _logsi.LogVerbose('Waiting %d seconds for next attempt ...' % waitSecs, colorValue=SIColors.LightGreen)
        print('\nWaiting %d seconds for next attempt ...' % waitSecs)
        time.sleep(waitSecs)
        
except Exception as ex:

    print("\n** Exception: %s" % str(ex))
    
finally:

    print("\n** Test Completed")

    # unwire events, and dispose of SmartInspect.
    print("** Disposing of SmartInspect resources")
    SIAuto.Si.Dispose()
