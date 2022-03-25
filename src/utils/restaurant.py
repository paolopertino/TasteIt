from utils.general_place import GeneralPlace


class Restaurant(GeneralPlace):
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
        return (
            "⭐️" * round(self.__ratingValue)
        ) + f" *{self.__ratingValue}*/5 (_{self.__totalRatings}_)"

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
