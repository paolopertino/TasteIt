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

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from requests import get
from string import capwords
from json import loads
from sys import path

from custom_exceptions import GoogleCriticalErrorException, NoPlaceFoundException
from utils.general_place import GeneralPlace

path.append("..")

from STRINGS_LIST import getString

from tools import verifyChatData
import utils

SELECT_STARTING_POSITION, SELECT_FOOD, CHECK_SEARCH_INFO = range(3)


def startSearch(update: Update, context: CallbackContext):
    """Send message on `/cerca`."""
    verifyChatData(update=update, context=context)

    searchMessage = update.message.reply_text(
        getString("GENERAL_SendRequiredPositionInfos", context.chat_data.get("lang")),
    )

    # The conversation continue by modifing the first message sent by the bot.
    # Therefore the message id is stored.
    context.chat_data.update({"search_message_id": searchMessage.message_id})

    # Tell ConversationHandler that we're in state `CHOSEN` now
    return SELECT_STARTING_POSITION


def searchLocationByName(update: Update, context: CallbackContext):
    """Based on the input given by the user, it search for a location which match."""
    verifyChatData(update=update, context=context)

    inputUserText = update.message.text
    context.bot.delete_message(update.message.chat_id, update.message.message_id)

    try:
        placesFound = __getPlaces(inputUserText)
    except NoPlaceFoundException:
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("search_message_id"),
            text=getString("ERROR_NoPlacesFound", context.chat_data.get("lang")),
        )

        return SELECT_STARTING_POSITION
    except GoogleCriticalErrorException:
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("search_message_id"),
            text=getString("ERROR_GoogleCriticalError", context.chat_data.get("lang")),
        )

        endSearchConversation(update=update, context=context)
    else:
        # Setting up the research info. This object will be used to store useful informations of the parameters used for the restaurant research.
        searchInfos = utils.ResearchInfo()
        searchInfos.location = utils.GeneralPlace(
            placesFound.get("candidates")[0].get("name"),
            placesFound.get("candidates")[0].get("geometry").get("location").get("lat"),
            placesFound.get("candidates")[0].get("geometry").get("location").get("lng"),
        )
        context.chat_data.update({"research_info": searchInfos})

        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("search_message_id"),
            text=getString(
                "GENERAL_SearchRestaurantStartingLocation",
                context.chat_data.get("lang"),
                searchInfos.location,
            ),
        )

        return SELECT_FOOD


def searchLocationByPosition(update: Update, context: CallbackContext):
    verifyChatData(update=update, context=context)

    userPosition = update.message.location
    context.bot.delete_message(update.message.chat_id, update.message.message_id)

    if userPosition != None:
        searchInfos = utils.ResearchInfo()
        searchInfos.location = GeneralPlace(
            "PERSONAL_POS",
            userPosition.latitude,
            userPosition.longitude,
        )
        context.chat_data.update({"research_info": searchInfos})

        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("search_message_id"),
            text=getString(
                "GENERAL_SearchRestaurantCurrentPositionAccepted",
                context.chat_data.get("lang"),
            ),
        )

        return SELECT_FOOD
    else:
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("search_message_id"),
            text=getString(
                "ERROR_InvalidPosition",
                context.chat_data.get("lang"),
            ),
        )

        return SELECT_STARTING_POSITION


def selectFood(update: Update, context: CallbackContext):
    verifyChatData(update=update, context=context)

    selectedFood = update.message.text
    context.bot.delete_message(update.message.chat_id, update.message.message_id)

    searchInfo = context.chat_data.get("research_info")
    searchInfo.food = selectedFood

    keyboard = [
        [
            InlineKeyboardButton("🍝", callback_data="CHANGE_FOOD"),
            InlineKeyboardButton("🕧", callback_data="CHANGE_TIME"),
            InlineKeyboardButton("💶", callback_data="CHANGE_PRICE"),
        ],
        [
            InlineKeyboardButton("🔎", callback_data="SEARCH"),
            InlineKeyboardButton("❌", callback_data="end"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("search_message_id"),
        text=getString(
            "GENERAL_SearchRestaurantInfoRecap",
            context.chat_data.get("lang"),
            searchInfo.food,
            "✅" if searchInfo.opennow == True else "❌",
            "€" * searchInfo.cost,
        ),
        reply_markup=reply_markup,
    )

    return CHECK_SEARCH_INFO


# TODO: make changeFunctions
def changeFood(update: Update, context: CallbackContext):
    print("changing food")


def changeTime(update: Update, context: CallbackContext):
    print("changing time")


def changePrice(update: Update, context: CallbackContext):
    print("changing price")


def searchRestaurant(update: Update, context: CallbackContext):
    print("searching restaurant")


def __getPlaces(textQuery: str) -> list:
    formattedText = __formatInputText(textQuery)

    googleKey = utils.ApiKey(utils.Service.GOOGLE_PLACES).value
    googleResult = get(
        f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?fields=name%2Cgeometry&input={formattedText}&inputtype=textquery&key={googleKey}"
    )
    googleResult.raise_for_status()

    # Parsing google response (json) to dictionary
    googleResult = loads(googleResult.text)

    if googleResult.get("status") == "OK":
        return googleResult
    elif googleResult.get("status") == "ZERO_RESULTS":
        raise NoPlaceFoundException(textQuery, "Place not found")
    else:
        raise GoogleCriticalErrorException(
            "Google critical error; check the google key status."
        )


def __formatInputText(textToFormat: str) -> str:
    return textToFormat.replace(" ", "%20")


def endSearchConversation(update: Update, context: CallbackContext):
    """Ends the search conversation.

    Returns:
        int: end-code for ConversationHandler
    """
    if context.chat_data.get("search_message_id") != None:
        context.chat_data.pop("search_message_id")
    if context.chat_data.get("research_info") != None:
        context.chat_data.pop("research_info")

    return utils.cancelConversation(update=update, context=context)
