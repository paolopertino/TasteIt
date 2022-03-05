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

# List of all the project's strings.

GENERAL_STRINGS = {
    "GENERAL_WelcomeString": {
        "it": """
                 Ciao, sono TasteIT, ti aiuterò nella ricerca del locale perfetto in cui mangiare.\n\nDigita il comando /help per avere una completa panoramica delle funzionalità offerte.
              """,
        "en": """
                 Hi, I am TasteIT, and I will help you to search for the perfect restaurant to have a meal.\n\nTry the /help command for having a complete overview of my functionalities.
              """,
    },
}

ERROR_STRINGS = {
    "ERROR_NoServiceFound": {
        "it": """
                 Il servizio da te richiesto non è disponibile.
              """,
        "en": """
                 The service requested is not available.
              """,
    },
}


def getString(stringName: str, language: str, *args) -> str:
    if stringName.startswith("GENERAL"):
        return GENERAL_STRINGS.get(stringName).get(language).format(*args)
    else:
        return ERROR_STRINGS.get(stringName).get(language).format(*args)
