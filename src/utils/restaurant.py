from utils.doubly_circular_array_list import DoublyCircularArrayList
from utils.general_place import GeneralPlace
from utils.list_iterator import ListIterator
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
    def id(self) -> str:
        return self.__restaurantId

    @property
    def price(self) -> str:
        return "€" * (self.__priceLevel + 1)

    @property
    def rating(self) -> float:
        return self.__ratingValue

    @property
    def ratingsnumber(self) -> int:
        return self.__totalRatings

    @property
    def phone(self) -> str:
        return self.__phoneNumber

    @phone.setter
    def phone(self, phoneNumber: str) -> None:
        self.__phoneNumber = phoneNumber

    @property
    def isdetailed(self) -> bool:
        return self.__hasAlreadyFetchedDetails

    @isdetailed.setter
    def isdetailed(self, isDetailed: bool) -> None:
        self.__hasAlreadyFetchedDetails = isDetailed

    @property
    def maps(self) -> str:
        return self.__mapsUrl

    @maps.setter
    def maps(self, mapsUrl: str) -> None:
        self.__mapsUrl = mapsUrl

    @property
    def reviews(self) -> RatingsList:
        return self.__ratings

    @reviews.setter
    def reviews(self, reviews: RatingsList) -> None:
        self.__ratings = reviews

    @property
    def website(self) -> None:
        return self.__website

    @website.setter
    def website(self, placeWebsite: str) -> None:
        self.__website = placeWebsite

    @property
    def address(self) -> str:
        return self.__restaurantAddress

    @address.setter
    def address(self, newAddress) -> None:
        self.__restaurantAddress = newAddress

    @property
    def timetable(self) -> str:
        return self.__timetable

    @timetable.setter
    def timetable(self, timetable) -> None:
        self.__timetable = timetable

    def clone(self):
        """Clones the restaurant object.

        Returns:
            `copyOfSelf` : `Restaurant` : a copied version of the current restaurant
        """
        copyOfSelf: Restaurant = Restaurant(
            self.name,
            self.latitude,
            self.longitude,
            self.id,
            self.__priceLevel,
            self.rating,
            self.ratingsnumber,
        )

        copyOfSelf.timetable = self.timetable
        copyOfSelf.address = self.address
        copyOfSelf.reviews = self.reviews.clone()
        copyOfSelf.website = self.website
        copyOfSelf.maps = self.maps
        copyOfSelf.phone = self.phone
        copyOfSelf.isdetailed = self.isdetailed

        return copyOfSelf


class RestaurantList(DoublyCircularArrayList):
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

    @property
    def next(self) -> Restaurant:
        return self.__listOfRestaurants[
            (self.__listOfRestaurants.index(self.__currentElement) + 1) % self.size
        ]

    @property
    def prev(self) -> Restaurant:
        return self.__listOfRestaurants[
            (self.__listOfRestaurants.index(self.__currentElement) - 1) % self.size
        ]

    @property
    def current(self) -> Restaurant:
        return self.__currentElement

    @property
    def size(self) -> int:
        return len(self.__listOfRestaurants)

    def add(self, newElement: Restaurant) -> None:
        """Add a restaurant to the list as last element.

        Args:
            `newElement` (Restaurant): the element to add to the list
        """
        if self.__currentElement == None:
            self.__currentElement = newElement
        self.__listOfRestaurants.append(newElement)

    def remove(self) -> None:
        """Removes the current element to the list if present.

        If there are more than just one element in the list, the new current element will be set with the next of the previous current one.
        """
        if self.__currentElement == None:
            return
        elif self.size == 1:
            self.__listOfRestaurants.remove(self.current)
            self.__currentElement = None
        else:
            indexOfRemovedElem = self.__listOfRestaurants.index(self.current)
            self.__listOfRestaurants.remove(self.current)
            self.__currentElement = self.__listOfRestaurants[
                indexOfRemovedElem % self.size
            ]

    def setCurrentElementWithHisNext(self) -> None:
        """
        Set the next element of the list as current element.

        If the initial current element is the last one of the list, the new current element will be the first element of the list
        """
        self.__currentElement = self.__listOfRestaurants[
            (self.__listOfRestaurants.index(self.__currentElement) + 1) % self.size
        ]

    def setCurrentElementWithHisPrev(self) -> None:
        """
        Set the previous element of the list as current element.

        If the initial current element is the first one of the list, the new current element will be the last element of the list
        """
        self.__currentElement = self.__listOfRestaurants[
            ((self.__listOfRestaurants.index(self.__currentElement) - 1) % self.size)
        ]

    def clone(self):
        """Clones the restaurants list.

        Returns:
            `copyOfSelf` : `RestaurantList`: a copied version of the current list
        """
        copyOfSelf: RestaurantList = RestaurantList()

        for restaurant in self.__listOfRestaurants:
            copyOfSelf.add(restaurant.clone())
            if self.__listOfRestaurants.index(
                restaurant
            ) == self.__listOfRestaurants.index(self.__currentElement):
                copyOfSelf.__currentElement = copyOfSelf.__listOfRestaurants[
                    len(copyOfSelf.__listOfRestaurants) - 1
                ]
        return copyOfSelf

    def __iter__(self):
        return ListIterator(self.__listOfRestaurants)
