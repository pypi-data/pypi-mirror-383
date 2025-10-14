# global imports.
import threading

# our imports.
from spotifywebapipython import SpotifyClient
from spotifywebapipython.const import VERSION as SPOTIFYWEBAPIPYTHON_VERSION
from spotifywebapipython.models import SpotifyConnectDevice, SpotifyConnectDevices, PlayerPlayState
from spotifywebapipython.spotifyconnect import SpotifyConnectDeviceEventArgs

# load SmartInspect settings from a configuration settings file.
from smartinspectpython.siauto import *

# user environment constants that control the application.
SPOTIFY_DEVAPP_CLIENT_ID:str = "eab07793bc744770a706ecc68097a218"   # Spotify developer application client id value.
SPOTIFY_CONNECT_USERNAME:str = "thlucas2010@gmail.com"              # Spotify username value.
SPOTIFY_CONNECT_PASSWORD:str = "Crazy$1spot"                        # Spotify password value.
SPOTIFY_CONNECT_LOGINID:str = None                                  # Spotify loginid value (None defaults to Spotify profile value based on SPOTIFY_DEVAPP_CLIENT_ID)
SPOTIFY_CONNECT_DISCOVERY_TIMEOUT:int=20                            # discovery timeout value in seconds; specify 0 to use player defined Spotify Connect devices only
TESTAPP_DIR:str = "./test"

# trace.
print("** Loading SmartInspect configuration settings")
siConfigPath:str = TESTAPP_DIR + "/smartinspect.cfg"
SIAuto.Si.LoadConfiguration(siConfigPath)
SIAuto.Main.LogSeparator(SILevel.Debug)
SIAuto.Main.LogThread(SILevel.Debug, "Main Thread information", threading.current_thread())


def OnDeviceAdded(sender:object, e:SpotifyConnectDeviceEventArgs) -> None:
    """
    Method that will handle the `DeviceAdded` event.
    
    Args:
        sender (object):
            The object which fired the event.
        e (SpotifyConnectDeviceEventArgs):
            Arguments that contain detailed information related to the event.

    This event is fired when a Spotify Connect device has been added. 
    """
    # trace.
    #_logsi.LogVerbose(e.StatusText)
    print("spotconn device added:   %s" % (e.DeviceObject.Title))

def OnDeviceRemoved(sender:object, e:SpotifyConnectDeviceEventArgs) -> None:
    """
    Method that will handle the `DeviceRemoved` event.
    
    Args:
        sender (object):
            The object which fired the event.
        e (SpotifyConnectDeviceEventArgs):
            Arguments that contain detailed information related to the event.

    This event is fired when a Spotify Connect device has been removed. 
    """
    # trace.
    #_logsi.LogVerbose(e.StatusText)
    print("spotconn device removed: %s" % (e.DeviceObject.Title))


def OnDeviceUpdated(sender:object, e:SpotifyConnectDeviceEventArgs) -> None:
    """
    Method that will handle the `DeviceUpdated` event.
    
    Args:
        sender (object):
            The object which fired the event.
        e (SpotifyConnectDeviceEventArgs):
            Arguments that contain detailed information related to the event.

    This event is fired when a Spotify Connect device has been updated. 
    """
    # trace.
    #_logsi.LogVerbose(e.StatusText)
    print("spotconn device updated: %s" % (e.DeviceObject.Title))


# create SpotifyClient instance.
print("Creating SpotifyClient to transfer playback to the Chromecast device")
spClient:SpotifyClient = SpotifyClient(
    manager=None,
    tokenStorageDir=TESTAPP_DIR + "/testdata",
    tokenStorageFile="SpotifyWebApiPython_tokens.json",
    spotifyConnectLoginId=SPOTIFY_CONNECT_LOGINID,
    spotifyConnectUsername=SPOTIFY_CONNECT_USERNAME,                    # for tokenProfileId below
    spotifyConnectPassword=SPOTIFY_CONNECT_PASSWORD,                    # not used, but required if username specified
    spotifyConnectDiscoveryTimeout=SPOTIFY_CONNECT_DISCOVERY_TIMEOUT,   # specify 0 to use player defined Spotify Connect devices
)

