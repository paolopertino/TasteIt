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

from telegram.ext import (
    CallbackContext,
    PicklePersistence,
    Updater,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    Defaults,
)
from telegram import ParseMode, Update
import traceback
import html
import json
import logging

from utils.api_key import ApiKey, Service
from utils.conversation_utils import notAvailableOption, cancelConversation
from bot_functionalities import (
    start,
    help,
    setLanguage,
    changeLanguage,
    startSearch,
    searchLocationByName,
    searchLocationByPosition,
    selectFood,
    changeFood,
    changeTime,
    priceChanged,
    changePrice,
    searchRestaurant,
    changeDistancePreference,
    showCurrentRestaurant,
    showNextRestaurant,
    showPrevRestaurant,
    showNextReview,
    showPrevReview,
    startPollWithCurrentRestaurant,
    getMoreInfoOfCurrentRestaurant,
    addRestaurantToFavorites,
    showReviews,
    askFavoriteListName,
    createList,
    addToList,
    endSearchConversation,
    displayFavoritesLists,
    pickedList,
    showCurrentFavRestaurant,
    showNextFavRestaurant,
    showPrevFavRestaurant,
    backToFavListsList,
    showFavoriteRestaurantReviews,
    showPrevReviewOfFavRestaurant,
    showNextReviewOfFavRestaurant,
    removeRestaurantFromList,
    deleteFavoriteList,
    endFavoriteListsConversation,
    modifySettings,
    modifyDistance,
    onWalkDistanceUpdate,
    onCarDistanceUpdate,
    endSettingsConversation,
    startPoll,
    SELECT_LANG,
    SELECT_STARTING_POSITION,
    SELECT_FOOD,
    PICK_PRICE,
    CHECK_SEARCH_INFO,
    VIEW_SEARCH_RESULTS,
    DETAILED_INFO,
    VIEW_REVIEWS,
    FAVORITE_LIST_PICK_STATE,
    FAVORITE_LIST_CREATE_STATE,
    FAV_LIST_DISPLAYED,
    RESTAURANT_INFOS_DISPLAY,
    NAVIGATE_REVIEWS,
    CHOSE_SETTING_TO_CHANGE,
    CHANGE_WALK_DISTANCE,
    CHANGE_CAR_DISTANCE,
)
from data import setupTables

_DEVMODE = False
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# USEFUL GUIDELINES FOR ConversationHandlers
# What do the per_* settings in ConversationHandler do?
# ConversationHandler needs to decide somehow to which conversation an update belongs.
# The default setting (per_user=True and per_chat=True) means that in each chat each user can have its own conversation - even in groups.
# If you set per_user=False and you start a conversation in a group chat, the ConversationHandler will also accept input from other users.
# Conversely, if per_user=True, but per_chat=False, its possible to start a conversation in one chat and continue with it in another.


def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    context.bot.send_message(
        chat_id=ApiKey(Service.TELEGRAM_DEVELOPER_CHAT_ID).value,
        text=message,
        parse_mode=ParseMode.HTML,
    )


