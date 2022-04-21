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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

import utils
from STRINGS_LIST import getString
from tools.verify_bot_data import verifyChatData
from data import fetchCategories, fetchFavoriteListContent
from utils.restaurant import Restaurant, RestaurantList

FAV_LIST_DISPLAYED, RESTAURANT_INFOS_DISPLAY = range(2)


def displayFavoritesLists(update: Update, context: CallbackContext) -> int:
    """Function triggered with the `/preferiti` command

    Send a message to the user with a keyboard containing all his favorite lists attached.
    """
    verifyChatData(update, context)

    # Fetching from the database all the favorite lists of the current user.
    currentUserFavoriteLists = fetchCategories(update.effective_chat.id)

    # Creating the effective keyboard. If currentUserFavoriteLists contains some values, they
    # will be displayed one foreach row. Otherwise an info message displaying that there are no
    # lists is sent.
    if len(currentUserFavoriteLists) > 0:
        keyboard = []
        for favoriteList in currentUserFavoriteLists:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=favoriteList.category, callback_data=favoriteList.id
                    )
                ]
            )
        # To stop the current conversation we also add a stop button.
        keyboard.append([InlineKeyboardButton(text="❌", callback_data="end")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Sending the message with all the user's favorites lists attached.
        # The message id is saved in the chat data so it's possible to edit this
        # message in the future steps of the conversation.
        favoriteListsMessageId = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=getString("GENERAL_ShowCategories", context.chat_data.get("lang")),
            reply_markup=reply_markup,
        ).message_id
        context.chat_data.update({"fav_list_message_id": favoriteListsMessageId})

        return FAV_LIST_DISPLAYED
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=getString("ERROR_NoListsAvailable", context.chat_data.get("lang")),
        )

        # Ends the current conversation.
        return endFavoriteListsConversation


def pickedList(update: Update, context: CallbackContext) -> int:
    """Fetches all the restaurants present in the picked list and display them to the user."""
    verifyChatData(update, context)

    query = update.callback_query
    query.answer()

    # Getting the listId of the list of which the user wants to fetch the restaurants.
    listId = update.callback_query.data
    pickedFavoriteListContent: RestaurantList = fetchFavoriteListContent(listId)

    # If the list is empty, we display an error message and we show again the list of favorites lists.
    # Otherwise a fancy looking interface will be sent to the user to navigate through his favorite restaurants
    # of the selected list.
    if pickedFavoriteListContent.size == 0:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=getString("ERROR_EmptyList", context.chat_data.get("lang")),
        )

        return displayFavoritesLists(update, context)
    else:
        context.chat_data.update(
            {"current_list_restaurants": pickedFavoriteListContent}
        )

        return showCurrentFavRestaurant(update, context)


def showCurrentFavRestaurant(update: Update, context: CallbackContext) -> int:
    """Shows detailed infos about the current restaurant of the list."""
    verifyChatData(update, context)

    currentPlace: Restaurant = context.chat_data.get("current_list_restaurants").current
    # Creating the keyboard to attach to the display restaurants message:
    #   by clicking 🌐                 the user will open the restaurant's website if present, otherwise it links google.com;
    #   by clicking 🗺                 the user will be redirected to google maps to start its navigation;
    #   by clicking ⭐️                 the user will be able to see all the restaurant's reviews;
    #   by clicking ⬅️                 the prev restaurant of the list will be displayed
    #   by clicking ➡️                 the next restaurant of the list will be displayed
    #   by clicking ↩️                 the user get back to the favorites lists' list;
    #   by clicking ❌                 the conversation will end.
    keyboard = [
        [
            InlineKeyboardButton(text="⬅️", callback_data="PREV_RESTAURANT"),
            InlineKeyboardButton(text="🌐", url=f"{currentPlace.website}"),
            InlineKeyboardButton(text="🗺️", url=f"{currentPlace.maps}"),
            InlineKeyboardButton(text="⭐️", callback_data="VIEW_REVIEWS"),
            InlineKeyboardButton(text="➡️", callback_data="NEXT_RESTAURANT"),
        ],
        [
            InlineKeyboardButton(
                text=getString(
                    "GENERAL_RemoveRestaurantFromList", context.chat_data.get("lang")
                ),
                callback_data="REMOVE_RESTAURANT_FROM_LIST",
            ),
            InlineKeyboardButton(
                text=getString("GENERAL_DeleteList", context.chat_data.get("lang")),
                callback_data="DELETE_LIST",
            ),
        ],
        [
            InlineKeyboardButton(text="↩", callback_data="BACK_TO_LIST"),
            InlineKeyboardButton(text="❌", callback_data="end"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("fav_list_message_id"),
        text=getString(
            "GENERAL_DetailedInfoOfRestaurant",
            context.chat_data.get("lang"),
            currentPlace.name,
            currentPlace.maps,
            currentPlace.address,
            currentPlace.phone,
            currentPlace.phone,
            currentPlace.price,
            "⭐️" * round(currentPlace.rating)
            + " <b><i>{}</i></b>/5".format(str(currentPlace.rating)),
            "<i>{}</i>".format(str(currentPlace.ratingsnumber)),
            currentPlace.timetable,
        ),
        reply_markup=reply_markup,
    )
    return RESTAURANT_INFOS_DISPLAY


def showNextFavRestaurant(update: Update, context: CallbackContext) -> int:
    """Shows detailed infos about the next restaurant of the list."""
    query = update.callback_query
    query.answer()

    context.chat_data.get("current_list_restaurants").setCurrentElementWithHisNext()

    return showCurrentFavRestaurant(update, context)


def showPrevFavRestaurant(update: Update, context: CallbackContext) -> int:
    """Shows detailed infos about the prev restaurant of the list."""
    query = update.callback_query
    query.answer()

    context.chat_data.get("current_list_restaurants").setCurrentElementWithHisPrev()

    return showCurrentFavRestaurant(update, context)


def backToFavListsList(update: Update, context: CallbackContext) -> int:
    """Exit from the current favorite list display phase and display back all the favorites lists of the user."""
    query = update.callback_query
    query.answer()

    # Popping the current list of data from the chat_data and deleting the previous message.
    context.chat_data.pop("current_list_restaurants")
    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("fav_list_message_id"),
    )

    return displayFavoritesLists(update, context)


def showFavoriteRestaurantReviews(update: Update, context: CallbackContext) -> int:
    """Shows the current restaurant reviews."""
    # TODO: fetch reviews from google and display them. @see search_restaurant.py
    print("printing reviews")


def removeRestaurantFromList(update: Update, context: CallbackContext) -> int:
    """Removes the current restaurant from the current preferred list."""
    print("removing the restaurant from the list")
    # TODO: implement this function


def deleteFavoriteList(update: Update, context: CallbackContext) -> int:
    """Deletes the current favorite list from the database."""
    print("removing the list from the db")
    # TODO: implement this function


def endFavoriteListsConversation(update: Update, context: CallbackContext) -> int:
    """Ends the display favorites lists conversation.

    Returns:
        int: end-code for ConversationHandler
    """
    # This function can both be called by an InlineKeyboardButton and by a command, so we try to answer the callback_query
    try:
        query = update.callback_query
        query.answer()
    except:
        pass

    if context.chat_data.get("fav_list_message_id") != None:
        context.chat_data.pop("fav_list_message_id")
    if context.chat_data.get("current_list_restaurants") != None:
        context.chat_data.pop("current_list_restaurants")

    return utils.cancelConversation(update=update, context=context)
