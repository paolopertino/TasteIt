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
import utils
from utils.restaurant import Restaurant, RestaurantList


def fetchLang(chatId: str) -> str:
    """
    Given a chat_id, it returns the language set.

    Args:
        chatId (str) - the chat_id of which the language is required
    """
    connection = dbConnect()
    result = (
        connection.cursor()
        .execute("""SELECT lang FROM chat WHERE chat_id = ?""", (chatId,))
        .fetchone()
    )
    connection.close()

    return result


def fetchCategories(chatId: str) -> list:
    """Given a chat_id, it returns all the lists' categories already created.

    Args:
        chatId (str): the chat_id of which the lists' categories are required

    Returns:
        list: the list of categories of the chat_id provided if present
    """
    result = []

    # Setting up the connection with the db and effectively fetching the categories if present.
    connection = dbConnect()
    dbResponse = (
        connection.cursor()
        .execute("""SELECT list_id, category FROM list WHERE chat_id = ?""", (chatId,))
        .fetchall()
    )
    connection.close()

    # Adding all the fetched categories to the result array and returning it.
    for chatList in dbResponse:
        result.append(utils.FavoriteList(chatList[0], chatList[1]))

    return result


def fetchFavoriteListContent(listId: int) -> RestaurantList:
    """Given a list_id it fetches all the restaurants which are part of that list.

    Args:
        listId (int): the id of the list we want to fetch

    Returns:
        result (RestaurantList): the list of restaurants which are part of the list identified by the list_id provided.
    """
    result = RestaurantList()

    # Setting up the connection with the db and effectively fetching the restaurants in the selected list if present.
    connection = dbConnect()
    dbResponse = (
        connection.cursor()
        .execute(
            """SELECT restaurant.restaurant_id, restaurant.name, restaurant.address, restaurant.phone_number, restaurant.rating, restaurant.website, restaurant.total_ratings, restaurant.price_lvl, restaurant.timetable, restaurant.maps_link 
               FROM restaurant JOIN restaurant_for_list ON restaurant.restaurant_id = restaurant_for_list.restaurant_id 
               WHERE restaurant_for_list.list_id = ?""",
            (listId,),
        )
        .fetchall()
    )
    connection.close()

    for restaurant in dbResponse:
        # Keep this in mind:
        #   restaurant[0]: restaurant.restaurant_id
        #   restaurant[1]: restaurant.name
        #   restaurant[2]: restaurant.address
        #   restaurant[3]: restaurant.phone_number
        #   restaurant[4]: restaurant.rating
        #   restaurant[5]: restaurant.website
        #   restaurant[6]: restaurant.total_ratings
        #   restaurant[7]: restaurant.price_lvl
        #   restaurant[8]: restaurant.timetable
        #   restaurant[9]: restaurant.maps_link
        #
        # We do not care this time about the latitude, the longitude.
        restaurantToAdd = Restaurant(
            restaurant[1],  # restaurant.name
            -1,  # latitude
            -1,  # longitude
            restaurant[0],  # restaurant.restaurant_id
            restaurant[
                7
            ],  # restaurant.price_lvl (converted again into an integer value which can assume values between 0 and 4)
            restaurant[4],  # restaurant.rating
            restaurant[6],  # total ratings number
        )
        restaurantToAdd.address = restaurant[2]
        restaurantToAdd.phone = restaurant[3]
        restaurantToAdd.website = restaurant[5]
        restaurantToAdd.timetable = restaurant[8]
        restaurantToAdd.maps = restaurant[9]
        result.add(restaurantToAdd)

    return result
