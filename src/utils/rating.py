from datetime import datetime

from utils.doubly_circular_linked_list import DoublyCircularLinkedList


class Rating:
    def __init__(
        self, authorName: str, ratingValue: int, content: str, timestamp: float
    ):
        self.__authorName = authorName
        self.__ratingVal = ratingValue
        self.__reviewText = content
        self.__reviewDate = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y")

    @property
    def author(self):
        return self.__authorName

    @property
    def rating(self):
        return self.__ratingVal

    @property
    def content(self):
        return self.__reviewText

    @property
    def date(self):
        return self.__reviewDate


class RatingsList(DoublyCircularLinkedList):
    def __init__(self):
        self.__currentElement: Rating = None
        self.__listOfRatings: list = []

    def add(self, newElement) -> None:
        if self.__currentElement == None:
            self.__currentElement = newElement
        self.__listOfRatings.append(newElement)

    @property
    def next(self):
        return self.__listOfRatings[
            (self.__listOfRatings.index(self.__currentElement) + 1) % self.size
        ]

    def setCurrentElementWithHisNext(self):
        self.__currentElement = self.__listOfRatings[
            (self.__listOfRatings.index(self.__currentElement) + 1) % self.size
        ]

    @property
    def prev(self):
        return self.__listOfRatings[
            (self.__listOfRatings.index(self.__currentElement) - 1) % self.size
        ]

    def setCurrentElementWithHisPrev(self):
        self.__currentElement = self.__listOfRatings[
            (self.__listOfRatings.index(self.__currentElement) - 1) % self.size
        ]

    @property
    def current(self):
        return self.__currentElement

    @property
    def size(self):
        return len(self.__listOfRatings)
