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

from telegram import (
    ReplyKeyboardMarkup,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import CallbackContext, ConversationHandler
from requests import get
from string import capwords
from json import loads
from sys import path
from geopy.distance import geodesic
from time import strftime, gmtime

from data import (
    fetchCategories,
    insertList,
    insertRestaurantInfos,
    insertRestaurantIntoList,
    fetchResearchRadius,
)
from tools import verifyChatData
import utils
from utils import research_info
from utils.general_place import GeneralPlace
from utils.rating import Rating
from utils.research_info import ResearchInfo
from utils.restaurant import Restaurant, RestaurantList
from custom_exceptions import GoogleCriticalErrorException, NoPlaceFoundException
from STRINGS_LIST import getString

path.append("..")


(
    SELECT_STARTING_POSITION,
    SELECT_FOOD,
    PICK_PRICE,
    CHECK_SEARCH_INFO,
    VIEW_SEARCH_RESULTS,
    DETAILED_INFO,
    VIEW_REVIEWS,
    FAVORITE_LIST_PICK_STATE,
    FAVORITE_LIST_CREATE_STATE,
) = range(9)


def startSearch(update: Update, context: CallbackContext) -> int:
    """Send a message on `/cerca`."""
    verifyChatData(update=update, context=context)

    searchMessage = update.message.reply_text(
        getString("GENERAL_SendRequiredPositionInfos", context.chat_data.get("lang")),
    )

    # The conversation continue by modifing the first message sent by the bot.
    # Therefore the message id is stored.
    context.chat_data.update({"search_message_id": searchMessage.message_id})

    # Tell ConversationHandler that we're in state `CHOSEN` now
    return SELECT_STARTING_POSITION


def searchLocationByName(update: Update, context: CallbackContext) -> int:
    """Based on the input given by the user, it search for a location which match."""
    verifyChatData(update=update, context=context)

    # Fetching the user input and deleting his message to keep the chat clear
    inputUserText = update.message.text
    context.bot.delete_message(update.message.chat_id, update.message.message_id)

    try:
        # Fetching from google the places with the given name
        placesFound = __getPlaces(inputUserText)
    except NoPlaceFoundException:
        # Thrown if there are no location with the given name
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("search_message_id"),
            text=getString("ERROR_NoPlacesFound", context.chat_data.get("lang")),
        )

        # The user can retry to insert a new location or send his position
        return SELECT_STARTING_POSITION
    except GoogleCriticalErrorException:
        # Thrown when an error from google internal apis occours.
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=getString("ERROR_GoogleCriticalError", context.chat_data.get("lang")),
        )

        # In this case the conversation will immediately stop
        return endSearchConversation(update=update, context=context)
    else:
        # Setting up the research info. This object will be used to store useful informations of the parameters used for the restaurant research.
        # We take the first candidate since it is most likely the one preferred by the user.
        searchInfos = utils.ResearchInfo()
        searchInfos.location = utils.GeneralPlace(
            placesFound.get("candidates")[0].get("name"),
            placesFound.get("candidates")[0].get("geometry").get("location").get("lat"),
            placesFound.get("candidates")[0].get("geometry").get("location").get("lng"),
        )

        # Putting the fetched location in the chat_data dictionary in order to access it for future uses.
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

        # Once the starting location is chosen (if chosen by name) the FSM moves to the SELECT_FOOD state where the user can choose
        # the food he wants to eat.
        return SELECT_FOOD