def main():
    telegramKey = ApiKey(service=Service.TELEGRAM, devMode=_DEVMODE).value

    defaults = Defaults(parse_mode=ParseMode.HTML)
    updater = Updater(telegramKey, use_context=True, defaults=defaults)
    dispatcher = updater.dispatcher

    #################################### Conversation Handlers ####################################
    # Language feature
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("lang", setLanguage)],
            allow_reentry=False,
            per_user=True,
            per_chat=True,
            states={
                SELECT_LANG: [
                    CallbackQueryHandler(changeLanguage, pattern="^" + "it" + "$"),
                    CallbackQueryHandler(changeLanguage, pattern="^" + "en" + "$"),
                    CallbackQueryHandler(cancelConversation, pattern="^" + "end" + "$"),
                ],
            },
            fallbacks=[
                MessageHandler(Filters.text | Filters.command, notAvailableOption),
            ],
        ),
        group=1,
    )

    # Settings feature
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("settings", modifySettings)],
            allow_reentry=False,
            per_user=True,
            per_chat=True,
            states={
                CHOSE_SETTING_TO_CHANGE: [
                    CallbackQueryHandler(
                        modifyDistance, pattern="^" + "MODIFY_WALK_DISTANCE" + "$"
                    ),
                    CallbackQueryHandler(
                        modifyDistance, pattern="^" + "MODIFY_CAR_DISTANCE" + "$"
                    ),
                    CallbackQueryHandler(
                        endSettingsConversation, pattern="^" + "end" + "$"
                    ),
                ],
                CHANGE_WALK_DISTANCE: [
                    MessageHandler((Filters.text), onWalkDistanceUpdate)
                ],
                CHANGE_CAR_DISTANCE: [
                    MessageHandler((Filters.text), onCarDistanceUpdate)
                ],
            },
            fallbacks=[
                CommandHandler("annulla", endSettingsConversation),
                MessageHandler(Filters.command, notAvailableOption),
            ],
        ),
        group=1,
    )

    # Search place feature
    # If the conversation is inactive for more than 5 minutes, it will be automaticallt ended.
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("cerca", startSearch)],
            allow_reentry=False,
            per_user=False,
            conversation_timeout=300,
            states={
                SELECT_STARTING_POSITION: [
                    MessageHandler(
                        (Filters.text & ~Filters.location & ~Filters.command),
                        searchLocationByName,
                    ),
                    MessageHandler(
                        (~Filters.text & Filters.location & ~Filters.command),
                        searchLocationByPosition,
                    ),
                ],
                SELECT_FOOD: [
                    MessageHandler(
                        (Filters.regex(r"^[a-zA-Z]+( [a-zA-Z]+)*$")),
                        selectFood,
                    ),
                ],
                PICK_PRICE: [
                    CallbackQueryHandler(priceChanged, pattern=r"^[1-5]$"),
                ],
                CHECK_SEARCH_INFO: [
                    CallbackQueryHandler(changeFood, pattern="^" + "CHANGE_FOOD" + "$"),
                    CallbackQueryHandler(changeTime, pattern="^" + "CHANGE_TIME" + "$"),
                    CallbackQueryHandler(
                        changePrice, pattern="^" + "CHANGE_PRICE" + "$"
                    ),
                    CallbackQueryHandler(
                        searchRestaurant, pattern="^" + "SEARCH" + "$"
                    ),
                    CallbackQueryHandler(
                        endSearchConversation, pattern="^" + "end" + "$"
                    ),
                    CallbackQueryHandler(
                        changeDistancePreference, pattern="^" + "CHANGE_DISTANCE" + "$"
                    ),
                ],
                VIEW_SEARCH_RESULTS: [
                    CallbackQueryHandler(
                        showNextRestaurant, pattern="^" + "NEXT_RESTAURANT" + "$"
                    ),
                    CallbackQueryHandler(
                        showPrevRestaurant, pattern="^" + "PREV_RESTAURANT" + "$"
                    ),
                    CallbackQueryHandler(
                        startPollWithCurrentRestaurant, pattern="^" + "START_POLL" + "$"
                    ),
                    CallbackQueryHandler(
                        getMoreInfoOfCurrentRestaurant,
                        pattern="^" + "DISPLAY_MORE_INFO" + "$",
                    ),
                    CallbackQueryHandler(
                        endSearchConversation, pattern="^" + "end" + "$"
                    ),
                ],
                DETAILED_INFO: [
                    CallbackQueryHandler(
                        showReviews, pattern="^" + "VIEW_REVIEWS" + "$"
                    ),
                    CallbackQueryHandler(
                        addRestaurantToFavorites, pattern="^" + "ADD_TO_PREF" + "$"
                    ),
                    CallbackQueryHandler(
                        showCurrentRestaurant, pattern="^" + "BACK_TO_LIST" + "$"
                    ),
                    CallbackQueryHandler(
                        endSearchConversation, pattern="^" + "end" + "$"
                    ),
                ],
                VIEW_REVIEWS: [
                    CallbackQueryHandler(
                        showPrevReview, pattern="^" + "PREV_REVIEW" + "$"
                    ),
                    CallbackQueryHandler(
                        showNextReview, pattern="^" + "NEXT_REVIEW" + "$"
                    ),
                    CallbackQueryHandler(
                        getMoreInfoOfCurrentRestaurant,
                        pattern="^" + "BACK_TO_DETAILED_INFO" + "$",
                    ),
                    CallbackQueryHandler(
                        endSearchConversation, pattern="^" + "end" + "$"
                    ),
                ],
                FAVORITE_LIST_PICK_STATE: [
                    CallbackQueryHandler(
                        askFavoriteListName, pattern="^" + "ADD_CATEGORY" + "$"
                    ),
                    CallbackQueryHandler(addToList),
                ],
                FAVORITE_LIST_CREATE_STATE: [
                    MessageHandler(
                        (Filters.text & ~Filters.command),
                        createList,
                    )
                ],
            },
            fallbacks=[
                CommandHandler("annulla", endSearchConversation),
                MessageHandler(Filters.command, notAvailableOption),
            ],
        ),
        group=1,
    )

    # Favorite lists display feature
    # If the conversation is inactive for more than 5 minutes, it will be automaticallt ended.
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("preferiti", displayFavoritesLists)],
            allow_reentry=False,
            per_user=False,
            conversation_timeout=300,
            states={
                FAV_LIST_DISPLAYED: [
                    CallbackQueryHandler(
                        endFavoriteListsConversation, pattern="^" + "end" + "$"
                    ),
                    CallbackQueryHandler(pickedList),
                ],
                RESTAURANT_INFOS_DISPLAY: [
                    CallbackQueryHandler(
                        showNextFavRestaurant, pattern="^" + "NEXT_RESTAURANT" + "$"
                    ),
                    CallbackQueryHandler(
                        showPrevFavRestaurant, pattern="^" + "PREV_RESTAURANT" + "$"
                    ),
                    CallbackQueryHandler(
                        backToFavListsList, pattern="^" + "BACK_TO_LIST" + "$"
                    ),
                    CallbackQueryHandler(
                        showFavoriteRestaurantReviews,
                        pattern="^" + "VIEW_REVIEWS" + "$",
                    ),
                    CallbackQueryHandler(
                        removeRestaurantFromList,
                        pattern="^" + "REMOVE_RESTAURANT_FROM_LIST" + "$",
                    ),
                    CallbackQueryHandler(
                        deleteFavoriteList, pattern="^" + "DELETE_LIST" + "$"
                    ),
                    CallbackQueryHandler(startPoll, pattern="^" + "START_POLL" + "$"),
                    CallbackQueryHandler(
                        endFavoriteListsConversation, pattern="^" + "end" + "$"
                    ),
                ],
                NAVIGATE_REVIEWS: [
                    CallbackQueryHandler(
                        showPrevReviewOfFavRestaurant, pattern="^" + "PREV_REVIEW" + "$"
                    ),
                    CallbackQueryHandler(
                        showNextReviewOfFavRestaurant, pattern="^" + "NEXT_REVIEW" + "$"
                    ),
                    CallbackQueryHandler(
                        showCurrentFavRestaurant,
                        pattern="^" + "BACK_TO_DETAILED_INFO" + "$",
                    ),
                    CallbackQueryHandler(
                        endFavoriteListsConversation, pattern="^" + "end" + "$"
                    ),
                ],
            },
            fallbacks=[
                CommandHandler("annulla", endSearchConversation),
                MessageHandler(Filters.command, notAvailableOption),
            ],
        ),
        group=1,
    )

    # Command Handlers
    dispatcher.add_handler(CommandHandler("start", start), group=1)
    dispatcher.add_handler(CommandHandler("help", help), group=1)

    # The error handler
    dispatcher.add_error_handler(error_handler)

    # Setting up database
    setupTables()

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
