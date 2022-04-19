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
                 Ciao, sono <b><i>TasteIT</i></b> 🍣🍝, ti aiuterò nella ricerca del locale perfetto in cui mangiare😋.\n\nDigita il comando /help per avere una completa panoramica delle funzionalità offerte.
              """,
        "en": """
                 Hi, I am <b><i>TasteIT*</i></b> 🍣🍝, and I will help you to search for the perfect restaurant to have a meal😋.\n\nTry the /help command for having a complete overview of my functionalities.
              """,
    },
    "GENERAL_HelpString": {
        "it": """
                 🔧 Comandi generali 🔧\n/start ~ Avvia il bot.\n/help ~ Visualizza la lista dei comandi disponibili.\n/lang ~ Imposta la lingua del bot.\n\n🍽 Comandi Ricerca Ristoranti 🍽\n/cerca ~ Inizia la ricerca di un ristorante.\n
              """,
        "en": """
                 🔧 General commands 🔧\n/start ~ Starts the bot.\n/help ~ Shows all available commands.\n/lang ~ Change the bot language.\n\n🍽 Restaurant Search Commands 🍽\n/cerca ~ Starts a restaurant search.\n
              """,
    },
    "GENERAL_ChooseLanguageString": {
        "it": """
                 Imposta la lingua del bot:
              """,
        "en": """
                 Set the bot language:
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
                 L'operazione è stata annullata.
              """,
        "en": """
                 The operation has been cancelled.
              """,
    },
    "GENERAL_SendRequiredPositionInfos": {
        "it": """
                 Per iniziare la ricerca dei ristoranti inviami la tua posizione attuale, oppure indicami il nome di una località di tuo interesse.
              """,
        "en": """
                 In order to start the restaurant search send me your current position or indicate a name of a place of interest. 
              """,
    },
    "GENERAL_SearchRestaurantStartingLocation": {
        "it": """
                 Perfetto ✅, inizierò la mia ricerca a partire da <b>{}</b>.\nCosa vuoi mangiare?
              """,
        "en": """
                 Awesome ✅, I'll start the research from <b>{}</b>.\nWhat would you like to eat?
              """,
    },
    "GENERAL_SearchRestaurantCurrentPositionAccepted": {
        "it": """
                 Perfetto ✅, inizierò la mia ricerca a partire dalla tua <b>posizione attuale</b>.\nCosa vuoi mangiare?
              """,
        "en": """
                 Awesome ✅, I'll start the research from your <b>current position</b>.\nWhat would you like to eat?
              """,
    },
    "GENERAL_SearchRestaurantInfoRecap": {
        "it": """
               ℹ️ <b>TasteIt - Info</b> ℹ️\nCibo 🍝 - <b>{}</b>\nRistorante aperto ora 🕧 - {}\nPrezzo massimo 💶 - <b>{}</b>\n\nVuoi modificare qualcosa?
              """,
        "en": """
               ℹ️ <b>TasteIt - Info</b> ℹ️\nFood 🍝 - <b>{}</b>\nRestaurant open now 🕧 - {}\nMax price 💶 - <b>{}</b>\n\nDo you need to modify something?
              """,
    },
    "GENERAL_FoodPreferenceReset": {
        "it": """
               Cosa vuoi mangiare?
        """,
        "en": """
               What would you like to eat?
        """,
    },
    "GENERAL_RestaurantInfoDisplay": {
        "it": """
               🍣 <b>TasteIt - Risultati</b> 🍝\n Ristorante - <b>{}</b>\n{}\n{} recensioni totali.
        """,
        "en": """
               🍣 <b>TasteIt - Results</b> 🍝\n Restaurant - <b>{}</b>\n{}\n{} total reviews.
        """,
    },
    "GENERAL_MoreInfos": {
        "it": """
        💡 Maggiori informazioni 💡
        """,
        "en": """
        💡 More infos 💡
        """,
    },
    "GENERAL_PollButton": {
        "it": """
        📊 Avvia un Sondaggio 📊
        """,
        "en": """
        📊 Start a Poll 📊
        """,
    },
    "GENERAL_PollStarted": {
        "it": """
        🍣 TasteIt - Sondaggio 🍝\n\n📊 Sondaggio creato. Scegliete un ristorante:
        """,
        "en": """
        🍣 TasteIt - Poll 🍝\n\n📊 Poll started. Pick a restaurant:
        """,
    },
    "GENERAL_DetailedInfoOfRestaurant": {
        "it": """
               🍣 <b>TasteIt - Dettaglio</b> 🍝\n\n🍴 Locale - <b>{}</b>\n📍Indirizzo - <b><a href='{}'>{}</a></b>\n ☎️ Telefono - <a href='tel:{}'>{}</a>\n{}\n{} recensioni totali.\n––––––––––––––––––\n\n🕙 Orario 🕟\n{}
        """,
        "en": """
               🍣 <b>TasteIt - Details</b> 🍝\n\n🍴 Restaurant - <b>{}</b>\n📍Address - <b><a href='{}'>{}</a></b>\n ☎️ Phone - <a href='tel:{}'>{}</a>\n{}\n{} total reviews.\n––––––––––––––––––\n\n🕙 Timetable 🕟\n{}
        """,
    },
    "GENERAL_ReviewContent": {
        "it": """
               🍣 <b>TasteIt - Recensione</b> 🍝\n\n 💁🏼‍♂️ Autore - <b>{}</b>\n🗓 Data - <b>{}</b>\n\n<i>{}</i>\n{} - {}/5
        """,
        "en": """
               🍣 <b>TasteIt - Review</b> 🍝\n\n 💁🏼‍♂️ Author - <b>{}</b>\n🗓 Date - <b>{}</b>\n\n<i>{}</i>\n{} - {}/5
        """,
    },
    "GENERAL_ShowCategories": {
        "it": """
               Le tue liste:
        """,
        "en": """
               Your lists:
        """,
    },
    "GENERAL_ChoseListName": {
        "it": """
               Che nome vuoi dare alla lista?
        """,
        "en": """
               What name do you want to give the list?
        """,
    },
    "GENERAL_RestaurantAddedToList": {
        "it": """
               Il ristorante è stato aggiunto con successo alla lista.
        """,
        "en": """
               The restaurant has been added succesfully to the list.
        """,
    },
    "GENERAL_AddToFavorites": {
        "it": """
               📄 Aggiungi ai preferiti
        """,
        "en": """
               📄 Adds to favorites
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
                 Per favore, scegli una delle opzioni disponibili prima di continuare.
              """,
        "en": """
                 Please, chose an available option from the above ones before continuing.
              """,
    },
    "ERROR_GoogleCriticalError": {
        "it": """
                 Errore critico. Contatta lo sviluppatore (@paolino_x), notificando GOOGLE_ERROR.
              """,
        "en": """
                 A critical error has occured. Please contact the developer (@paolino_x), notifing GOOGLE_ERROR.
              """,
    },
    "ERROR_NoPlacesFound": {
        "it": """
                 Nessun posto trovato. Riprova inviandomi un nuovo nome di località o la tua posizione attuale.
              """,
        "en": """
                 No places found. Please, send me back another location name or your current position.
              """,
    },
    "ERROR_NoRestaurantsFound": {
        "it": """
                 Nessun ristorante trovato con i parametri specificati. Prova ad iniziare una nuova ricerca.
              """,
        "en": """
                 No restaurants found with the specified parameters. Try starting a new research.
              """,
    },
    "ERROR_InsufficientPollOptions": {
        "it": """
                 I sondaggi non sono creabili se sono presenti meno 2 di opzioni nella lista.
              """,
        "en": """
                 Cannot create a poll with less than 2 options in the restaurants list.
              """,
    },
    "ERROR_InvalidPosition": {
        "it": """
                 Posizione invalida, inviami nuovamente la tua posizione o il nome di una località di interesse.
              """,
        "en": """
                 Invalid position\. Please, send me back again a location name of your interest or your current position.
              """,
    },
    "ERROR_TimetableNotAvailable": {
        "it": """
                 <i>Orario non disponibile.</i>
              """,
        "en": """
                 <i>Timetable not available.</i>
              """,
    },
    "ERROR_PhoneNumberNotAvailable": {
        "it": """
                 <i>Numero di telefono non disponibile.</i>
              """,
        "en": """
                 <i>Phone number not available.</i>
              """,
    },
    "ERROR_UnableToCreateFavoriteList": {
        "it": """
                 <i>Impossibile creare la lista preferiti desiderata.</i>
              """,
        "en": """
                 <i>Impossible to create the favorite list.</i>
              """,
    },
}


def getString(stringName: str, language: str, *args) -> str:
    if stringName.startswith("GENERAL"):
        return GENERAL_STRINGS.get(stringName).get(language).format(*args)
    else:
        return ERROR_STRINGS.get(stringName).get(language).format(*args)
