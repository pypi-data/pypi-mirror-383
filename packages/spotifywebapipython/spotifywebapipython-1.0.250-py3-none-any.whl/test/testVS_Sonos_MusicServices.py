import sys
sys.path.append("..")

import unittest
from testVS_Sonos_Base import Test_Sonos_Base
from testVS_Sonos_AvTransport import *

# external package imports.
from smartinspectpython.siauto import *
from soco import SoCo
from soco.plugins.sharelink import ShareLinkPlugin
from soco.music_services import Account

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# MusicServices Tests.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_Sonos_MusicServices(Test_Sonos_Base): 
    """
    Test client scenarios.
    """

    ###################################################################################################################################
    # test methods start here - above are testing support methods.
    ###################################################################################################################################

    def fstr(self, template, **kwargs):
        return eval(f"f'{template}'", kwargs)


    def test_MediaTitleFormatting(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_MediaTitleFormatting"

        try:

            print("Test Starting:  %s\n" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # string to be formatted.
            result:str = '   this is a media title XXXXX   '
            
            # set format string:
            #fmtString:str = '{result.title()}'
            fmtString:str = '{result.title()}'
            # capitalize()	Converts the first character to upper case
            # casefold()    Converts string into lower case
            # lower()	    Converts a string into lower case
            # lstrip()	    Returns a left trim version of the string
            # strip()	    Returns a trimmed version of the string
            # swapcase()	Swaps cases, lower case becomes upper case and vice versa
            # title()	    Converts the first character of each word to upper case
            # upper()	    Converts a string into upper case
            
            try:
                resultFmt:str = None
                # format media title as desired by configuration options.
                #resultFmt = f"{(lambda x: (fmtString))}"
                #resultFmt = self.fstr(fmtString, result=result)
                resultFmt = eval("f'" + f"{fmtString}" + "'")
                resultFmt = eval("f'" + fmtString + "'")
                resultFmt = f'{fmtString}'
                resultFmt = f'' + fmtString + ''


                #resultFmt:str = f"{(lambda x: fmtString)}"
                #resultFmt:str = f'{result.title()}'
                _logsi.LogVerbose("media_title formatted from '%s' to '%s'" % (result, resultFmt))
                print("media_title formatted\n- OLD: '%s'\n- NEW: '%s'" % (result, resultFmt))
                result = resultFmt
            except Exception as ex:
                # trace.
                _logsi.LogException("media_title could not be formatted: %s" % (str(ex)), ex, logToSystemLogger=False)
                print("media_title conversion error: '%s'" % (str(ex)))
                print("media_title result:\n- OLD: '%s'" % (result))
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

    def test_GetAccounts(self):
        
        _logsi:SISession = SIAuto.Main            
        methodName:str = "test_GetAccounts"

        try:

            print("Test Starting:  %s" % methodName)
            _logsi.LogMessage("Testing method: '%s'" % (methodName), colorValue=SIColors.LightGreen)

            # create Sonos device instance.
            sonosDevice:SoCo = self._CreateSonosDevice_SONOS01()
            
            # send command to Sonos device.
            print('\nQuerying Music Service Accounts from Sonos device')
            accounts:dict = Account.get_accounts(sonosDevice)

            # dump account data.
            account:Account
            for account in accounts.values():
                _logsi.LogObject(SILevel.Verbose, "Sonos account definition: '%s' (service type=%s)" % (account.serial_number, account.service_type), account, colorValue=SIColors.LightGreen)
                print("\nAccount: %s" % str(account))
            
            print("\nTest Completed: %s" % methodName)

        except Exception as ex:

            _logsi.LogException("Test Exception (%s): %s" % (type(ex).__name__, methodName), ex)
            print("** Exception: %s" % str(ex))
            raise
        

# execute unit tests.
if __name__ == '__main__':
    unittest.main()
