from utils.general_place import GeneralPlace


class ResearchInfo:
    def __init__(self):
        self.__startingPlace: GeneralPlace = None
        self.__maxCost: int = 2
        self.__openNow: bool = True
        self.__specifiedFood: str = None

    @property
    def location(self):
        """The name of the starting location if present.

        In case the research starts from a Position Message sent by the user, no name is provided.

        Returns:
            str: the name of the starting location | None
        """
        return self.__startingPlace.name

    @location.setter
    def location(self, place: GeneralPlace) -> None:
        self.__startingPlace = place

    @property
    def latitude(self):
        return self.__startingPlace.latitude

    @property
    def longitude(self):
        return self.__startingPlace.longitude

    @property
    def cost(self):
        return self.__maxCost

    @cost.setter
    def cost(self, newMaxCost: int) -> None:
        self.__maxCost = newMaxCost

    @property
    def opennow(self):
        return self.__openNow

    @opennow.setter
    def opennow(self, isOpen: bool) -> None:
        self.__openNow = isOpen

    @property
    def food(self):
        return self.__specifiedFood

    @food.setter
    def food(self, newFood: str) -> None:
        self.__specifiedFood = newFood
