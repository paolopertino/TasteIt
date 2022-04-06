from utils.general_place import GeneralPlace


class ResearchInfo:
    """An object to represent the restaurants research details.

    Attributes
    ----------
    :attr:`__startingPlace` : GeneralPlace
        the location from which to start the location
    :attr:`__maxCost` : int, default 3
        the max cost rate accepted for the research (it can assume values from 1 to 5 depending on the expensiveness chosen)
    :attr:`__openNow` : bool, default False
        defines if you want fetch both closed and open restaurant at the time of the research or not (otherwise only open restaurants will be fetched)
    :attr:`__specifiedFood` : str
        desired food chosen by the user
    """

    def __init__(self):
        self.__startingPlace: GeneralPlace = None
        self.__maxCost: int = 3
        self.__openNow: bool = False
        self.__specifiedFood: str = None

    @property
    def location(self):
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
