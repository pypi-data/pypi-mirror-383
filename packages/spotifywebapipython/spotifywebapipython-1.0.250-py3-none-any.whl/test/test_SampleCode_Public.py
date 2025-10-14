# external package imports.
from smartinspectpython.siauto import *

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *

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

import logging
logging.basicConfig(level=logging.WARN)

print("** Test Starting")

try:

    CLIENT_ID:str = 'eab07793bc744770a706ecc68097a218'
    CLIENT_SECRET:str = 'cc1f9b159e284a73b67689e98c5bd718'

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient(tokenStorageDir='./test/testdata')

    # # generate a spotify client credentials access token (no scope, public data use only).
    # spotify.SetAuthTokenClientCredentials(CLIENT_ID, CLIENT_SECRET)
    # print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    # print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get Spotify zeroconf api action "resetUsers" response.
    actionUrl:str = 'http://192.168.1.82:8200/zc?action=resetUsers&VERSION=1.0'
    print('\nGetting Spotify zeroconf resetUsers response:\n- "%s" ...\n' % actionUrl)
    zcfResponse:ZeroconfResponse = spotify.ZeroconfResetUsers(actionUrl)
            
    print(zcfResponse.ToString())

except Exception as ex:

    print("\n** Exception: %s" % str(ex))
    
finally:

    print("\n** Test Completed")

    # unwire events, and dispose of SmartInspect.
    print("** Disposing of SmartInspect resources")
    SIAuto.Si.Dispose()
