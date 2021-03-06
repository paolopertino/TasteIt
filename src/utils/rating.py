from datetime import datetime

from utils.doubly_circular_array_list import DoublyCircularArrayList
from utils.list_iterator import ListIterator


class Rating:
    def __init__(
        self, authorName: str, ratingValue: int, content: str, timestamp: float
    ):
        self.__authorName = authorName
        self.__ratingVal = ratingValue
        self.__reviewText = content
        self.__reviewDate = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y")

    @property
    def author(self) -> str:
        return self.__authorName

    @property
    def rating(self) -> int:
        return self.__ratingVal

    @property
    def content(self) -> str:
        return self.__reviewText

    @property
    def date(self) -> str:
        return self.__reviewDate

    def clone(self):
        """Creates a copy of the Rating object.

        Returns:
            `copyOfSelf` : `Rating` : a copied version of the Rating object
        """
        copyOfSelf: Rating = Rating(
            self.author,
            self.rating,
            self.content,
            datetime.strptime(self.date, "%d/%m/%Y").timestamp(),
        )

        return copyOfSelf


class RatingsList(DoublyCircularArrayList):
    def __init__(self):
        self.__currentElement: Rating = None
        self.__listOfRatings: list = []

    @property
    def next(self) -> Rating:
        return self.__listOfRatings[
            (self.__listOfRatings.index(self.__currentElement) + 1) % self.size
        ]

    @property
    def prev(self) -> Rating:
        return self.__listOfRatings[
            (self.__listOfRatings.index(self.__currentElement) - 1) % self.size
        ]

    @property
    def current(self) -> Rating:
        return self.__currentElement

    @property
    def size(self) -> int:
        return len(self.__listOfRatings)

    def add(self, newElement) -> None:
        if self.__currentElement == None:
            self.__currentElement = newElement
        self.__listOfRatings.append(newElement)

    def remove(self) -> None:
        """Removes the current element to the list if present.

        If there are more than just one element in the list, the new current element will be set with the next of the previous current one.
        """
        if self.__currentElement == None:
            return
        elif self.size == 1:
            self.__listOfRatings.remove(self.current)
            self.__currentElement = None
        else:
            indexOfRemovedElem = self.__listOfRatings.index(self.current)
            self.__listOfRatings.remove(self.current)
            self.__currentElement = self.__listOfRatings[indexOfRemovedElem % self.size]

    def setCurrentElementWithHisNext(self) -> None:
        self.__currentElement = self.__listOfRatings[
            (self.__listOfRatings.index(self.__currentElement) + 1) % self.size
        ]

    def setCurrentElementWithHisPrev(self) -> None:
        self.__currentElement = self.__listOfRatings[
            (self.__listOfRatings.index(self.__currentElement) - 1) % self.size
        ]

    def clone(self):
        """Clones the ratings list.

        Returns:
            `copyOfSelf` : `RatingsList` : a copied version of the RatingsList object
        """
        copyOfSelf: RatingsList = RatingsList()

        for rating in self.__listOfRatings:
            copyOfSelf.add(rating.clone())
            if self.__listOfRatings.index(rating) == self.__listOfRatings.index(
                self.__currentElement
            ):
                copyOfSelf.__currentElement = copyOfSelf.__listOfRatings[
                    len(copyOfSelf.__listOfRatings) - 1
                ]

        return copyOfSelf

    def __iter__(self):
        return ListIterator(self.__listOfRatings)
