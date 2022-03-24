class GeneralPlace:
    def __init__(self, name: str, latitude: float, longitude: float) -> None:
        self.__placeName: str = name
        self.__placeLatitude: float = latitude
        self.__placeLongitude: float = longitude

    @property
    def name(self):
        """The name of the place

        Returns:
            str: the name of the place
        """
        return self.__placeName

    @property
    def latitude(self):
        """The latitude of the place

        Returns:
            float: the latitude of the place
        """
        return self.__placeLatitude

    @property
    def longitude(self):
        """The longitude of the place

        Returns:
            float: the longitude of the place
        """
        return self.__placeLongitude