def searchLocationByPosition(update: Update, context: CallbackContext) -> int:
    """Based on the current position of the user, it saves latitude and longitude in `chat_data` as a `GeneralPlace` and moves the FSM to `SELECT_FOOD` state."""
    verifyChatData(update=update, context=context)

    # Fetching the user position by the location message sent and deleting his message to keep the chat clear.
    userPosition = update.message.location
    context.bot.delete_message(update.message.chat_id, update.message.message_id)

    if userPosition != None:
        # If the position is valid we fetch latitude and longitude
        searchInfos = utils.ResearchInfo()
        searchInfos.location = GeneralPlace(
            "PERSONAL_POS",
            userPosition.latitude,
            userPosition.longitude,
        )

        # Putting the fetched location in the chat_data dictionary in order to access it for future uses.
        context.chat_data.update({"research_info": searchInfos})

        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("search_message_id"),
            text=getString(
                "GENERAL_SearchRestaurantCurrentPositionAccepted",
                context.chat_data.get("lang"),
            ),
        )

        # Once the starting location is chosen (if chosen by current position) the FSM moves to the SELECT_FOOD state where the user can choose
        # the food he wants to eat.
        return SELECT_FOOD
    else:
        # If the position is invalid, the user can try again by sending another location message or by sending a location name.
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("search_message_id"),
            text=getString(
                "ERROR_InvalidPosition",
                context.chat_data.get("lang"),
            ),
        )

        return SELECT_STARTING_POSITION


def selectFood(update: Update, context: CallbackContext) -> int:
    """Selected the food, setup the recap message before the actual research"""
    verifyChatData(update=update, context=context)

    # Fetching the selected food by the user and deleting his message to keep the chat clean
    selectedFood: str = update.message.text
    context.bot.delete_message(update.message.chat_id, update.message.message_id)

    # Updating the research infos with the food selected by the user
    searchInfo: ResearchInfo = context.chat_data.get("research_info")
    searchInfo.food = selectedFood

    return showRecapMessage(update, context)


def showRecapMessage(update: Update, context: CallbackContext):
    """Update the search message with recap informations."""
    verifyChatData(update=update, context=context)

    searchInfo: ResearchInfo = context.chat_data.get("research_info")

    # Creating the keyboard to attach to the recap message:
    #   by clicking 🍝 the user will be able to chose the food again;
    #   by clicking 🕧 the user will switch the openNow parameter between true and false;
    #   by clicking 💶 the user will be able to set his max price preference (from 1 to 5 according to his expensiveness preferences);
    #   by clicking 🔎 the restaurant research will actually begin;
    #   by clicking ❌ the conversation will end.

    keyboard = [
        [
            InlineKeyboardButton("🍝", callback_data="CHANGE_FOOD"),
            InlineKeyboardButton("🕧", callback_data="CHANGE_TIME"),
            InlineKeyboardButton("💶", callback_data="CHANGE_PRICE"),
            InlineKeyboardButton(
                "🚙" if searchInfo.walkingdistance == True else "🚶‍♂️",
                callback_data="CHANGE_DISTANCE",
            ),
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
            getString(
                "GENERAL_ReachableOnFoot",
                context.chat_data.get("lang"),
                round(
                    float(
                        fetchResearchRadius(update.effective_chat.id, True)[0] / 1000
                    ),
                    2,
                ),
            )
            if searchInfo.walkingdistance == True
            else getString(
                "GENERAL_ReachableByCar",
                context.chat_data.get("lang"),
                round(
                    float(
                        fetchResearchRadius(update.effective_chat.id, False)[0] / 1000
                    ),
                    2,
                ),
            ),
            "€" * searchInfo.cost,
        ),
        reply_markup=reply_markup,
    )

    return CHECK_SEARCH_INFO


def changeDistancePreference(update: Update, context: CallbackContext) -> int:
    """Update the way the user wants to reach the restaurant."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Switching between "by walking" and "by car"
    searchInfo: ResearchInfo = context.chat_data.get("research_info")
    searchInfo.walkingdistance = not (searchInfo.walkingdistance)

    return showRecapMessage(update, context)


def changeFood(update: Update, context: CallbackContext) -> int:
    """Set up the conversation in order to let the user chose again the food he wants to eat."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("search_message_id"),
        text=getString(
            "GENERAL_FoodPreferenceReset",
            context.chat_data.get("lang"),
        ),
    )

    return SELECT_FOOD


