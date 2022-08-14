import os.path
import time

try:
    # Python 3
    from configparser import ConfigParser
except ImportError:
    # Python 2
    from ConfigParser import RawConfigParser as ConfigParser

from garmin_uploader import CONFIG_FILE, logger
from garmin_uploader.api import GarminAPI


class User(object):
    """
    Garmin Connect user model
    Authenticates through web api as a browser
    """

    def __init__(self, username=None, password=None):
        """
        ---- GC login credential order of precedence ----
        1) Credentials given on command line
        2) Credentials given in config file in current working directory
        3) Credentials given in config file in user's home directory

        Command line overrides all, config in cwd overrides config in home dir
        """
        # Authenticated API session
        self.session = None

        configCurrentDir = os.path.abspath(os.path.normpath("./" + CONFIG_FILE))
        configHomeDir = os.path.expanduser(os.path.normpath("~/" + CONFIG_FILE))

        if username and password:
            logger.debug("Using credentials from command line.")
            self.username = username
            self.password = password
        elif os.path.isfile(configCurrentDir):
            logger.debug("Using credentials from '%s'." % configCurrentDir)
            config = ConfigParser()
            config.read(configCurrentDir)
            self.username = config.get("Credentials", "username")
            self.password = config.get("Credentials", "password")
        elif os.path.isfile(configHomeDir):
            logger.debug("Using credentials from '%s'." % configHomeDir)
            config = ConfigParser()
            config.read(configHomeDir)
            self.username = config.get("Credentials", "username")
            self.password = config.get("Credentials", "password")
        else:
            cwd = os.path.abspath(os.path.normpath("./"))
            homepath = os.path.expanduser(os.path.normpath("~/"))
            raise Exception(
                "'{}' file does not exist in current directory {}"
                "or home directory {}.  Use login options.".format(CONFIG_FILE, cwd, homepath)
            )

    def authenticate(self, force=False):
        """
        Authenticate on Garmin API
        """
        if self.session is not None and not force:
            # return cached session unless we're forcing authentication this
            # will help keep test from constantly trying to reauthenticate
            return self.session
        logger.info("Try to login on GarminConnect...")
        logger.debug("Username: {}".format(self.username))
        logger.debug("Password: {}".format("*" * len(self.password)))

        api = GarminAPI()
        for _ in range(3):
            try:
                self.session = api.authenticate(self.username, self.password)
                logger.debug("Login Successful.")
                return True
            except Exception as e:
                logger.critical("Login Failure: {}".format(e))
                time.sleep(10)

        return False
