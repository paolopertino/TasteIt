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

import utils
from tools import verifyChatData
from data import fetchResearchRadius, updateMaxWalkingDistance, updateMaxCarDistance
from STRINGS_LIST import getString

CHOSE_SETTING_TO_CHANGE, CHANGE_WALK_DISTANCE, CHANGE_CAR_DISTANCE = range(3)


def modifySettings(update: Update, context: CallbackContext) -> int:
    """Send a message on `/settings` to modify user default settings."""
    verifyChatData(update, context)

    # Fetching the current values
    currentMaxWalkDistance: int = fetchResearchRadius(update.effective_chat.id, True)[0]
    currentMaxCarDistance: int = fetchResearchRadius(update.effective_chat.id, False)[0]

    keyboard = [
        [
            InlineKeyboardButton(
                getString("GENERAL_ReachableOnFootSet", context.chat_data.get("lang")),
                callback_data="MODIFY_WALK_DISTANCE",
            )
        ],
        [
            InlineKeyboardButton(
                getString("GENERAL_ReachableByCarSet", context.chat_data.get("lang")),
                callback_data="MODIFY_CAR_DISTANCE",
            )
        ],
        [InlineKeyboardButton("❌", callback_data="end")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    settingsMessage = update.message.reply_text(
        getString(
            "GENERAL_ChangeSettingsIntro",
            context.chat_data.get("lang"),
            currentMaxWalkDistance,
            currentMaxCarDistance,
        ),
        reply_markup=reply_markup,
    )

    # The conversation continue by modifing the first message sent by the bot.
    # Therefore the message id is stored.
    context.chat_data.update({"settings_message_id": settingsMessage.message_id})

    # Tell ConversationHandler that we're in state `CHOSEN` now
    return CHOSE_SETTING_TO_CHANGE


def modifyDistance(update: Update, context: CallbackContext) -> int:
    """Asks the user to write the maximum distance in meters to set as default max walking distance."""
    verifyChatData(update, context)

    query = update.callback_query
    query.answer()
    callback_data = update.callback_query.data

    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data.get("settings_message_id"),
        text=getString("GENERAL_ChangeDistance", context.chat_data.get("lang")),
    )

    if callback_data == "MODIFY_WALK_DISTANCE":
        return CHANGE_WALK_DISTANCE
    else:
        return CHANGE_CAR_DISTANCE


def onWalkDistanceUpdate(update: Update, context: CallbackContext) -> int:
    """Update the maximum walking distance in the database for the user with the current chat_id."""
    verifyChatData(update, context)

    callback_data = update.message.text

    try:
        newMaxDistance: int = int(callback_data)

        if newMaxDistance <= 0 or newMaxDistance > 50000:
            raise Exception
    except:
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("settings_message_id"),
            text=getString(
                "ERROR_InvalidDistanceParameter", context.chat_data.get("lang")
            ),
        )

        return modifySettings(update, context)
    else:
        updateMaxWalkingDistance(update.effective_chat.id, newMaxDistance)
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("settings_message_id"),
            text=getString(
                "GENERAL_ParamSuccessfullyChanged", context.chat_data.get("lang")
            ),
        )

        context.chat_data.pop("settings_message_id")
        return ConversationHandler.END


def onCarDistanceUpdate(update: Update, context: CallbackContext) -> int:
    """Update the maximum car distance in the database for the user with the current chat_id."""
    verifyChatData(update, context)

    callback_data = update.message.text

    try:
        newMaxDistance: int = int(callback_data)

        if newMaxDistance <= 0 or newMaxDistance > 50000:
            raise Exception
    except:
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("settings_message_id"),
            text=getString(
                "ERROR_InvalidDistanceParameter", context.chat_data.get("lang")
            ),
        )

        return modifySettings(update, context)
    else:
        updateMaxCarDistance(update.effective_chat.id, newMaxDistance)
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data.get("settings_message_id"),
            text=getString(
                "GENERAL_ParamSuccessfullyChanged", context.chat_data.get("lang")
            ),
        )

        context.chat_data.pop("settings_message_id")
        return ConversationHandler.END


def endSettingsConversation(update: Update, context: CallbackContext) -> int:
    """Ends the settings conversation.

    Returns:
        int: end-code for ConversationHandler
    """
    # This function can both be called by an InlineKeyboardButton and by a command, so we try to answer the callback_query
    try:
        query = update.callback_query
        query.answer()
    except:
        pass

    if context.chat_data.get("settings_message_id") != None:
        context.chat_data.pop("settings_message_id")

    return utils.cancelConversation(update=update, context=context)