def changeTime(update: Update, context: CallbackContext):
    """Set up the conversation in order to let the user chose again the openNow parameter."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Actually inverting the openNow parameter in the research info stored object.
    context.chat_data.get("research_info").opennow = not (
        context.chat_data.get("research_info").opennow
    )

    return showRecapMessage(update, context)


def changePrice(update: Update, context: CallbackContext) -> int:
    """Set up the conversation in order to let the user chose again the max price value."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Creating the keyboard to attach to the 'change price' message:
    #   by clicking €       the price limit will be set to 1;
    #   by clicking €€      the price limit will be set to 2;
    #   by clicking €€€     the price limit will be set to 3;
    #   by clicking €€€€    the price limit will be set to 4;
    #   by clicking €€€€€   the price limit will be set to 5;
    keyboard = [
        [
            InlineKeyboardButton("€", callback_data="1"),
            InlineKeyboardButton("€€", callback_data="2"),
            InlineKeyboardButton("€€€", callback_data="3"),
        ],
        [
            InlineKeyboardButton("€€€€", callback_data="4"),
            InlineKeyboardButton("€€€€€", callback_data="5"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    searchInfo = context.chat_data.get("research_info")

    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("search_message_id"),
        text=getString(
            "GENERAL_SearchRestaurantInfoRecap",
            context.chat_data.get("lang"),
            searchInfo.food,
            "✅" if searchInfo.opennow == True else "❌",
            getString(
                "GENERAL_ReachableOnFoot",
                context.chat_data.get("lang"),
                round(
                    float(
                        fetchResearchRadius(update.effective_chat.id, True)[0] / 1000
                    ),
                    2,
                ),
            )
            if searchInfo.walkingdistance == True
            else getString(
                "GENERAL_ReachableByCar",
                context.chat_data.get("lang"),
                round(
                    float(
                        fetchResearchRadius(update.effective_chat.id, False)[0] / 1000
                    ),
                    2,
                ),
            ),
            "€" * searchInfo.cost,
        ),
        reply_markup=reply_markup,
    )

    return PICK_PRICE


def priceChanged(update: Update, context: CallbackContext):
    """Handles the price change."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Handling the new max price param received and updating the research info object stored with the new value.
    newPrice = int(update.callback_query.data)
    searchInfo = context.chat_data.get("research_info")
    searchInfo.cost = newPrice

    return showRecapMessage(update, context)


def searchRestaurant(update: Update, context: CallbackContext) -> int:
    """Given the research parameters (stored in `chat_data`), it fetches the list of restaurants and display it to the user."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Getting the complete research infos. They will be used to perform the restaurants research.
    searchInfo: ResearchInfo = context.chat_data.get("research_info")

    try:
        # Fetch the restaurants.
        placesFound = __fetchRestaurant(
            update.effective_chat.id, searchInfo, context.chat_data.get("lang")
        )
    except NoPlaceFoundException:
        # Thrown when no restaurants were found with the specfied research informations.
        # In this case the recap will pop back.
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=getString("ERROR_NoRestaurantsFound", context.chat_data.get("lang")),
        )

        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("search_message_id"),
        )
        # Creating a new "empty" message. It will be immediately overridden by showRecapMessage method.
        newMessage = context.bot.send_message(
            chat_id=update.effective_chat.id, text="_"
        )
        context.chat_data.update({"search_message_id": newMessage.message_id})

        # Since no restaurant matched with the given specs, then we reset them to their default value.
        searchInfo.opennow = False
        searchInfo.cost = 3

        return showRecapMessage(update, context)
    except GoogleCriticalErrorException:
        # Thrown when an internal google apis error occur.
        # Also in this case an error message is sent and the conversation immediately ends.
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=getString("ERROR_GoogleCriticalError", context.chat_data.get("lang")),
        )

        return endSearchConversation(update=update, context=context)
    else:
        # If everything has gone fine, a restaurants' list is compiled and stored in chat_data
        fetchedRestaurants = RestaurantList()
        filteredRestaurants = RestaurantList()
        maxRadius = fetchResearchRadius(
            update.effective_chat.id, searchInfo.walkingdistance
        )[0]
        # outOfRangeRestaurants: list = []
        for result in placesFound.get("results"):
            if (
                geodesic(
                    (
                        result.get("geometry").get("location").get("lat"),
                        result.get("geometry").get("location").get("lng"),
                    ),
                    (searchInfo.latitude, searchInfo.longitude),
                ).meters
                <= maxRadius
            ):
                restaurant = Restaurant(
                    result.get("name"),
                    result.get("geometry").get("location").get("lat"),
                    result.get("geometry").get("location").get("lng"),
                    result.get("place_id"),
                    result.get("price_level"),
                    result.get("rating"),
                    result.get("user_ratings_total"),
                )

                # Than we measure the walking or driving distance between the starting position and the destination
                (
                    restaurant.distance,
                    restaurant.reachtime,
                ) = __compileRestaurantReachingParameters(
                    searchInfo.latitude,
                    searchInfo.longitude,
                    restaurant.latitude,
                    restaurant.longitude,
                    "mapbox/walking"
                    if searchInfo.walkingdistance
                    else "mapbox/driving",
                )
                if restaurant.distance <= maxRadius:
                    filteredRestaurants.add(restaurant)

        if filteredRestaurants.size == 0:
            # Thrown when no restaurants were found with the specfied research informations.
            # In this case the recap will pop back.
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=getString(
                    "ERROR_NoRestaurantsFound", context.chat_data.get("lang")
                ),
            )

            context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.chat_data.get("search_message_id"),
            )
            # Creating a new "empty" message. It will be immediately overridden by showRecapMessage method.
            newMessage = context.bot.send_message(
                chat_id=update.effective_chat.id, text="_"
            )
            context.chat_data.update({"search_message_id": newMessage.message_id})

            # Since no restaurant matched with the given specs, then we reset them to their default value.
            searchInfo.opennow = False
            searchInfo.cost = 3

            return showRecapMessage(update, context)
        else:
            context.chat_data.update({"restaurants_list": filteredRestaurants})

            return showCurrentRestaurant(update, context)


