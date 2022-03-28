from utils.general_place import GeneralPlace


class Restaurant(GeneralPlace):
    """A class to represent a restaurant. It is subclass of GeneralPlace.

    Attributes
    ----------
    :attr:`name` : str
        name of the restaurant
    :attr:`latitude` : float
        latitude of the restaurant
    :attr:`longitude` : float
        longitude of the restaurant
    :attr:`placeId` : str
        place id of the restaurant in the google database
    :attr:`priceLevel` : int
        price level of the restaurant (from 0 which means cheap, to 4 which means very expensive)
    :attr:`rating` : float
        rating of the restaurant, from 0 to 5 stars based on its reviews
    :attr:`totalRatings` : int
        number of the restaurant's reviews
    """

    def __init__(
        self,
        name: str,
        latitude: float,
        longitude: float,
        placeId: str,
        priceLevel: int,
        rating: float,
        totalRatings: int,
    ) -> None:
        super().__init__(name=name, latitude=latitude, longitude=longitude)

        self.__restaurantId = placeId
        self.__priceLevel = priceLevel
        self.__ratingValue = rating
        self.__totalRatings = totalRatings
        self.__timetable = ""
        self.__restaurantAddress = ""
        self.__ratings = []

    @property
    def id(self):
        return self.__restaurantId

    @property
    def price(self):
        return "€" * (self.__priceLevel + 1)

    @property
    def rating(self):
        return self.__ratingValue

    @property
    def ratingsnumber(self):
        return self.__totalRatings

    @property
    def ratings(self):
        return self.ratings

    # TODO: add rating object

    @property
    def address(self):
        return self.__restaurantAddress

    @address.setter
    def address(self, newAddress):
        self.__restaurantAddress = newAddress

    @property
    def timetable(self):
        return self.__timetable

    @timetable.setter
    def timetable(self, timetable):
        self.__timetable = timetable


class RestaurantList:
    def __init__(self):
        self.__currentElement: Restaurant = None
        self.__listOfRestaurants: list = []

    def add(self, restaurant: Restaurant) -> None:
        if self.__currentElement == None:
            self.__currentElement = restaurant
        self.__listOfRestaurants.append(restaurant)

    @property
    def next(self):
        return self.__listOfRestaurants[
            (self.__listOfRestaurants.index(self.__currentElement) + 1) % self.size
        ]

    def setCurrentElementWithHisNext(self):
        self.__currentElement = self.__listOfRestaurants[
            (self.__listOfRestaurants.index(self.__currentElement) + 1) % self.size
        ]

    @property
    def prev(self):
        return self.__listOfRestaurants[
            (self.__listOfRestaurants.index(self.__currentElement) - 1) % self.size
        ]

    def setCurrentElementWithHisPrev(self):
        self.__currentElement = self.__listOfRestaurants[
            (self.__listOfRestaurants.index(self.__currentElement) - 1) % self.size
        ]

    @property
    def current(self):
        return self.__currentElement

    @property
    def size(self):
        return len(self.__listOfRestaurants)
