from utils.restaurant import RestaurantList


class FavoriteList:
    def __init__(self, listId: int, listCategory: str):
        self.__id = listId
        self.__category = listCategory
        self.__restaurantsList = RestaurantList()

    @property
    def id(self) -> int:
        return self.__id

    @property
    def category(self) -> str:
        return self.__category

    @property
    def restaurants(self) -> RestaurantList:
        return self.__restaurantsList

    @restaurants.setter
    def restaurants(self, newRestaurantsList):
        self.__restaurantsList = newRestaurantsList