def showCurrentRestaurant(update: Update, context: CallbackContext) -> int:
    """Display the current restaurant name and ratings and set up some possible actions."""
    verifyChatData(update=update, context=context)

    # Fetching the list of restaurants
    listOfRestaurants = context.chat_data.get("restaurants_list")

    # Creating the keyboard to attach to the display restaurants message:
    #   by clicking ⬅️                 the user will move to the previous restaurant of the list;
    #   by clicking ➡️                 the user will move to the next restaurant of the list;
    #   by clicking GENERAL_MoreInfos  the user will be able to see detailed informations of the current restaurant;
    #   by clicking GENERAL_PollButton  GROUPS ONLY - a poll with the current restaurants is started
    #   by clicking ❌                 the conversation will end.
    keyboard = (
        [
            [
                InlineKeyboardButton("⬅️", callback_data="PREV_RESTAURANT"),
                InlineKeyboardButton("➡️", callback_data="NEXT_RESTAURANT"),
            ],
            [
                InlineKeyboardButton(
                    getString("GENERAL_MoreInfos", context.chat_data.get("lang")),
                    callback_data="DISPLAY_MORE_INFO",
                ),
            ],
            [
                InlineKeyboardButton(
                    getString("GENERAL_PollButton", context.chat_data.get("lang")),
                    callback_data="START_POLL",
                ),
            ],
            [
                InlineKeyboardButton("❌", callback_data="end"),
            ],
        ]
        if (
            update.effective_chat.type == "group"
            or update.effective_chat.type == "supergroup"
        )
        else [
            [
                InlineKeyboardButton("⬅️", callback_data="PREV_RESTAURANT"),
                InlineKeyboardButton("➡️", callback_data="NEXT_RESTAURANT"),
            ],
            [
                InlineKeyboardButton(
                    getString("GENERAL_MoreInfos", context.chat_data.get("lang")),
                    callback_data="DISPLAY_MORE_INFO",
                ),
            ],
            [
                InlineKeyboardButton("❌", callback_data="end"),
            ],
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Printing the infos of the current element
    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("search_message_id"),
        text=getString(
            "GENERAL_RestaurantInfoDisplay",
            context.chat_data.get("lang"),
            listOfRestaurants.current.name,
            (
                (
                    "🚶‍♂️ - "
                    if (context.chat_data.get("research_info").walkingdistance)
                    else "🚙 - "
                )
                + (
                    (
                        (
                            str(round(listOfRestaurants.current.distance / 1000, 2))
                            + " km"
                        )
                        if listOfRestaurants.current.distance >= 1000
                        else str(round(listOfRestaurants.current.distance))
                        + getString("GENERAL_Meters", context.chat_data.get("lang"))
                    )
                    if listOfRestaurants.current.distance < 100000
                    else "N.A."
                )
            ),
            strftime("%M:%S", gmtime(listOfRestaurants.current.reachtime))
            # str(round(listOfRestaurants.current.reachtime / 60, 2))
            if listOfRestaurants.current.reachtime < 100000 else "N.A.",
            "⭐️" * round(listOfRestaurants.current.rating)
            + " <b><i>{}</i></b>/5".format(str(listOfRestaurants.current.rating)),
            "<i>{}</i>".format(str(listOfRestaurants.current.ratingsnumber)),
        ),
        reply_markup=reply_markup,
    )

    # The state VIEW_SEARCH_RESULTS handles the user possibility to switch between restaurant, to add the current restaurant to his
    # favorites list, to get detailed informations about the current restaurant.
    return VIEW_SEARCH_RESULTS


def showNextRestaurant(update: Update, context: CallbackContext) -> int:
    """Updates the current element of the restaurants list with his next, and shows that restaurant."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Fetching the list of restaurants and picking the next
    # If there is only one element there is no reason to move from the current state
    if context.chat_data.get("restaurants_list").size > 1:
        context.chat_data.get("restaurants_list").setCurrentElementWithHisNext()

        return showCurrentRestaurant(update, context)


def showPrevRestaurant(update: Update, context: CallbackContext) -> int:
    """Updates the current element of the restaurants list with his previous, and shows that restaurant."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Fetching the list of restaurants and picking the next
    # If there is only one element there is no reason to move from the current state
    if context.chat_data.get("restaurants_list").size > 1:
        context.chat_data.get("restaurants_list").setCurrentElementWithHisPrev()

        return showCurrentRestaurant(update, context)


def startPollWithCurrentRestaurant(update: Update, context: CallbackContext):
    """Starts a poll in a group chat with the fetched restaurants."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Getting a copy of the current restaurants list.
    restaurantsList: RestaurantList = context.chat_data.get("restaurants_list").clone()

    if restaurantsList.size < 2:
        # Cannot create a poll with less than 2 options
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("search_message_id"),
            text=getString(
                "ERROR_InsufficientPollOptions", context.chat_data.get("lang")
            ),
        )
        newMessageId = context.bot.send_message(
            chat_id=update.effective_chat.id, text="_"
        ).message_id
        context.chat_data.update({"search_message_id": newMessageId})

        return showCurrentRestaurant(update, context)
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
        message_id=context.chat_data.get("search_message_id"),
    )
    newMessageId = context.bot.send_message(
        chat_id=update.effective_chat.id, text="_"
    ).message_id
    context.chat_data.update({"search_message_id": newMessageId})
    return showCurrentRestaurant(update, context)


def getMoreInfoOfCurrentRestaurant(update: Update, context: CallbackContext) -> int:
    """Fetches in-depth details of the current restaurant and shows them to the user."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Getting the current restaurant and updating his attributes with datailed infos.
    currentPlace: Restaurant = context.chat_data.get("restaurants_list").current
    if not currentPlace.isdetailed:
        __fetchDetailedInfosOfRestaurant(currentPlace, context.chat_data.get("lang"))

    # Creating the keyboard to attach to the display restaurants message:
    #   by clicking 🌐                 the user will open the restaurant's website if present, otherwise it links google.com;
    #   by clicking 📍                 the user will be redirected to google maps to start its navigation;
    #   by clicking ⭐️                 the user will be able to see all the restaurant's reviews;
    #   by clicking ↩️                 the user get back to the detailed informations message;
    #   by clicking ❌                 the conversation will end.
    keyboard = [
        [
            InlineKeyboardButton(text="🌐", url=f"{currentPlace.website}"),
            InlineKeyboardButton(text="📍", url=f"{currentPlace.maps}"),
            InlineKeyboardButton(text="⭐️", callback_data="VIEW_REVIEWS"),
        ],
        [
            InlineKeyboardButton(
                getString("GENERAL_AddToFavorites", context.chat_data.get("lang")),
                callback_data="ADD_TO_PREF",
            ),
        ],
        [
            InlineKeyboardButton(text="↩️", callback_data="BACK_TO_LIST"),
            InlineKeyboardButton(text="❌", callback_data="end"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("search_message_id"),
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

    # The DETAILED_INFO state handles the possibility to view the restaurant's reviews
    # or eventually going back to the restaurants list.
    return DETAILED_INFO


def addRestaurantToFavorites(update: Update, context: CallbackContext):
    """Starts the process to add the current restaurant to a favourite list."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    return showCategories(update, context)


def showCategories(update: Update, context: CallbackContext):
    """Shows the current available categories for the user or group"""
    verifyChatData(update=update, context=context)

    # Fetching from the database the categories already created if present.
    chatLists = fetchCategories(update.effective_chat.id)

    # Setting up the keyboard. Each row will contain a category.
    # The last button is used to add a new category to the present ones.
    keyboard = []
    for chatList in chatLists:
        keyboard.append(
            [InlineKeyboardButton(text=chatList.category, callback_data=chatList.id)]
        )
    keyboard.append([InlineKeyboardButton(text="➕", callback_data="ADD_CATEGORY")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Editing the bot message with the "select list" text and appending the keyboard
    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("search_message_id"),
        text=getString(
            "GENERAL_ShowCategories",
            context.chat_data.get("lang"),
        ),
        reply_markup=reply_markup,
    )

    return FAVORITE_LIST_PICK_STATE


def askFavoriteListName(update: Update, context: CallbackContext):
    """Init the creation of a new list for the current chat asking the user the name."""
    verifyChatData(update, context)

    query = update.callback_query
    query.answer()

    # Asking the user the name of the category of which he wants to create the list (e.g. Pizza,Pasta,Sushi,...)
    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("search_message_id"),
        text=getString(
            "GENERAL_ChoseListName",
            context.chat_data.get("lang"),
        ),
    )

    return FAVORITE_LIST_CREATE_STATE


def createList(update: Update, context: CallbackContext):
    """Creates the list adding a record to the database."""
    verifyChatData(update, context)

    # Fetching the name chosen by the user and deleting his message
    nameChosen = update.message.text
    context.bot.delete_message(update.message.chat_id, update.message.message_id)

    try:
        # Trying to insert the list into the db
        insertList(update.effective_chat.id, nameChosen)
    except:
        # If it fails an error messge is sent
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=getString(
                "ERROR_UnableToCreateFavoriteList", context.chat_data.get("lang")
            ),
        )
    finally:
        # In both cases we get back to the default state showing back the lists already present.
        return showCategories(update, context)


def addToList(update: Update, context: CallbackContext):
    """Adds the current restaurant to the list by updating the database."""
    verifyChatData(update, context)

    query = update.callback_query
    query.answer()

    # Fetching the list id of the list we want to insert the restaurant in and the restaurant itself.
    listId = update.callback_query.data
    restaurantToInsert: Restaurant = context.chat_data.get("restaurants_list").current

    # Inserting the restaurant in the database (if already present the insert command will be ignored internally)
    insertRestaurantInfos(
        restaurantToInsert.id,
        restaurantToInsert.name,
        restaurantToInsert.address,
        restaurantToInsert.phone,
        restaurantToInsert.rating,
        restaurantToInsert.website,
        restaurantToInsert.ratingsnumber,
        len(restaurantToInsert.price) - 1,
        restaurantToInsert.timetable,
        restaurantToInsert.maps,
    )

    # Inserting the restaurant into the selected list.
    insertRestaurantIntoList(listId, restaurantToInsert.id)

    # Sending a confirmation message and displaying the datailed infos of the current restaurant again.
    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("search_message_id"),
        text=getString("GENERAL_RestaurantAddedToList", context.chat_data.get("lang")),
    )

    newId = context.bot.send_message(
        chat_id=update.effective_chat.id, text="_"
    ).message_id
    context.chat_data.update({"search_message_id": newId})

    return showCurrentRestaurant(update, context)


def showReviews(update: Update, context: CallbackContext) -> int:
    """Shows the current restaurant's reviews."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Fetching the current review of the current restaurant
    restaurantCurrentReview: Rating = context.chat_data.get(
        "restaurants_list"
    ).current.reviews.current

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
            InlineKeyboardButton(text="↩️ Info", callback_data="BACK_TO_DETAILED_INFO"),
            InlineKeyboardButton(text="❌", callback_data="end"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("search_message_id"),
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

    # The VIEW_REVIEWS state allows the user to switch between reviews handling prev&next button callbacks.
    return VIEW_REVIEWS


def showPrevReview(update: Update, context: CallbackContext) -> int:
    """Updates the current element of the reviews list with its previous, and shows that review."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # If there is only one element there is no reason to move from the current state
    if context.chat_data.get("restaurants_list").current.reviews.size > 1:
        context.chat_data.get(
            "restaurants_list"
        ).current.reviews.setCurrentElementWithHisPrev()

        return showReviews(update, context)


def showNextReview(update: Update, context: CallbackContext) -> int:
    """Updates the current element of the reviews list with its next, and shows that review."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # If there is only one element there is no reason to move from the current state
    if context.chat_data.get("restaurants_list").current.reviews.size > 1:
        context.chat_data.get(
            "restaurants_list"
        ).current.reviews.setCurrentElementWithHisNext()

        return showReviews(update, context)


def endSearchConversation(update: Update, context: CallbackContext) -> int:
    """Ends the search conversation.

    Returns:
        int: end-code for ConversationHandler
    """
    # This function can both be called by an InlineKeyboardButton and by a command, so we try to answer the callback_query
    try:
        query = update.callback_query
        query.answer()
    except:
        pass

    if context.chat_data.get("search_message_id") != None:
        context.chat_data.pop("search_message_id")
    if context.chat_data.get("research_info") != None:
        context.chat_data.pop("research_info")
    if context.chat_data.get("restaurants_list") != None:
        context.chat_data.pop("restaurants_list")

    return utils.cancelConversation(update=update, context=context)


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


def __fetchRestaurant(chatId: str, researchInfo: ResearchInfo, lang: str):
    googleKey = utils.ApiKey(utils.Service.GOOGLE_PLACES).value

    radiusInMeters: int = int(
        fetchResearchRadius(chatId, researchInfo.walkingdistance)[0]
    )

    if researchInfo.opennow:
        googleResult = get(
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword={researchInfo.food}&maxprice={researchInfo.cost-1}&opennow&language={lang}&location={researchInfo.latitude}%2C{researchInfo.longitude}&radius={radiusInMeters}&type=restaurant&key={googleKey}"
        )
    else:
        googleResult = get(
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword={researchInfo.food}&maxprice={researchInfo.cost-1}&language={lang}&location={researchInfo.latitude}%2C{researchInfo.longitude}&radius={radiusInMeters}&type=restaurant&key={googleKey}"
        )
    googleResult.raise_for_status()

    # Parsing google response (json) to dictionary
    googleResult = loads(googleResult.text)

    if googleResult.get("status") == "OK":
        return googleResult
    elif googleResult.get("status") == "ZERO_RESULTS":
        raise NoPlaceFoundException(researchInfo.location, "Place not found")
    else:
        raise GoogleCriticalErrorException(
            "Google critical error; check the google key status."
        )


def __fetchDetailedInfosOfRestaurant(restaurant: Restaurant, lang: str) -> None:
    # Utils
    placeId: str = restaurant.id
    googleKey = utils.ApiKey(utils.Service.GOOGLE_PLACES).value

    # Fetching detailed information of a restaurant
    googleResult = get(
        f"https://maps.googleapis.com/maps/api/place/details/json?fields=formatted_address%2Cformatted_phone_number%2Copening_hours/weekday_text%2Creviews%2Cwebsite%2Curl&language={lang}&place_id={placeId}&key={googleKey}"
    )
    googleResult.raise_for_status()

    googleResult = loads(googleResult.text)

    if googleResult.get("status") == "OK":
        weekTimeTable = ""

        # Compiling a formatted timetable for the week if provided
        try:
            for dayTimeTable in (
                googleResult.get("result").get("opening_hours").get("weekday_text")
            ):
                weekTimeTable += dayTimeTable + "\n"
        except:
            weekTimeTable = getString("ERROR_TimetableNotAvailable", language=lang)

        # Updating restaurant's infos
        restaurant.address = (
            googleResult.get("result").get("formatted_address")
            if googleResult.get("result").get("formatted_address") != None
            else "https://maps.google.com/"
        )
        restaurant.timetable = weekTimeTable
        restaurant.website = (
            googleResult.get("result").get("website")
            if googleResult.get("result").get("website") != None
            else "https://www.google.com/"
        )
        restaurant.maps = googleResult.get("result").get("url")
        restaurant.phone = (
            googleResult.get("result").get("formatted_phone_number")
            if googleResult.get("result").get("formatted_phone_number") != None
            else getString("ERROR_PhoneNumberNotAvailable", lang)
        )

        for review in googleResult.get("result").get("reviews"):
            restaurant.reviews.add(
                Rating(
                    review.get("author_name"),
                    review.get("rating"),
                    review.get("text"),
                    review.get("time"),
                )
            )

        # The restaurant now has complete informations stored
        restaurant.isdetailed = True
    elif googleResult.get("status") == "ZERO_RESULTS":
        raise NoPlaceFoundException(restaurant.name, "Place not found")
    else:
        raise GoogleCriticalErrorException(
            "Google critical error; check the google key status."
        )


def __compileRestaurantReachingParameters(
    latOrigin: float,
    longOrigin: float,
    latDest: float,
    longDest: float,
    movementType: str,
) -> tuple:
    # http://127.0.0.1:5000/route/v1/{movementType}/{longDest},{latOrigin};{longDest},{latDest}?overview=false
    key = utils.ApiKey(utils.Service.MAPBOX).value
    OSRMResponse = get(
        f"https://api.mapbox.com/directions/v5/{movementType}/{longOrigin},{latOrigin};{longDest},{latDest}?access_token={key}"
    )
    OSRMResponse.raise_for_status()
    OSRMResponse = loads(OSRMResponse.text)

    if OSRMResponse.get("code") != "Ok":
        return (100000, 100000)
    else:
        return (
            OSRMResponse.get("routes")[0].get("distance"),
            OSRMResponse.get("routes")[0].get("duration"),
        )
