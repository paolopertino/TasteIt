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

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from STRINGS_LIST import getString

from tools.verify_bot_data import verifyChatData
from bot_functionalities import SELECT_LANG


def notAvailableOption(update: Update, context: CallbackContext) -> int:
    verifyChatData(update=update, context=context)

    update.message.reply_text(
        getString("ERROR_ChoseAnAvailableOption", context.chat_data.get("lang")),
    )
    # Return to the SELECT_LANG state.
    return SELECT_LANG


def cancelConversation(update: Update, context: CallbackContext) -> int:
    """Ends an active conversation.

    Args:
        update (Update):
        context (CallbackContext):

    Returns:
        ConversationHandler.END: signal to end the conversation
    """
    # verifyChatData(update=update, context=context)

    try:
        query = update.callback_query
        query.answer()
    except:
        update.message.reply_text(
            text=getString("GENERAL_OperationCanceled", context.chat_data.get("lang"))
        )
    else:
        query.edit_message_text(
            text=getString("GENERAL_OperationCanceled", context.chat_data.get("lang"))
        )
    finally:
        return ConversationHandler.END
