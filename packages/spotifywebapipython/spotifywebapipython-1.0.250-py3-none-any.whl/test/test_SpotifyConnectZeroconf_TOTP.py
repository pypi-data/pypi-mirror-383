# global imports.
import base64
from datetime import datetime
import json
import math
from pyotp import TOTP
import threading
import time
import requests

# our imports.
from spotifywebapipython import SpotifyApiError
from spotifywebapipython.sautils import GetUnixTimestampMSFromUtcNow

# load SmartInspect settings from a configuration settings file.
from smartinspectpython.siauto import *

# trace.
print("** Loading SmartInspect configuration settings")
siConfigPath:str = "./test/smartinspect.cfg"
SIAuto.Si.LoadConfiguration(siConfigPath)
SIAuto.Main.LogSeparator(SILevel.Debug)
SIAuto.Main.LogThread(SILevel.Debug, "Main Thread information", threading.current_thread())

SPOTIFY_WEBUI_URL_BASE = "https://open.spotify.com"
SPOTIFY_WEBUI_URL_GET_SERVER_TIME = SPOTIFY_WEBUI_URL_BASE + "/server-time"
MSG_SPOTIFY_WEB_API_RETRY_TIMEOUT:str = "Timed out waiting for Spotify Gateway to become available; gave up after %f seconds from initial request."
MSG_SPOTIFY_WEB_API_RETRY_RESPONSE_STATUS:str = "Spotify Web API request returned with a %s status (%s); request will be retried"
MSG_SPOTIFY_WEB_API_RETRY_REQUEST_DELAY:str = "Delaying for %s seconds before retry to allow Spotify Gateway to become available"


def Base32FromBytes(inputBytes:bytes, secretSauce:str) -> str:
    """
    Converts an array of bytes to a base32 string value.

    Args:
        inputBytes (bytearray):
            Array of bytes to convert to Base32.
        secretSauce (str):
            Characters allowed in the generated base32 string value.

    Returns:
        A generated base32 string value.
    """

    t:int = 0  # This will store the number of bits processed
    n:int = 0  # This will store the accumulated bits
    result:str = ""  # This will store the resulting base32 string

    for byte in inputBytes:

        # shift accumulated bits to the left and add the current byte.
        n = (n << 8) | byte
        t += 8

        # while we have more than 5 bits, we process them.
        while t >= 5:
            # extract 5 bits and append the corresponding character from secret sauce.
            result += secretSauce[(n >> (t - 5)) & 31]
            t -= 5

    # if there are any remaining bits, process them.
    if t > 0:
        result += secretSauce[(n << (5 - t)) & 31]

    # return result to caller.
    return result


