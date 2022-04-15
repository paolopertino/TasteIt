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

from sqlite3 import Connection

from data import dbConnect


def setupTables() -> None:
    """
    Create the database's tables if they haven't been created yet.
    The DB is composed by 4 tables: `chat`, `list`, `restaurant`, `restaurant_for_list`.
    """
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS chat (
            chat_id TEXT PRIMARY KEY,
            lang TEXT NOT NULL)
        """
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS list (
            list_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            chat_id TEXT NOT NULL, 
            FOREIGN KEY (chat_id) REFERENCES chat (chat_id) ON DELETE NO ACTION ON UPDATE CASCADE)
        """
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS restaurant (
            restaurant_id TEXT PRIMARY KEY, 
            name TEXT NOT NULL, 
            address TEXT NOT NULL, 
            rating REAL, 
            price_lvl REAL, 
            timetable TEXT)
        """
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS restaurant_for_list (
            list_id INTEGER, 
            restaurant_id TEXT, 
            PRIMARY KEY(list_id, restaurant_id),
            FOREIGN KEY (list_id) REFERENCES list (list_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (restaurant_id) REFERENCES restaurant (restaurant_id) ON DELETE CASCADE ON UPDATE CASCADE)"""
    )

    connection.commit()
    connection.close()
