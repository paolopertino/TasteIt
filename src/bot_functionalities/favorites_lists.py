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
from requests import get
from json import loads

import utils
from STRINGS_LIST import getString
from tools.verify_bot_data import verifyChatData
from data import (
    fetchCategories,
    fetchFavoriteListContent,
    removeRestaurantFromListDb,
    removeFavoriteListFromDb,
)
from utils.api_key import Service, ApiKey
from utils.favorite_list import FavoriteList
from utils.rating import Rating, RatingsList
from utils.restaurant import Restaurant, RestaurantList

FAV_LIST_DISPLAYED, RESTAURANT_INFOS_DISPLAY, NAVIGATE_REVIEWS = range(3)


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
    # We create a new FavoriteList object. At this point we do not care anymore of the caregory since
    # in the next steps is not used anymore.
    favoriteListPickedId = update.callback_query.data
    favoriteListPicked: FavoriteList = FavoriteList(int(favoriteListPickedId), "_")
    favoriteListPicked.restaurants = fetchFavoriteListContent(favoriteListPicked.id)

    # If the list is empty, we display an error message and we show again the list of favorites lists.
    # Otherwise a fancy looking interface will be sent to the user to navigate through his favorite restaurants
    # of the selected list.
    if favoriteListPicked.restaurants.size == 0:
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("fav_list_message_id"),
            text=getString(
                "ERROR_EmptyList",
                context.chat_data.get("lang"),
            ),
        )
        # newId = context.bot.send_message(
        #     chat_id=update.effective_chat.id,
        #     text="_",
        # )
        # context.chat_data.update({"fav_list_message_id": newId})

        return displayFavoritesLists(update, context)
    else:
        context.chat_data.update({"current_list_restaurants": favoriteListPicked})

        return showCurrentFavRestaurant(update, context)


