# external package imports.
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

try:

    CLIENT_ID:str = 'eab07793bc744770a706ecc68097a218'
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

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient(tokenStorageDir='./test/testdata')

    # generate a spotify authorization code with PKCE access token.
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES, tokenProfileId='thlucas2010@gmail.com')
    
    # log authorization token and user profile info.
    _logsi.LogObject(SILevel.Verbose,'Authorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)), spotify.AuthToken, colorValue=SIColors.LightGreen, excludeNonPublic=True)
    print('\nAuthorization Token: Type="%s", Profile="%s", Scope="%s"' % (spotify.AuthToken.AuthorizationType, spotify.AuthToken.ProfileId, str(spotify.AuthToken.Scope)))
    _logsi.LogObject(SILevel.Verbose,'User Profile Object: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail), spotify.UserProfile, colorValue=SIColors.LightGreen, excludeNonPublic=True)
    print('\nUser Profile Object: DisplayName="%s", EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # test ToDictionary() method - Miscellaneous.
    oDict:AudioFeatures = AudioFeatures()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - AudioFeatures", oDict.ToDictionary(), prettyPrint=True)
    oDict:Author = Author()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Author", oDict.ToDictionary(), prettyPrint=True)
    oDict:Category = Category()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Category", oDict.ToDictionary(), prettyPrint=True)
    oDict:CategoryPage = CategoryPage()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - CategoryPage", oDict.ToDictionary(), prettyPrint=True)
    oDict:Context = Context()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Context", oDict.ToDictionary(), prettyPrint=True)
    oDict:Copyright = Copyright()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Copyright", oDict.ToDictionary(), prettyPrint=True)
    oDict:Device = Device()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Device", oDict.ToDictionary(), prettyPrint=True)
    oDict:ExplicitContent = ExplicitContent()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ExplicitContent", oDict.ToDictionary(), prettyPrint=True)
    oDict:ExternalIds = ExternalIds()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ExternalIds", oDict.ToDictionary(), prettyPrint=True)
    oDict:ExternalUrls = ExternalUrls()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ExternalUrls", oDict.ToDictionary(), prettyPrint=True)
    oDict:Followers = Followers()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Followers", oDict.ToDictionary(), prettyPrint=True)
    oDict:ImageObject = ImageObject()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ImageObject", oDict.ToDictionary(), prettyPrint=True)
    oDict:Narrator = Narrator()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Narrator", oDict.ToDictionary(), prettyPrint=True)
    oDict:Owner = Owner()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Owner", oDict.ToDictionary(), prettyPrint=True)
    oDict:PageObject = PageObject()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - PageObject", oDict.ToDictionary(), prettyPrint=True)
    oDict:RecommendationSeed = RecommendationSeed()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - RecommendationSeed", oDict.ToDictionary(), prettyPrint=True)
    oDict:Restrictions = Restrictions()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Restrictions", oDict.ToDictionary(), prettyPrint=True)
    oDict:ResumePoint = ResumePoint()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ResumePoint", oDict.ToDictionary(), prettyPrint=True)

    # test ToDictionary() method - Album.
    oDict:Album = Album()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Album", oDict.ToDictionary(), prettyPrint=True)
    oDict:AlbumSimplified = AlbumSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - AlbumSimplified", oDict.ToDictionary(), prettyPrint=True)
    oDict:AlbumPageSaved = AlbumPageSaved()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - AlbumPageSaved", oDict.ToDictionary(), prettyPrint=True)
    oDict:AlbumSaved = AlbumSaved()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - AlbumSaved", oDict.ToDictionary(), prettyPrint=True)
    oDict:AlbumPageSimplified = AlbumPageSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - AlbumPageSimplified", oDict.ToDictionary(), prettyPrint=True)

    # test ToDictionary() method - Artist.
    oDict:Artist = Artist()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Artist", oDict.ToDictionary(), prettyPrint=True)
    oDict:ArtistSimplified = ArtistSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ArtistSimplified", oDict.ToDictionary(), prettyPrint=True)
    oDict:ArtistPage = ArtistPage()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ArtistPage", oDict.ToDictionary(), prettyPrint=True)
    
    # test ToDictionary() method - Audiobook.
    oDict:Audiobook = Audiobook(root={'name':'Audiobook Name'})
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Audiobook", oDict.ToDictionary(), prettyPrint=True)
    oDict:AudiobookSimplified = AudiobookSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - AudiobookSimplified", oDict.ToDictionary(), prettyPrint=True)
    oDict:AudiobookPageSimplified = AudiobookPageSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - AudiobookPageSimplified", oDict.ToDictionary(), prettyPrint=True)

    # test ToDictionary() method - Chapter.
    oDict:Chapter = Chapter(root={'audiobook':{'name':'Audiobook name'}})
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Chapter", oDict.ToDictionary(), prettyPrint=True)
    oDict:ChapterSimplified = ChapterSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ChapterSimplified", oDict.ToDictionary(), prettyPrint=True)
    oDict:ChapterPageSimplified = ChapterPageSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ChapterPageSimplified", oDict.ToDictionary(), prettyPrint=True)
    
    # test ToDictionary() method - Episode.
    oDict:Episode = Episode(root={'show':{'name':'Audiobook name'}})
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Episode", oDict.ToDictionary(), prettyPrint=True)
    oDict:EpisodeSimplified = EpisodeSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - EpisodeSimplified", oDict.ToDictionary(), prettyPrint=True)
    oDict:EpisodePageSaved = EpisodePageSaved()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - EpisodePageSaved", oDict.ToDictionary(), prettyPrint=True)
    oDict:EpisodeSaved = EpisodeSaved()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - EpisodeSaved", oDict.ToDictionary(), prettyPrint=True)
    oDict:EpisodePageSimplified = EpisodePageSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - EpisodePageSimplified", oDict.ToDictionary(), prettyPrint=True)

    # test ToDictionary() method - PlayerActions.
    oDict:PlayerActions = PlayerActions()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - PlayerActions", oDict.ToDictionary(), prettyPrint=True)
    oDict:PlayerPlayState = PlayerPlayState()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - PlayerPlayState", oDict.ToDictionary(), prettyPrint=True)
    oDict:PlayerQueueInfo = PlayerQueueInfo()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - PlayerQueueInfo", oDict.ToDictionary(), prettyPrint=True)
    oDict:PlayHistory = PlayHistory()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - PlayHistory", oDict.ToDictionary(), prettyPrint=True)
    oDict:PlayHistoryPage = PlayHistoryPage()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - PlayHistoryPage", oDict.ToDictionary(), prettyPrint=True)

    # test ToDictionary() method - Playlist.
    oDict:Playlist = Playlist()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Playlist", oDict.ToDictionary(), prettyPrint=True)
    oDict:PlaylistSimplified = PlaylistSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - PlaylistSimplified", oDict.ToDictionary(), prettyPrint=True)
    oDict:PlaylistPage = PlaylistPage()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - PlaylistPage", oDict.ToDictionary(), prettyPrint=True)
    oDict:PlaylistPageSimplified = PlaylistPageSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - PlaylistPageSimplified", oDict.ToDictionary(), prettyPrint=True)
    oDict:PlaylistTrack = PlaylistTrack()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - PlaylistTrack", oDict.ToDictionary(), prettyPrint=True)
    oDict:PlaylistTrackSummary = PlaylistTrackSummary()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - PlaylistTrackSummary", oDict.ToDictionary(), prettyPrint=True)

    # test ToDictionary() method - SearchResponse.
    oDict:SearchResponse = SearchResponse('criteria value', 'album,track,playlist')
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - SearchResponse", oDict.ToDictionary(), prettyPrint=True)

    # test ToDictionary() method - Show.
    oDict:Show = Show()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Show", oDict.ToDictionary(), prettyPrint=True)
    oDict:ShowSimplified = ShowSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ShowSimplified", oDict.ToDictionary(), prettyPrint=True)
    oDict:ShowPageSaved = ShowPageSaved()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ShowPageSaved", oDict.ToDictionary(), prettyPrint=True)
    oDict:ShowSaved = ShowSaved()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ShowSaved", oDict.ToDictionary(), prettyPrint=True)
    oDict:ShowPageSimplified = ShowPageSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - ShowPageSimplified", oDict.ToDictionary(), prettyPrint=True)

    # test ToDictionary() method - Track.
    oDict:Track = Track()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - Track", oDict.ToDictionary(), prettyPrint=True)
    oDict:TrackSimplified = TrackSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - TrackSimplified", oDict.ToDictionary(), prettyPrint=True)
    oDict:TrackPage = TrackPage()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - TrackPage", oDict.ToDictionary(), prettyPrint=True)
    oDict:TrackPageSaved = TrackPageSaved()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - TrackPageSaved", oDict.ToDictionary(), prettyPrint=True)
    oDict:TrackSaved = TrackSaved()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - TrackSaved", oDict.ToDictionary(), prettyPrint=True)
    oDict:TrackPageSimplified = TrackPageSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - TrackPageSimplified", oDict.ToDictionary(), prettyPrint=True)
    oDict:TrackRecommendations = TrackRecommendations()
    _logsi.LogDictionary(SILevel.Verbose, "ToDictionary test - TrackRecommendations", oDict.ToDictionary(), prettyPrint=True)

    # test ToDictionary() method - UserProfile.
    oDict:UserProfile = UserProfile()
    _logsi.LogDictionary(SILevel.Verbose, "UserProfile test - Episode", oDict.ToDictionary(), prettyPrint=True)
    oDict:UserProfileSimplified = UserProfileSimplified()
    _logsi.LogDictionary(SILevel.Verbose, "UserProfileSimplified test - Episode", oDict.ToDictionary(), prettyPrint=True)

except Exception as ex:

    print("\n** Exception: %s" % str(ex))
    raise
    
finally:

    print("\n** Test Completed")

    # unwire events, and dispose of SmartInspect.
    print("** Disposing of SmartInspect resources")
    SIAuto.Si.Dispose()
