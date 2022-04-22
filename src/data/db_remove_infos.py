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


def removeRestaurantFromListDb(restaurantId: str, listId: int) -> None:
    """Given a listId and a restaurantId it removes the related row in the restaurant_for_list table in the database.

    Args:
        restaurantId (str): the id of the restaurant to remove from the list
        listId (int): the list from where the restaurant has to be removed
    """
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(
        """DELETE FROM restaurant_for_list
           WHERE list_id = ? AND restaurant_id = ?""",
        (listId, restaurantId),
    )
    connection.commit()
    connection.close()


def removeFavoriteListFromDb(listId: int) -> None:
    """Removes the list from the database with the given id.

    Args:
        listId (int): the listId of the list to remove from the database
    """
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(
        """DELETE FROM list
           WHERE list_id = ?""",
        (listId,),
    )
    connection.commit()
    connection.close()
