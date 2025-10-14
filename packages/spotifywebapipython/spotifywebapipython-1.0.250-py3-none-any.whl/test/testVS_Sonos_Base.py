import sys
sys.path.append("..")

import unittest

# external package imports.
from smartinspectpython.siauto import *
from soco import SoCo

# our package imports.
from spotifywebapipython import *
from spotifywebapipython.models import *

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# Sonos Tests - base class from which all client tests inherit from.
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class Test_Sonos_Base(unittest.TestCase):
    """
    Test client scenarios.
    """

    @classmethod
    def setUpClass(cls):
        
        try:

            #print("*******************************************************************************")
            #print("** unittest.TestCase - setUpClass() Started")

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
            _logsi.LogSeparator(SILevel.Fatal, colorValue=SIColors.LightGreen)
            _logsi.LogAppDomain(SILevel.Message, colorValue=SIColors.LightGreen)
            _logsi.LogSystem(SILevel.Message, colorValue=SIColors.LightGreen)
            
        except Exception as ex:

            print("\n** unittest.TestCase - Exception in setUpClass() method!\n" + str(ex))
            raise

        finally:

            pass
            #print("** unittest.TestCase - setUpClass() Complete")
            #print("*******************************************************************************")

    
    @classmethod
    def tearDownClass(cls):
        
        try:

            #print("*******************************************************************************")
            #print("** unittest.TestCase - tearDownClass() Started")

            # unwire events, and dispose of SmartInspect.
            #print("** Disposing of SmartInspect resources")
            SIAuto.Si.Dispose()
            
        except Exception as ex:

            print("\n** unittest.TestCase - Exception in tearDownClass() method!\n" + str(ex))
            raise

        finally:

            pass
            #print("** unittest.TestCase - tearDownClass() Complete")
            #print("*******************************************************************************")
                    
    
    def setUp(self):
        
        try:

            pass
            #print("*******************************************************************************")
            #print("** unittest.TestCase - setUp() Started")

            # nothing to do here.
            
        except Exception as ex:

            print("\n** unittest.TestCase - Exception in setUp() method!\n" + str(ex))
            raise

        finally:

            pass
            # print("** unittest.TestCase - setUp() Complete")
            # print("*******************************************************************************")

    
    def tearDown(self):
        
        try:

            # print("*******************************************************************************")
            # print("** unittest.TestCase - tearDown() Started")

            # nothing to do here.
            pass
            
        except Exception as ex:

            print("\n** unittest.TestCase - Exception in tearDown() method!\n" + str(ex))
            raise

        finally:

            # print("** unittest.TestCase - tearDown() Complete")
            # print("*******************************************************************************")
            pass
                    
    
    def _CreateSonosDevice_SONOS01(self) -> SoCo:
        """
        Creates a new SpotifyClient instance that can access user details, and sets all properties for executing these test cases.

        Returns:
            An SpotifyClient instance.
        """
        _logsi:SISession = SIAuto.Main            

        try:

            # create Sonos device instance by it's IP address.
            sonosDevice:SoCo = SoCo("192.168.1.91")
            print('\nSonos device created:\n Player Name="%s"' % (sonosDevice.player_name))
                       
            # return instance to caller.
            return sonosDevice

        except Exception as ex:

            _logsi.LogException("Exception in Test Method \"{0}\"".format(SISession.GetMethodName()), ex)
            print("** Exception: %s" % str(ex))
            raise


# execute unit tests.
if __name__ == '__main__':
    unittest.main()
