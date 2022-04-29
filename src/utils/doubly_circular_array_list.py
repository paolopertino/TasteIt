from abc import ABC, abstractmethod, abstractproperty


class DoublyCircularArrayList(ABC):
    @abstractmethod
    def add(self, newElement):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def setCurrentElementWithHisNext(self):
        pass

    @abstractmethod
    def setCurrentElementWithHisPrev(self):
        pass

    @abstractmethod
    def clone(self):
        pass

    @abstractproperty
    def next(self):
        pass

    @abstractproperty
    def prev(self):
        pass

    @abstractproperty
    def current(self):
        pass

    @abstractproperty
    def size(self):
        pass
