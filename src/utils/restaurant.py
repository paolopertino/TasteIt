from utils.doubly_circular_linked_list import DoublyCircularLinkedList
from utils.general_place import GeneralPlace
from utils.rating import RatingsList


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
        self.__ratings = RatingsList()
        self.__website = ""
        self.__mapsUrl = ""
        self.__phoneNumber = ""
        self.__hasAlreadyFetchedDetails = False

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
    def phone(self):
        return self.__phoneNumber

    @phone.setter
    def phone(self, phoneNumber: str):
        self.__phoneNumber = phoneNumber

    @property
    def isdetailed(self):
        return self.__hasAlreadyFetchedDetails

    @isdetailed.setter
    def isdetailed(self, isDetailed: bool):
        self.__hasAlreadyFetchedDetails = isDetailed

    @property
    def maps(self):
        return self.__mapsUrl

    @maps.setter
    def maps(self, mapsUrl: str):
        self.__mapsUrl = mapsUrl

    @property
    def reviews(self):
        return self.__ratings

    @reviews.setter
    def reviews(self, reviews):
        self.__ratings = reviews

    @property
    def website(self):
        return self.__website

    @website.setter
    def website(self, placeWebsite):
        self.__website = placeWebsite

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


class RestaurantList(DoublyCircularLinkedList):
    """A list of restaurants with doubly circular linked list features.

    Attributes
    ----------
    :attr:`__currentElement` : Restaurant
        the restaurant on which the cursor is pointing
    :attr:`__listOfRestaurants` : list
        a list of restaurants
    """

    def __init__(self):
        self.__currentElement: Restaurant = None
        self.__listOfRestaurants: list = []

    def add(self, newElement) -> None:
        """Add a restaurant to the list as last element.

        Args:
            `newElement` (Restaurant): the element to add to the list
        """
        if self.__currentElement == None:
            self.__currentElement = newElement
        self.__listOfRestaurants.append(newElement)

    @property
    def next(self):
        return self.__listOfRestaurants[
            (self.__listOfRestaurants.index(self.__currentElement) + 1) % self.size
        ]

    def setCurrentElementWithHisNext(self):
        """
        Set the next element of the list as current element.

        If the initial current element is the last one of the list, the new current element will be the first element of the list
        """
        self.__currentElement = self.__listOfRestaurants[
            (self.__listOfRestaurants.index(self.__currentElement) + 1) % self.size
        ]

    @property
    def prev(self):
        return self.__listOfRestaurants[
            (self.__listOfRestaurants.index(self.__currentElement) - 1) % self.size
        ]

    def setCurrentElementWithHisPrev(self):
        """
        Set the previous element of the list as current element.

        If the initial current element is the first one of the list, the new current element will be the last element of the list
        """
        self.__currentElement = self.__listOfRestaurants[
            (self.__listOfRestaurants.index(self.__currentElement) - 1) % self.size
        ]

    @property
    def current(self):
        return self.__currentElement

    @property
    def size(self):
        return len(self.__listOfRestaurants)