def CleanBuffer(value:str) -> bytes:
    """
    Converts a displayable hex string value to a bytes object.

    Args:
        value (str):
            Input value in displayable hex format (e.g. "0140FF").

    Returns:
        A bytes object that contains the converted `value` contents.
    """

    # create a list of zeroes of length half the size of input value.
    result:bytes = [0] * (len(value) // 2)
    
    # convert the hexadecimal pairs to integers.
    for idx in range(0, len(value), 2):
        result[idx // 2] = int(value[idx:idx+2], 16)
    
    # return result to caller.
    return bytes(result)


def TimeFormat(time, interval=30) -> int:

    # get the time in milliseconds since the epoch.
    time_milliseconds = int(time.timestamp() * 1000)
    
    # convert the milliseconds to seconds (remove the last 3 digits).
    format_time = str(time_milliseconds)[:-3]
    
    # divide by interval and return the result as an integer.
    return int(format_time) // interval


_logsi = SIAuto.Main
apiMethodName:str = 'GenerateTOTP'
apiMethodParms:SIMethodParmListContext = None
tracePrefix:str = 'SpotifyWebPlayerAccessToken server time'
        
try:

    # trace.
    apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
    _logsi.LogMethodParmList(SILevel.Verbose, "Generating Spotify TOTP (Time-based One Time Password) value", apiMethodParms)

    # characters allowed in the generated base32 secret string value.
    secretSauce:str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

    # perform a bitwise XOR (^) on each cipherbyte.
    secretCipherBytesRaw:list = [12, 56, 76, 33, 88, 44, 88, 33, 78, 78, 11, 66, 22, 22, 55, 69, 54]
    _logsi.LogArray(SILevel.Debug, "secretCipherBytesRaw (len=%d)" % (len(secretCipherBytesRaw)), secretCipherBytesRaw)
    secretCipherBytes:list = [
        elm ^ ((idx % 33) + 9) 
        for idx, elm in enumerate(secretCipherBytesRaw)
    ]
    _logsi.LogArray(SILevel.Debug, "secretCipherBytes (len=%d)" % (len(secretCipherBytes)), secretCipherBytes)

    # convert secret cipher bytes into a string, then encode as UTF-8.
    secretCipherString:str = "".join(str(num) for num in secretCipherBytes)
    _logsi.LogString(SILevel.Debug, "secretCipherString (len=%d)" % (len(secretCipherString)), secretCipherString)
    secretCipherBytesEncoded:bytes = secretCipherString.encode("utf-8")
    _logsi.LogBinary(SILevel.Debug, "secretCipherBytesEncoded (len=%d)" % (len(secretCipherBytesEncoded)), secretCipherBytesEncoded)

    # convert each byte to hexadecimal string.
    secretCipherBytesHex:str = "".join(["{:02x}".format(byte) for byte in secretCipherBytesEncoded])
    _logsi.LogString(SILevel.Debug, "secretCipherBytesHex (len=%d)" % (len(secretCipherBytesHex)), secretCipherBytesHex)

    # clean the result using the CleanBuffer function.
    secretBytes:bytes = CleanBuffer(secretCipherBytesHex)
    _logsi.LogBinary(SILevel.Debug, "secretBytes (len=%d)" % (len(secretBytes)), secretBytes)

    # convert bytes to base32 string value.
    secretBase32:str = Base32FromBytes(secretBytes, secretSauce)
    _logsi.LogString(SILevel.Debug, "secretBase32 (len=%d)" % (len(secretBase32)), secretBase32)

    # create a session, using the specified header data.
    session = requests.Session()
    reqUrl:str = SPOTIFY_WEBUI_URL_GET_SERVER_TIME
    reqHeaders = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}

    # trace.
    _logsi.LogVerbose("Retrieving Spotify TOTP server time value")
    _logsi.LogDictionary(SILevel.Debug, "%s http request: \"%s\" (headers)" % (tracePrefix, SPOTIFY_WEBUI_URL_GET_SERVER_TIME), reqHeaders)

    # request retry loop for failed requests that are temporary in nature (504 Gateway Timeout, etc).
    loopTotalDelay:float = 0
    LOOP_DELAY:float = 0.200
    LOOP_TIMEOUT:float = 1.000
    while True:
            
        # convert the spotify web player cookie credentials to an access token.
        response = session.get(
            reqUrl, 
            headers=reqHeaders, 
            allow_redirects=False,
            )

        # check for errors that are temporary in nature; for these errors, we will retry the 
        # request for a specified number of tries with a small wait period in between.
        if (response.status_code == 504):

            # only retry so many times before we give up.
            if (loopTotalDelay >= LOOP_TIMEOUT):
                raise SpotifyApiError(MSG_SPOTIFY_WEB_API_RETRY_TIMEOUT % (loopTotalDelay), None, logsi=_logsi)

            # trace.
            _logsi.LogVerbose(MSG_SPOTIFY_WEB_API_RETRY_RESPONSE_STATUS % (response.status_code, response.reason), colorValue=SIColors.Red)

            # wait just a bit between requests.
            _logsi.LogVerbose(MSG_SPOTIFY_WEB_API_RETRY_REQUEST_DELAY % (LOOP_DELAY))
            time.sleep(LOOP_DELAY)
            loopTotalDelay = loopTotalDelay + LOOP_DELAY

        else:

            # otherwise, break out of retry loop and process response.
            break

    # trace.
    if _logsi.IsOn(SILevel.Debug):
        _logsi.LogObject(SILevel.Debug, "%s http response object - type=\"%s\", module=\"%s\"" % (tracePrefix, type(response).__name__, type(response).__module__), response)
        _logsi.LogObject(SILevel.Debug, "%s http response [%s-%s] (response)" % (tracePrefix, response.status_code, response.reason), response)
        if (response.headers):
            _logsi.LogCollection(SILevel.Debug, "%s http response [%s-%s] (headers)" % (tracePrefix, response.status_code, response.reason), response.headers.items())

    # if successful request, then process response; otherwise, it's an exception.
    if (response.status_code == 200):
        _logsi.LogVerbose("Spotify TOTP server time request was successful within %f seconds from initial request; processing results" % (loopTotalDelay))
    else:
        raise SpotifyApiError("Spotify TOTP Server Time request failed: %s - %s" % (response.status_code, response.reason), None, logsi=_logsi)

    # load request response.
    data = response.content.decode('utf-8')
    responseData = json.loads(data)

    # trace.
    if _logsi.IsOn(SILevel.Verbose):
        if isinstance(responseData, dict):
            _logsi.LogDictionary(SILevel.Verbose, "%s http response [%s-%s] (json dict)" % (tracePrefix, response.status_code, response.reason), responseData, prettyPrint=True)
        elif isinstance(responseData, list):
            _logsi.LogArray(SILevel.Verbose, "%s http response [%s-%s] (json array)" % (tracePrefix, response.status_code, response.reason), responseData)
        else:
            _logsi.LogObject(SILevel.Verbose, "%s http response [%s-%s] (json object)" % (tracePrefix, response.status_code, response.reason), responseData)

    # parse server time value; if not found, then it's an error.
    serverTimeSeconds:int = responseData.get("serverTime", None);
    if (serverTimeSeconds == None):
        raise SpotifyApiError("Spotify TOTP server time response was not recognized: \"%s\"" % (str(data)), None, logsi=_logsi)

    # trace.
    _logsi.LogVerbose("Spotify TOTP server time value = \"%s\"" % (serverTimeSeconds))

    # create TOTP instance.
    totp:TOTP = TOTP(
        secretBase32,
        digest="SHA1",
        digits=6,
        interval=30,
    )

    # get a generated Time-based One Time Password (TOTP) value.
    totp_value = totp.at(serverTimeSeconds)
    _logsi.LogString(SILevel.Debug, "Spotify TOTP (Time-based One Time Password) value (len=%d)" % (len(totp_value)), totp_value)

        # params = {
        #     "reason": "transport",
        #     "productType": "web_player",
        #     "totp": otp_value,
        #     "totpVer": 5,
        #     "ts": timestamp,
        # }

    breakpoint33:str = "TEST_BREAKPOINT"

except Exception as ex:
            
    # trace.
    raise SpotifyApiError("Could not get Spotify Web Player TOTP value", ex, logsi=_logsi)

finally:

    # trace.
    _logsi.LeaveMethod(SILevel.Debug, apiMethodName)

# dispose of SmartInspect instance and allocated resources.
SIAuto.Si.Dispose()

print("SpotConn has finished!")

