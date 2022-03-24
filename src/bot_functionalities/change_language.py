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
from sys import path

path.append("..")

from STRINGS_LIST import getString
from tools.verify_bot_data import verifyChatData
from data import updateLang

SELECT_LANG = range(1)


def setLanguage(update: Update, context: CallbackContext):
    """Send message on `/lang`."""
    verifyChatData(update=update, context=context)

    keyboard = [
        [
            InlineKeyboardButton("🇮🇹", callback_data="it"),
            InlineKeyboardButton("🇺🇸", callback_data="en"),
        ],
        [
            InlineKeyboardButton("❌", callback_data="end"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    update.message.reply_text(
        getString("GENERAL_ChooseLanguageString", context.chat_data.get("lang")),
        reply_markup=reply_markup,
    )
    # Tell ConversationHandler that we're in state `SELECT_LANG` now
    return SELECT_LANG


def changeLanguage(update: Update, context: CallbackContext) -> int:
    """Change the `chat_data["lang"]` value to the one selected by the user, and it updates the database.

    Args:
        update (Update)
        context (CallbackContext)

    Returns:
        ConversationHandler.END: signal which ends the conversation.
    """
    verifyChatData(update=update, context=context)

    query = update.callback_query
    query.answer()

    newLanguage = update.callback_query.data
    updateLang(chatId=update.effective_chat.id, newLang=newLanguage)
    context.chat_data.update({"lang": newLanguage})

    query.edit_message_text(
        text=getString("GENERAL_LanguageUpdated", context.chat_data.get("lang"))
    )
    return ConversationHandler.END
