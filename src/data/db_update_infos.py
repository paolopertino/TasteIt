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

from data import dbConnect


def updateLang(chatId: str, newLang: str) -> None:
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE chat 
        SET lang = ? 
        WHERE chat_id = ?
    """,
        (newLang, chatId),
    )

    connection.commit()
    connection.close()


def updateMaxWalkingDistance(chatId: str, newDistanceInMeters: int) -> None:
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE chat
        SET preferred_distance_on_foot = ?
        WHERE chat_id = ?
    """,
        (newDistanceInMeters, chatId),
    )

    connection.commit()
    connection.close()


def updateMaxCarDistance(chatId: str, newDistanceInMeters: int) -> None:
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE chat
        SET preferred_distance_by_car = ?
        WHERE chat_id = ?
    """,
        (newDistanceInMeters, chatId),
    )

    connection.commit()
    connection.close()
