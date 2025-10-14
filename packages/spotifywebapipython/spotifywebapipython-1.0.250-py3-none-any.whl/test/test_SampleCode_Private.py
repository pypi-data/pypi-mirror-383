# external package imports.
from smartinspectpython.siauto import *

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

print("** Test Starting")

try:

    # this sample requires an authorization token, as it accesses protected data.
    # the SetAuthTokenAuthorizationCodePKCE() method must be used to establish the authorization token.

    CLIENT_ID:str = 'eab07793bc744770a706ecc68097a218'
    SPOTIFY_SCOPES:list = ['user-read-email','user-library-read','user-library-modify']

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient(tokenStorageDir='./test/testdata')

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get a list of the albums saved in the current Spotify user's 'Your Library'.
    print('\nGetting users saved albums ...\n')
    albumPage:AlbumPageSaved = spotify.GetAlbumFavorites()

    while True:

        # display paging details.
        print(str(albumPage))
        print('')

        # display album details.
        albumSaved:AlbumSaved
        for albumSaved in albumPage.Items:
        
            print(str(albumSaved))

            print('\nArtist(s):')
            for artist in albumSaved.Artists:
                print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

            print('')
         
        # anymore page results?
        if albumPage.Next is None:
            # no - all pages were processed.
            break
        else:
            # yes - retrieve the next page of results.
            print('\nGetting next page of %d items ...\n' % (albumPage.Limit))
            albumPage = spotify.GetAlbumFavorites(offset=albumPage.Offset + albumPage.Limit, limit=albumPage.Limit)

except Exception as ex:

    print("\n** Exception: %s" % str(ex))
    
finally:

    print("\n** Test Completed")

    # unwire events, and dispose of SmartInspect.
    print("** Disposing of SmartInspect resources")
    SIAuto.Si.Dispose()