def showCurrentFavRestaurant(update: Update, context: CallbackContext) -> int:
    """Shows detailed infos about the current restaurant of the list."""
    verifyChatData(update, context)

    # If there are restaurants in the list they will be displayed, otherwise an error message will be sent
    # and the list of favorites lists will be displayed again.
    if context.chat_data.get("current_list_restaurants").restaurants.size > 0:
        currentPlace: Restaurant = context.chat_data.get(
            "current_list_restaurants"
        ).restaurants.current
        # Creating the keyboard to attach to the display restaurants message:
        #   by clicking 🌐                 the user will open the restaurant's website if present, otherwise it links google.com;
        #   by clicking 📍                 the user will be redirected to google maps to start its navigation;
        #   by clicking ⭐️                 the user will be able to see all the restaurant's reviews;
        #   by clicking ⬅️                 the prev restaurant of the list will be displayed
        #   by clicking ➡️                 the next restaurant of the list will be displayed
        #   by clicking GENERAL_PollButton GROUPS ONLY - a poll with the restaurants in the current list is started
        #   by clicking ↩️                 the user get back to the favorites lists' list;
        #   by clicking ❌                 the conversation will end.
        if (
            update.effective_chat.type == "group"
            or update.effective_chat.type == "supergroup"
        ):

            keyboard = [
                [
                    InlineKeyboardButton(text="⬅️", callback_data="PREV_RESTAURANT"),
                    InlineKeyboardButton(text="🌐", url=f"{currentPlace.website}"),
                    InlineKeyboardButton(text="📍", url=f"{currentPlace.maps}"),
                    InlineKeyboardButton(text="⭐️", callback_data="VIEW_REVIEWS"),
                    InlineKeyboardButton(text="➡️", callback_data="NEXT_RESTAURANT"),
                ],
                [
                    InlineKeyboardButton(
                        text=getString(
                            "GENERAL_PollButton", context.chat_data.get("lang")
                        ),
                        callback_data="START_POLL",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=getString(
                            "GENERAL_RemoveRestaurantFromList",
                            context.chat_data.get("lang"),
                        ),
                        callback_data="REMOVE_RESTAURANT_FROM_LIST",
                    ),
                    InlineKeyboardButton(
                        text=getString(
                            "GENERAL_DeleteList", context.chat_data.get("lang")
                        ),
                        callback_data="DELETE_LIST",
                    ),
                ],
                [
                    InlineKeyboardButton(text="↩", callback_data="BACK_TO_LIST"),
                    InlineKeyboardButton(text="❌", callback_data="end"),
                ],
            ]
        else:
            keyboard = [
                [
                    InlineKeyboardButton(text="⬅️", callback_data="PREV_RESTAURANT"),
                    InlineKeyboardButton(text="🌐", url=f"{currentPlace.website}"),
                    InlineKeyboardButton(text="📍", url=f"{currentPlace.maps}"),
                    InlineKeyboardButton(text="⭐️", callback_data="VIEW_REVIEWS"),
                    InlineKeyboardButton(text="➡️", callback_data="NEXT_RESTAURANT"),
                ],
                [
                    InlineKeyboardButton(
                        text=getString(
                            "GENERAL_RemoveRestaurantFromList",
                            context.chat_data.get("lang"),
                        ),
                        callback_data="REMOVE_RESTAURANT_FROM_LIST",
                    ),
                    InlineKeyboardButton(
                        text=getString(
                            "GENERAL_DeleteList", context.chat_data.get("lang")
                        ),
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
    else:
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("fav_list_message_id"),
            text=getString("ERROR_EmptyList", context.chat_data.get("lang")),
        )

        return displayFavoritesLists(update, context)


def showNextFavRestaurant(update: Update, context: CallbackContext) -> int:
    """Shows detailed infos about the next restaurant of the list."""
    query = update.callback_query
    query.answer()

    # If there is only one element there is no reason to move from the current state
    if context.chat_data.get("current_list_restaurants").restaurants.size > 1:
        context.chat_data.get(
            "current_list_restaurants"
        ).restaurants.setCurrentElementWithHisNext()

        return showCurrentFavRestaurant(update, context)


def showPrevFavRestaurant(update: Update, context: CallbackContext) -> int:
    """Shows detailed infos about the prev restaurant of the list."""
    query = update.callback_query
    query.answer()

    # If there is only one element there is no reason to move from the current state
    if context.chat_data.get("current_list_restaurants").restaurants.size > 1:
        context.chat_data.get(
            "current_list_restaurants"
        ).restaurants.setCurrentElementWithHisPrev()

        return showCurrentFavRestaurant(update, context)


def startPoll(update: Update, context: CallbackContext):
    """Starts a poll in a group chat with the current favorites list."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Getting a copy of the current restaurants list.
    restaurantsList: RestaurantList = context.chat_data.get(
        "current_list_restaurants"
    ).restaurants.clone()

    if restaurantsList.size < 2:
        # Cannot create a poll with less than 2 options
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("fav_list_message_id"),
            text=getString(
                "ERROR_InsufficientPollOptions", context.chat_data.get("lang")
            ),
        )
        newMessageId = context.bot.send_message(
            chat_id=update.effective_chat.id, text="_"
        ).message_id
        context.chat_data.update({"fav_list_message_id": newMessageId})

        return showCurrentFavRestaurant(update, context)
    elif restaurantsList.size > 10:
        # Due to telegram internal limits, poll cannot have more than 10 possible choices
        numberOfPollChoices = 10
    else:
        # If  2 <= restaurantsList.size <= 10, than we display only those options
        numberOfPollChoices = restaurantsList.size

    # Compiling the poll choices with the restaurants names starting from the current one.
    pollChoices: list = []
    for i in range(numberOfPollChoices):
        pollChoices.append(restaurantsList.current.name)
        restaurantsList.setCurrentElementWithHisNext()

    # Sending the poll. After 1 minute it will automatically close.
    context.bot.send_poll(
        update.effective_chat.id,
        getString("GENERAL_PollStarted", context.chat_data.get("lang")),
        pollChoices,
        is_anonymous=False,
        allows_multiple_answers=False,
        open_period=60,
    )
    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("fav_list_message_id"),
    )
    newMessageId = context.bot.send_message(
        chat_id=update.effective_chat.id, text="_"
    ).message_id
    context.chat_data.update({"fav_list_message_id": newMessageId})
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
    verifyChatData(update, context)

    query = update.callback_query
    query.answer()

    currentRestaurant: Restaurant = context.chat_data.get(
        "current_list_restaurants"
    ).restaurants.current
    # If the current restaurant hasn't any review fetched, we try to fetch them.
    if currentRestaurant.reviews.size == 0:
        currentRestaurant.reviews = __fetchRestaurantReviews(
            currentRestaurant.id, context.chat_data.get("lang")
        )

    # Printing currentRestaurant reviews to the user if present. Otherwise an error message is sent.
    if currentRestaurant.reviews.size != 0:
        restaurantCurrentReview: Rating = currentRestaurant.reviews.current
        # Creating the keyboard to attach to the display restaurants message:
        #   by clicking ⬅️                 the user will switch to the previous review of the list;
        #   by clicking ➡️                 the user will switch to the next review of the list;
        #   by clicking ↩️                 the user get back to the detailed informations message;
        #   by clicking ❌                 the conversation will end.
        keyboard = [
            [
                InlineKeyboardButton("⬅️", callback_data="PREV_REVIEW"),
                InlineKeyboardButton("➡️", callback_data="NEXT_REVIEW"),
            ],
            [
                InlineKeyboardButton(
                    text="↩️ Info", callback_data="BACK_TO_DETAILED_INFO"
                ),
                InlineKeyboardButton(text="❌", callback_data="end"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("fav_list_message_id"),
            text=getString(
                "GENERAL_ReviewContent",
                context.chat_data.get("lang"),
                restaurantCurrentReview.author,
                restaurantCurrentReview.date,
                restaurantCurrentReview.content,
                "⭐️" * round(restaurantCurrentReview.rating),
                restaurantCurrentReview.rating,
            ),
            reply_markup=reply_markup,
        )

        # The NAVIGATE_REVIEWS state allows the user to switch between reviews handling prev&next button callbacks.
        return NAVIGATE_REVIEWS
    else:
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("fav_list_message_id"),
            text=getString("ERROR_NoReviewsAvailable", context.chat_data.get("lang")),
        )

        # Sending a new empty message which will be overwritten immediately by going back to the RESTAURANT_INFOS_DISPLAY state.
        newId = context.bot.send_message(
            chat_id=update.effective_chat.id, text="_"
        ).message_id
        # Storing the new id which will be used from now on to modify the message.
        context.chat_data.update({"fav_list_message_id": newId})

        return showCurrentFavRestaurant(update, context)


def showNextReviewOfFavRestaurant(update: Update, context: CallbackContext) -> int:
    """Updates the current element of the reviews list with its next, and shows that review."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # If there is only one element there is no reason to move from the current state
    if (
        context.chat_data.get(
            "current_list_restaurants"
        ).restaurants.current.reviews.size
        > 1
    ):
        context.chat_data.get(
            "current_list_restaurants"
        ).restaurants.current.reviews.setCurrentElementWithHisNext()
        return showFavoriteRestaurantReviews(update, context)


def showPrevReviewOfFavRestaurant(update: Update, context: CallbackContext) -> int:
    """Updates the current element of the reviews list with its previous, and shows that review."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # If there is only one element there is no reason to move from the current state
    if (
        context.chat_data.get(
            "current_list_restaurants"
        ).restaurants.current.reviews.size
        > 1
    ):
        context.chat_data.get(
            "current_list_restaurants"
        ).restaurants.current.reviews.setCurrentElementWithHisPrev()

        return showFavoriteRestaurantReviews(update, context)


def removeRestaurantFromList(update: Update, context: CallbackContext) -> int:
    """Removes the current restaurant from the current preferred list."""
    query = update.callback_query
    query.answer()

    # Removing the restaurant from the list in the database
    removeRestaurantFromListDb(
        context.chat_data.get("current_list_restaurants").restaurants.current.id,
        context.chat_data.get("current_list_restaurants").id,
    )

    # Removing the restaurant even from the local list
    context.chat_data.get("current_list_restaurants").restaurants.remove()

    # Sending a message of success and displaying back the updated list.
    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("fav_list_message_id"),
        text=getString(
            "GENERAL_RestaurantRemovedFromFavList", context.chat_data.get("lang")
        ),
    )

    # Sending a new empty message which will be overwritten immediately by going back to the RESTAURANT_INFOS_DISPLAY state.
    newId = context.bot.send_message(
        chat_id=update.effective_chat.id, text="_"
    ).message_id
    # Storing the new id which will be used from now on to modify the message.
    context.chat_data.update({"fav_list_message_id": newId})

    return showCurrentFavRestaurant(update, context)


def deleteFavoriteList(update: Update, context: CallbackContext) -> int:
    """Deletes the current favorite list from the database."""
    query = update.callback_query
    query.answer()

    # Removing all the entries of the assosciation between the current restaurant and the list in the restaurant_for_list table
    # in the database
    for restaurant in context.chat_data.get("current_list_restaurants").restaurants:
        removeRestaurantFromListDb(
            restaurant.id, context.chat_data.get("current_list_restaurants").id
        )

    # Removing the list from the database
    removeFavoriteListFromDb(context.chat_data.get("current_list_restaurants").id)

    # Popping out the list from chat data and returning the list of lists and deleting the message with fav_list_message_id id.
    context.chat_data.pop("current_list_restaurants")
    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("fav_list_message_id"),
    )
    context.chat_data.pop("fav_list_message_id")

    return displayFavoritesLists(update, context)


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


def __fetchRestaurantReviews(restaurantId: str, lang: str) -> RatingsList:
    """Fetches the reviews of the restaurant with the restaurantId provided written in the lang language.

    Args:
        restaurantId (str): the id of the restaurant of which we want to fetch the reviews
        lang (str): the language in which the reviews should be written

    Returns:
        RatingsList: the list of all the restaurant reviews
    """
    result: RatingsList = RatingsList()

    googleKey = ApiKey(Service.GOOGLE_PLACES).value
    # Fetching detailed information of a restaurant
    googleResult = get(
        f"https://maps.googleapis.com/maps/api/place/details/json?fields=reviews&language={lang}&place_id={restaurantId}&key={googleKey}"
    )
    googleResult.raise_for_status()

    googleResult = loads(googleResult.text)

    for review in googleResult.get("result").get("reviews"):
        result.add(
            Rating(
                review.get("author_name"),
                review.get("rating"),
                review.get("text"),
                review.get("time"),
            )
        )

    return result