print("Discovering Spotify Connect devices on the local network ...")

# set authorization token.
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
spClient.SetAuthTokenAuthorizationCodePKCE(
    SPOTIFY_DEVAPP_CLIENT_ID, 
    SPOTIFY_SCOPES, 
    tokenProfileId=spClient.SpotifyConnectUsername
)

# reference the Spotify Connect Directory task.
scDirectory = spClient.SpotifyConnectDirectory

# wire up events to receive updates as zeroconf device changes are detected.
scDirectory.DeviceAdded += OnDeviceAdded
scDirectory.DeviceRemoved += OnDeviceRemoved
scDirectory.DeviceUpdated += OnDeviceUpdated

# load initial device list.
scDevices:SpotifyConnectDevices = spClient.GetSpotifyConnectDevices(refresh=True)

while True:

    # prompt user for action.
    print('\nSpotifyWebApiPython version = %s' % SPOTIFYWEBAPIPYTHON_VERSION)
    print('Commands available:')
    print('- "ACTIVATE n" - activates Spotify Cast App on device (no transfer playback)')
    print('- "TRANSFER n" - transfer playback to specified spotify connect device entry # (by id)')
    print('- "TRANSNAME n"- transfer playback to specified spotify connect device entry # (by name)')
    print('- "PAUSE n"    - pause playback on specified spotify connect device entry #')
    print('- "RESUME n"   - resume playback on specified spotify connect device entry #')
    print('- "DEVICE xxx" - gets the specified device instance by name or id')
    print('- "LIST"       - list spotify connect device summary')
    print('- "INFO n"     - list spotify connect device detailed info')
    print('- "TASKS"      - list spotify connect device detailed info')
    print('- "REFRESH"    - refresh dynamic device list')
    print('- "LASTPLAYED" - display last played info')
    print('- "STOP"       - stop Spotify Connect Zeroconf Browser task')
    cmd = input("Enter Command:\n")
    cmd = (cmd + "").upper()

    if (cmd.startswith("ACTIVATE")):
        try:
            idx:int = int("0" + cmd.replace("ACTIVATE","").strip())
            if (idx < 1): continue
            scDevice:SpotifyConnectDevice = scDevices[idx - 1]
            scDirectory.ActivateCastAppSpotify(scDevice.Id, transferPlayback=False)
            print("You have about 15 seconds to transfer playback to the cast device")
        except Exception as ex:
            print(str(ex))
        continue

    if (cmd.startswith("TRANSNAME")):
        try:
            idx:int = int("0" + cmd.replace("TRANSNAME","").strip())
            if (idx < 1): continue
            scDevice:SpotifyConnectDevice = scDevices[idx - 1]
            print("Transferring to: %s [by name]\n" % scDevice.Title)
            spClient.PlayerTransferPlayback(scDevice.Name, play=True)
        except Exception as ex:
            print(str(ex))
        continue

    if (cmd.startswith("TRANSFER")):
        try:
            idx:int = int("0" + cmd.replace("TRANSFER","").strip())
            if (idx < 1): continue
            scDevice:SpotifyConnectDevice = scDevices[idx - 1]
            print("Transferring to: %s [by id]\n" % scDevice.Title)
            spClient.PlayerTransferPlayback(scDevice.Id, play=True)
        except Exception as ex:
            print(str(ex))
        continue

    if (cmd.startswith("PAUSE")):
        try:
            idx:int = int("0" + cmd.replace("PAUSE","").strip())
            deviceId:str = None
            if (idx > 0):
                scDevice:SpotifyConnectDevice = scDevices[idx - 1]
                print("Pausing play on: %s\n" % scDevice.Title)
                deviceId = scDevice.Id
            else:
                print("Pausing play on active device\n")
            spClient.PlayerMediaPause(deviceId)
        except Exception as ex:
            print(str(ex))
        continue

    if (cmd.startswith("RESUME")):
        try:
            idx:int = int("0" + cmd.replace("RESUME","").strip())
            deviceId:str = None
            if (idx > 0):
                scDevice:SpotifyConnectDevice = scDevices[idx - 1]
                print("Resuming play on: %s\n" % scDevice.Title)
                deviceId = scDevice.Id
            else:
                print("Resuming play on active device\n")
            spClient.PlayerMediaResume(deviceId)
        except Exception as ex:
            print(str(ex))
        continue

    if (cmd.startswith("INFO")):
        try:
            idx:int = int("0" + cmd.replace("INFO","").strip())
            if (idx < 1): continue
            scDevice:SpotifyConnectDevice = scDevices[idx - 1]
            print("\n%s" % (scDevice.ToString()))
        except Exception as ex:
            print(str(ex))
        continue

    if (cmd.startswith("DEVICE")):
        try:
            value:str = ("" + cmd.replace("DEVICE","").strip())
            scDevice:SpotifyConnectDevice = scDirectory.GetDevice(value, refreshDynamicDevices=False)
            #scDevice:SpotifyConnectDevice = scDirectory.GetDevice(value, "Bose-ST10-2")       # test valid default device.
            #scDevice:SpotifyConnectDevice = scDirectory.GetDevice(value, "Bose-ST10-XXXX")   # test invalid default device exception.
            #scDevice:SpotifyConnectDevice = scDirectory.GetDevice(value, None)               # test no default device exception.
            print("\n%s" % (scDevice.ToString()))
        except Exception as ex:
            print(str(ex))
        continue

    if (cmd == "REFRESH"):
        try:
            print("\nRefreshing Dynamic Devices")
            scDevices = spClient.GetSpotifyConnectDevices(refresh=True)
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (*active*)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx + 1), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))
            continue
        except Exception as ex:
            print(str(ex))
        continue

    if (cmd == "LIST"):
        try:
            print("\nCached Spotify Connect Device List:")
            scDevices = spClient.GetSpotifyConnectDevices(refresh=False)
            scDevice:SpotifyConnectDevice
            for idx in range(len(scDevices)):
                scDevice:SpotifyConnectDevice = scDevices[idx]
                isActive:str = " (*active*)" if (scDevice.IsActiveDevice) else ""
                print("%s - %s [%s]%s" % (str(idx + 1), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))
            continue
        except Exception as ex:
            print(str(ex))
        continue

    if (cmd == "TASKS"):
        try:
            print("\nSpotify App Task List:")
            for castApp in scDirectory.CastAppTasks.values():
                print(" - %s (isIdle=%s), status: \"%s\"" % (castApp.name, str(castApp.CastDevice.is_idle), str(castApp.CastDevice.status.status_text)))
            continue
        except Exception as ex:
            print(str(ex))
        continue

    if (cmd == "STOP"):
        try:
            print("\nRequesting stop of %s ..." % (scDirectory.name))
            break
        except Exception as ex:
            print(str(ex))
        continue

    if (cmd == "LASTPLAYED"):
        try:
            playerState:PlayerPlayState = spClient.GetPlayerPlaybackState(additionalTypes="episode")
            playerStateContext:str = "None" if playerState.Context is None else playerState.Context.Uri
            lastInfoContext:str = "None" if spClient.PlayerLastPlayedInfo.Context is None else spClient.PlayerLastPlayedInfo.Context.Uri
            print("\nSpotify PlayerState Info:")
            print(" - Device:   %s" % playerState.Device.SelectItemNameAndId)
            print(" - Context:  %s" % playerStateContext)
            print(" - Track:    %s" % playerState.Summary)
            print(" - Type:     %s" % playerState.ItemType)
            print(" - Progress: %s" % playerState.ProgressMS)
            print("\nSpotify Last Played Info:")
            print(" - Device:   %s" % spClient.PlayerLastPlayedInfo.Device.SelectItemNameAndId)
            print(" - Context:  %s" % lastInfoContext)
            print(" - Track:    %s" % spClient.PlayerLastPlayedInfo.Summary)
            print(" - Type:     %s" % spClient.PlayerLastPlayedInfo.ItemType)
            print(" - Progress: %s" % spClient.PlayerLastPlayedInfo.ProgressMS)
            continue
        except Exception as ex:
            print(str(ex))
        continue

    print("Command not recognized: \"%s\"" % (cmd))

# dispose of SpotifyClient instance and allocated resources.
spClient.Dispose()

print("SpotConn has finished!")

