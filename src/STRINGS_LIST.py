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
                 Ciao\, sono _*TasteIT*_ 🍣🍝\, ti aiuterò nella ricerca del locale perfetto in cui mangiare😋\.\n\nDigita il comando /help per avere una completa panoramica delle funzionalità offerte\.
              """,
        "en": """
                 Hi\, I am _*TasteIT*_ 🍣🍝\, and I will help you to search for the perfect restaurant to have a meal😋\.\n\nTry the /help command for having a complete overview of my functionalities\.
              """,
    },
    "GENERAL_HelpString": {
        "it": """
                 🔧 Comandi generali 🔧\n/start \~ Avvia il bot\.\n/help \~ Visualizza la lista dei comandi disponibili\.\n/lang \~ Imposta la lingua del bot\.\n\n🍽 Comandi Ricerca Ristoranti 🍽\n/cerca \~ Inizia la ricerca di un ristorante\.\n
              """,
        "en": """
                 🔧 General commands 🔧\n/start \~ Starts the bot\.\n/help \~ Shows all available commands\.\n/lang \~ Change the bot language\.\n\n🍽 Restaurant Search Commands 🍽\n/cerca \~ Starts a restaurant search\.\n
              """,
    },
    "GENERAL_ChooseLanguageString": {
        "it": """
                 Imposta la lingua del bot\:
              """,
        "en": """
                 Set the bot language\:
              """,
    },
    "GENERAL_LanguageUpdated": {
        "it": """
                 La tua lingua è stata aggiornata 🇮🇹
              """,
        "en": """
                 Your language has been updated 🇺🇸
              """,
    },
    "GENERAL_OperationCanceled": {
        "it": """
                 L'operazione è stata annullata\.
              """,
        "en": """
                 The operation has been cancelled\.
              """,
    },
    "GENERAL_SendRequiredPositionInfos": {
        "it": """
                 Per iniziare la ricerca dei ristoranti inviami la tua posizione attuale\, oppure indicami il nome di una località di tuo interesse\.
              """,
        "en": """
                 In order to start the restaurant search send me your current position or indicate a name of a place of interest\. 
              """,
    },
    "GENERAL_SearchRestaurantStartingLocation": {
        "it": """
                 Perfetto ✅, inizierò la mia ricerca a partire da *{}*\.\nCosa vuoi mangiare?
              """,
        "en": """
                 Awesome ✅, I'll start the research from *{}*\.\nWhat would you like to eat?
              """,
    },
    "GENERAL_SearchRestaurantCurrentPositionAccepted": {
        "it": """
                 Perfetto ✅, inizierò la mia ricerca a partire dalla tua *posizione attuale*\.\nCosa vuoi mangiare?
              """,
        "en": """
                 Awesome ✅, I'll start the research from your *current position*\.\nWhat would you like to eat?
              """,
    },
    "GENERAL_SearchRestaurantInfoRecap": {
        "it": """
               ℹ️ *TasteIt \- Info* ℹ️\nCibo 🍝 \- *{}*\nRistorante aperto ora 🕧 \- *{}*\nPrezzo massimo 💶 \- *{}*\n\nVuoi modificare qualcosa?
              """,
        "en": """
               ℹ️ *TasteIt \- Info* ℹ️\nFood 🍝 \- *{}*\nRestaurant open now 🕧 \- *{}*\nMax price 💶 \- *{}*\n\nDo you need to modify something?
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
    "ERROR_ChoseAnAvailableOption": {
        "it": """
                 Per favore\, scegli una delle opzioni disponibili prima di continuare\.
              """,
        "en": """
                 Please\, chose an available option from the above ones before continuing\.
              """,
    },
    "ERROR_GoogleCriticalError": {
        "it": """
                 Errore critico\. Contatta lo sviluppatore \(\@paolino\_x\)\, notificando GOOGLE\_ERROR\.
              """,
        "en": """
                 A critical error has occured\. Please contact the developer \(\@paolino\_x\)\, notifing GOOGLE\_ERROR\.
              """,
    },
    "ERROR_NoPlacesFound": {
        "it": """
                 Nessun posto trovato\. Riprova inviandomi un nuovo nome di località o la tua posizione attuale\.
              """,
        "en": """
                 No places found\. Please\, send me back another location name or your current position\.
              """,
    },
    "ERROR_InvalidPosition": {
        "it": """
                 Posizione invalida\, inviami nuovamente la tua posizione o il nome di una località di interesse\.
              """,
        "en": """
                 Invalid position\. Please\, send me back again a location name of your interest or your current position\.
              """,
    },
}


def getString(stringName: str, language: str, *args) -> str:
    if stringName.startswith("GENERAL"):
        return GENERAL_STRINGS.get(stringName).get(language).format(*args)
    else:
        return ERROR_STRINGS.get(stringName).get(language).format(*args)
