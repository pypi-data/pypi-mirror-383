# external package imports.
from smartinspectpython.siauto import *
import time
import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1
from base64 import b64decode, b64encode

# our package imports.
from spotifywebapipython import SpotifyDiscovery
from spotifywebapipython.zeroconfapi.blobbuilder import BlobBuilder
from spotifywebapipython.zeroconfapi.credentials import Credentials
from spotifywebapipython.zeroconfapi.cryptodiffiehellman import CryptoDiffieHellman
from spotifywebapipython.zeroconfapi.helpers import write_bytes, write_int, byte_list_to_int, b64_to_int, int_to_bytes, string_to_int

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

try:

    print("Test Starting\n")
    _logsi.LogMessage("Testing ZeroConf Blob Decryption", colorValue=SIColors.LightGreen)

    # Sonos details:
    # # addUser request details (utf-8 encoded).
    # username:str = "1156377975"
    # deviceName:str = "LBsMBP"
    # # addUser request details (base64 encoded).
    # blobStr:str = "AQB8ay46qJJ8WWLpax4HlCs8AGIWQNG-KqvAMqfMExiny6vJ5662-vfS8IEG1IfiW4tAbdjc8gSBkUCp1dVsRqMWVtWs8q-d-zMxOQRKvplIkQXXmDOoRkWgRZV91Qz3Z50IeAu9jFj5y2PrAg=="
    # clientKeyStr:str = ""

    # Bose-ST10-1 details:
    # addUser request details (utf-8 encoded).
    username = 'thlucas2010@gmail.com' 
    password = 'Crazy$1spot'
    loginid  = '31l77y2al5lnn7mxfrmd4bpfhqke'
    
    deviceName:str = "ha-spotifyplus"
    deviceId:str = "5d4931f9d0684b625d702eaa24137b2c1d99539c"  # (info.DeviceId)
    
    # addUser request details (base64 encoded).
    # blobStr = Encrypted Blob (signed with checksum, base64-encoded String)
    blobStr:str = "/VHeE0bLLVmNRNLwXRRMHhWk2rGdStL1GDpP7hH1ToGxdVzukVmxx1Bxy3MVX33hVLZkB/zb4uNAZFCYpb6SXwNu2PCfylxbZaLOHrhEPeS0pMQHxiRZKfs+d8atNutSrdQJ3w=="
    # remote_PublicKey = info.PublicKey
    remote_PublicKeyStr:str = "2bZijq/75KYSu2FBzzx0RZCJZTKq7NlnraL5b4DNnnG7MS0LeJTs3m7bpBlfN6D1fqORg8rZwQqCo9vCub72IxREjp8+RjInO+j7RFLZ2rgYui5yNzmjlcVBQa85my/I"

    # **** Decrypt the blob:
    credentials:Credentials = Credentials(username, password)
    builder = BlobBuilder(credentials, deviceId, remote_PublicKeyStr)
    builder.Decrypt(blobStr)
  


except Exception as ex:

    _logsi.LogException(None, ex)
    print(str(ex))
        
finally:
            
    print("\nTests Completed")

    # dispose of SmartInspect.
    print("** Disposing of SmartInspect resources")
    SIAuto.Si.Dispose()