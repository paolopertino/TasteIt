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

from custom_exceptions import GoogleCriticalErrorException, NoPlaceFoundException
from utils.general_place import GeneralPlace
from utils.rating import Rating
from utils.research_info import ResearchInfo
from utils.restaurant import Restaurant, RestaurantList

path.append("..")

from STRINGS_LIST import getString

from tools import verifyChatData
import utils

(
    SELECT_STARTING_POSITION,
    SELECT_FOOD,
    PICK_PRICE,
    CHECK_SEARCH_INFO,
    VIEW_SEARCH_RESULTS,
    DETAILED_INFO,
    VIEW_REVIEWS,
) = range(7)


def startSearch(update: Update, context: CallbackContext) -> int:
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
        endSearchConversation(update=update, context=context)
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

    # Once the recap message is shown the FSM moves to CHECK_SEARCH_INFO state.
    # That state handles all the user needs to change the search parameters.
    return CHECK_SEARCH_INFO


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
    searchInfo = context.chat_data.get("research_info")

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

    # Getting back to the recap state.
    return CHECK_SEARCH_INFO


def searchRestaurant(update: Update, context: CallbackContext) -> int:
    """Given the research parameters (stored in `chat_data`), it fetches the list of restaurants and display it to the user."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Getting the complete research infos. They will be used to perform the restaurants research.
    searchInfo = context.chat_data.get("research_info")

    try:
        # Fetch the restaurants.
        placesFound = __fetchRestaurant(searchInfo, context.chat_data.get("lang"))
    except NoPlaceFoundException:
        # Thrown when no restaurants were found with the specfied research informations.
        # In this case an error message will be sent and the conversation immediately ends.
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=getString("ERROR_NoRestaurantsFound", context.chat_data.get("lang")),
        )

        endSearchConversation(update=update, context=context)
    except GoogleCriticalErrorException:
        # Thrown when an internal google apis error occur.
        # Also in this case an error message is sent and the conversation immediately ends.
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=getString("ERROR_GoogleCriticalError", context.chat_data.get("lang")),
        )

        endSearchConversation(update=update, context=context)
    else:
        # If everything has gone fine, a restaurants' list is compiled and stored in chat_data
        fetchedRestaurants = RestaurantList()
        for result in placesFound.get("results"):
            fetchedRestaurants.add(
                Restaurant(
                    result.get("name"),
                    result.get("geometry").get("location").get("lat"),
                    result.get("geometry").get("location").get("lng"),
                    result.get("place_id"),
                    result.get("price_level"),
                    result.get("rating"),
                    result.get("user_ratings_total"),
                )
            )

        context.chat_data.update({"restaurants_list": fetchedRestaurants})

        showCurrentRestaurant(update, context)


def showCurrentRestaurant(update: Update, context: CallbackContext):
    """Display the current restaurant name and ratings and set up some possible actions."""
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Fetching the list of restaurants
    listOfRestaurants = context.chat_data.get("restaurants_list")

    # Creating the keyboard to attach to the display restaurants message:
    #   by clicking ⬅️                 the user will move to the previous restaurant of the list;
    #   by clicking ➡️                 the user will move to the next restaurant of the list;
    #   by clicking GENERAL_MoreInfos  the user will be able to see detailed informations of the current restaurant;
    #   by clicking 📄+                the user can add the current restaurant to his favorites list;
    #   by clicking ❌                 the conversation will end.
    keyboard = [
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
            InlineKeyboardButton("📄+", callback_data="ADD_TO_PREF"),
            InlineKeyboardButton("❌", callback_data="end"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Printing the infos of the current element
    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("search_message_id"),
        text=getString(
            "GENERAL_RestaurantInfoDisplay",
            context.chat_data.get("lang"),
            listOfRestaurants.current.name,
            "⭐️" * round(listOfRestaurants.current.rating)
            + " <b><i>{}</i></b>/5".format(str(listOfRestaurants.current.rating)),
            "<i>{}</i>".format(str(listOfRestaurants.current.ratingsnumber)),
        ),
        reply_markup=reply_markup,
    )

    # The state VIEW_SEARCH_RESULTS handles the user possibility to switch between restaurant, to add the current restaurant to his
    # favorites list, to get detailed informations about the current restaurant.
    return VIEW_SEARCH_RESULTS


# TODO: sono arrivato qui per scrivere la documentazione


def showNextRestaurant(update: Update, context: CallbackContext):
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Fetching the list of restaurants and picking the next
    listOfRestaurants = context.chat_data.get(
        "restaurants_list"
    ).setCurrentElementWithHisNext()
    showCurrentRestaurant(update, context)


def showPrevRestaurant(update: Update, context: CallbackContext):
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    # Fetching the list of restaurants and picking the next
    listOfRestaurants = context.chat_data.get(
        "restaurants_list"
    ).setCurrentElementWithHisPrev()
    showCurrentRestaurant(update, context)


def getMoreInfoOfCurrentRestaurant(update: Update, context: CallbackContext):
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    currentPlace: Restaurant = context.chat_data.get("restaurants_list").current
    if not currentPlace.isdetailed:
        __fetchDetailedInfosOfRestaurant(currentPlace, context.chat_data.get("lang"))

    keyboard = [
        [
            InlineKeyboardButton(text="🌐", url=f"{currentPlace.website}"),
            InlineKeyboardButton(text="🗺", url=f"{currentPlace.maps}"),
            InlineKeyboardButton(text="⭐️", callback_data="VIEW_REVIEWS"),
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
            "⭐️" * round(currentPlace.rating)
            + " <b><i>{}</i></b>/5".format(str(currentPlace.rating)),
            "<i>{}</i>".format(str(currentPlace.ratingsnumber)),
            currentPlace.timetable,
        ),
        reply_markup=reply_markup,
    )

    return DETAILED_INFO


def addRestaurantToFavorites(update: Update, context: CallbackContext):
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()
    # TODO: add the current displayed restaurant to the favorites
    print("adding to the preferred restaurants")


def showReviews(update: Update, context: CallbackContext):
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    restaurantCurrentReview: Rating = context.chat_data.get(
        "restaurants_list"
    ).current.reviews.current

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

    return VIEW_REVIEWS


def showPrevReview(update: Update, context: CallbackContext):
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    context.chat_data.get(
        "restaurants_list"
    ).current.reviews.setCurrentElementWithHisPrev()
    showReviews(update, context)


def showNextReview(update: Update, context: CallbackContext):
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    context.chat_data.get(
        "restaurants_list"
    ).current.reviews.setCurrentElementWithHisNext()
    showReviews(update, context)


def endSearchConversation(update: Update, context: CallbackContext) -> int:
    """Ends the search conversation.

    Returns:
        int: end-code for ConversationHandler
    """
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


def __fetchRestaurant(researchInfo: ResearchInfo, lang: str):
    googleKey = utils.ApiKey(utils.Service.GOOGLE_PLACES).value
    if researchInfo.opennow:
        googleResult = get(
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword={researchInfo.food}&maxprice={researchInfo.cost-1}&opennow&language={lang}&location={researchInfo.latitude}%2C{researchInfo.longitude}&rankby=distance&type=restaurant&key={googleKey}"
        )
    else:
        googleResult = get(
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword={researchInfo.food}&maxprice={researchInfo.cost-1}&language={lang}&location={researchInfo.latitude}%2C{researchInfo.longitude}&rankby=distance&type=restaurant&key={googleKey}"
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
