# external package imports.
from smartinspectpython.siauto import *
import time

# our package imports.
from spotifywebapipython.spotifyclient import SpotifyClient
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

    # spotify code example:
    # - https://stmorse.github.io/journal/spotify-api.html

    CLIENT_ID:str = 'eab07793bc744770a706ecc68097a218'
    CLIENT_SECRET:str = 'cc1f9b159e284a73b67689e98c5bd718'

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient(tokenStorageDir='./test/testdata')

    # generate a spotify client credentials access token.
    spotify.SetAuthTokenClientCredentials(CLIENT_ID, CLIENT_SECRET)
    
    # log authorization token and user profile info.
    _logsi.LogObject(SILevel.Verbose,'Authorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)), spotify.AuthToken, colorValue=SIColors.LightGreen, excludeNonPublic=True)
    print('\nAuthorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)))
    _logsi.LogObject(SILevel.Verbose,'User Profile Object: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
    print('\nUser Profile Object: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # Uri="spotify:artist:6APm8EjxOHSYM5B4i3vT3q" - Artist="MercyMe"
    # Uri="spotify:album:6vc9OTcyd3hyzabCmsdnwE"  - Artist="MercyMe", Album="Welcome to the New"
    # Uri="spotify:track:1kWUud3vY5ij5r62zxpTRy"  - Artist="MercyMe", Album="Welcome to the New", Track="Flawless"
   
    # loop 150 times, as we want to get as close to the token expiration as possible.
    for loopCnt in range(0, 15):
        
        # retrieve artist information.
        artist:Artist = spotify.GetArtist('6APm8EjxOHSYM5B4i3vT3q')
        _logsi.LogObject(SILevel.Verbose,'Artist Object: "%s" (%s)' % (artist.Name, artist.Id), artist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
        print('')
        print(artist)

        # wait x seconds before next attempt.
        waitSecs:int = 5
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
