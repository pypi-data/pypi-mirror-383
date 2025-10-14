# external package imports.
from requests_oauthlib import OAuth2Session
from smartinspectpython.siauto import *

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

def TokenUpdater() -> dict:
    _logsi.LogCurrentStackTrace(SILevel.Verbose, 'TokenUpdater - Current Stack Trace', colorValue=SIColors.DarkBlue)
    
    UPDATED_TOKEN:dict = {
        'access_token': 'BQAJFP4neZySkGccp3UIjQG7j6lKhHXv1yupz48WATUdBaoa7bMWGu38TUfW92PqW6ZVVHK74QylZO3lHlyh62INesQI_DYf9R5oE8A98eCUblzDQx38o38EXVj5EhcguE4T5kL28yi9aDLnNLSol7SRs4iUVKbvF-8TZdBRY2QXam7gI81MbfVwTMZ9kpLFHijs7LZCnNoqTcKkOXJOLMV3vZeAvEOtazRABCzoSvBcCP7PwDXi95D8q0mYvs4nHNf8-ROYPLWnYIZECOCikAFMP88GwCUqunWAOtBH7p3wYuSnS6DRCvjdXX2chrm6vblrz30rUMs59ZQ',
        'expires_in': 3600,
        'refresh_token': 'AQBVAv8UKnMYTVtFdS_uTFzaM_QRqN5f3lVLwKf-H5hHwSFp0467RgsbgjSakqyzjCKxb6ssAEZSAdWk_1hbE2OUyx7_27ieVEIu0FNJpgDA-0pLg2R9TP4Quq8aznzCnRA',
        'expires_at': 1707148646.4159575,
        "scope": [
            "playlist-read-private",
            "playlist-read-collaborative",
            "ugc-image-upload",
            "user-follow-read",
            "playlist-modify-private",
            "user-read-email",
            "user-read-private",
            "user-follow-modify",
            "user-modify-playback-state",
            "user-library-read",
            "user-library-modify",
            "playlist-modify-public",
            "user-read-playback-state",
            "user-read-currently-playing",
            "user-read-recently-played",
            "user-read-playback-position",
            "user-top-read"
        ],
        "token_type": "Bearer",
        'status': 'token_updater token'
    }

    return UPDATED_TOKEN

try:

    CLIENT_ID:str = 'eab07793bc744770a706ecc68097a218'
    CLIENT_SECRET:str = 'cc1f9b159e284a73b67689e98c5bd718'
    SPOTIFY_SCOPES:list = \
    [
        'playlist-modify-private',
        'playlist-modify-public',
        'playlist-read-collaborative',
        'playlist-read-private',
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

    TOKEN:dict = {
        'access_token': 'BQCylDIef4JiH_9_mnwA3ZpGv1qGS5la-TTH25fZCCZ0qv1pp9ugV_lXXJPjKsJ8rTA2toJDONyfMiS5B2wiH9iZ-DBNN-1Bo6q214lggXS72la81bYLqlI0-JV65sPf6aPxPp9us2iY36Haq_ZI4tpnQytUH097QfKqwT3sJtz2GvfZPyGpvuXrYn4SZ0YAOUtro0_LZZnxI6_-cgB8JvDi9rKT_ymkpze-U6r3dgfha5fP92xJheuJXePDioI9E1Xt26bxELztNfFXUp4whjhekO-lX0bhE-N_M4FmCoE3Fh_jiB8Zrnt-hDOpoNwVVwmx_Bxjj0BJDLA',
        'expires_in': 3600,
        'refresh_token': 'AQBVAv8UKnMYTVtFdS_uTFzaM_QRqN5f3lVLwKf-H5hHwSFp0467RgsbgjSakqyzjCKxb6ssAEZSAdWk_1hbE2OUyx7_27ieVEIu0FNJpgDA-0pLg2R9TP4Quq8aznzCnRA',
        'expires_at': 1707141014.3164904,
        "scope": [
            "playlist-read-private",
            "playlist-read-collaborative",
            "ugc-image-upload",
            "user-follow-read",
            "playlist-modify-private",
            "user-read-email",
            "user-read-private",
            "user-follow-modify",
            "user-modify-playback-state",
            "user-library-read",
            "user-library-modify",
            "playlist-modify-public",
            "user-read-playback-state",
            "user-read-currently-playing",
            "user-read-recently-played",
            "user-read-playback-position",
            "user-top-read"
        ],
        "token_type": "Bearer"
    }

    # create a new oauth2session.
    REDIRECT_URI:str = 'http://127.0.0.1/'

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient(tokenStorageDir='./test/testdata', tokenUpdater=TokenUpdater)

    # generate a spotify authorization code access token.
    spotify.SetAuthTokenFromToken(CLIENT_ID, TOKEN, 'thlucas2010@gmail.com')
    
    # log authorization token and user profile info.
    _logsi.LogObject(SILevel.Verbose,'Authorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)), spotify.AuthToken, colorValue=SIColors.LightGreen, excludeNonPublic=True)
    print('\nAuthorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)))
    _logsi.LogObject(SILevel.Verbose,'User Profile Object: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
    print('\nUser Profile Object: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # Uri="spotify:artist:6APm8EjxOHSYM5B4i3vT3q" - Artist="MercyMe"
    # Uri="spotify:album:6vc9OTcyd3hyzabCmsdnwE"  - Artist="MercyMe", Album="Welcome to the New"
    # Uri="spotify:track:1kWUud3vY5ij5r62zxpTRy"  - Artist="MercyMe", Album="Welcome to the New", Track="Flawless"

    # retrieve artist information.
    artist:Artist = spotify.GetArtist('6APm8EjxOHSYM5B4i3vT3q')
    _logsi.LogObject(SILevel.Verbose,'Artist Object: "%s" (%s)' % (artist.Name, artist.Id), artist, colorValue=SIColors.LightGreen, excludeNonPublic=True)
    print('')
    print(artist)

    # retrieve user albums information (requires scope: 'user-library-read').
    albumPage:AlbumPageSaved = spotify.GetAlbumFavorites()
    _logsi.LogObject(SILevel.Verbose,'AlbumPageSaved Object: %s items (%s)' % (len(albumPage.Items), albumPage.Href), albumPage, colorValue=SIColors.LightGreen, excludeNonPublic=True)
    print('')
    print(albumPage)

except Exception as ex:

    print("\n** Exception: %s" % str(ex))
    
finally:

    print("\n** Test Completed")

    # unwire events, and dispose of SmartInspect.
    print("** Disposing of SmartInspect resources")
    SIAuto.Si.Dispose()
    