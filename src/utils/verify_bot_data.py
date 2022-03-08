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
from telegram.ext import CallbackContext

from data import fetchLang, insertChat


def verifyChatData(update: Update, context: CallbackContext) -> None:
    """Verify that all needed chat_data are correctly set, otherwise it fetches them from the database.\\
    Currently the followings datas need to be stored in chat_data to make the bot work properly:
        * `lang` - language code for the current chat

    Args:
        update (Update): _description_
        context (CallbackContext): _description_
    """
    if context.chat_data.get("lang") == None:
        chatLanguage = fetchLang(update.effective_chat.id)

        if chatLanguage:
            context.chat_data.update({"lang": chatLanguage[0]})
        else:
            insertChat(update.effective_chat.id, update.effective_user.language_code)
            context.chat_data.update({"lang": update.effective_user.language_code})

    # If other data needs to be refreshed or checked it will be set below.
