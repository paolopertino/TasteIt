####################################################################################
# Copyright (c) 2022 TasteIt                                                       #
# Author: Paolo Pertino                                                            #
#                                                                                  #
# Permission is hereby granted, free of charge, to any person obtaining a copy     #
# of this software and associated documentation files (the "Software"), to deal    #
# in the Software without restriction, including without limitation the rights     #
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell        #
# copies of the Software, and to permit persons to whom the Software is            #
# furnished to do so, subject to the following conditions:                         #
#                                                                                  #
# The above copyright notice and this permission notice shall be included in       #
# all copies or substantial portions of the Software.                              #
#                                                                                  #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR       #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,         #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE      #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER           #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,    #
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN        #
# THE SOFTWARE.                                                                    #
####################################################################################

from dotenv import dotenv_values
from os import getenv
from sys import path
from enum import Enum, auto, unique

path.append("..")

from custom_exceptions import NoServiceFoundException
from STRINGS_LIST import getString


@unique
class Service(Enum):
    """Defines all the available services which have an API key set in the .env file or in the os environment.

    Usage:
        * Add the name of the service you want to implement in this class.
        * Add an ENV variable to your environment or .env file with the following convention:
                * if the key you want insert is for dev use: DEV_`<SERVICE_NAME>`_KEY = `KEY_VALUE`
                * otherwise if it's for public usage: `<SERVICE_NAME>`_KEY = `KEY_VALUE`.
    """

    TELEGRAM = auto()
    GOOGLE_PLACES = auto()
    TELEGRAM_DEVELOPER_CHAT_ID = auto()


class ApiKey:
    """
    A class used to represent an API key.

    Attributes
    ----------
    service : Service
        the API key service

    Methods
    -------
    @property
    `value() -> str`
        Returns the API key of the key service if it is available.\\
        Throws a NoServiceFoundException if the service given is not available.
    """

    def __init__(self, service: Service, devMode: bool = False) -> None:
        self.service = service
        self.isDeveloperKey = devMode

    @property
    def value(self):
        """The key value

        Raises:
            NoServiceFoundException: raised when the service given is not part of the available services.

        Returns:
            str: the value of the current key
        """
        if self.service in list(Service):
            if self.isDeveloperKey:
                keyToSearch = "DEV_" + self.service.name + "_KEY"
            else:
                keyToSearch = self.service.name + "_KEY"

            if getenv(keyToSearch) != None:
                return getenv(keyToSearch)
            else:
                return dotenv_values(".env").get(keyToSearch)
        else:
            raise NoServiceFoundException(
                self.service, getString("ERROR_NoServiceFound", "en")
            )
