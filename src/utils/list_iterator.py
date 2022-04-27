class ListIterator:
    def __init__(self, array):
        self.i = 0
        self.data = array

    def __iter__(self):
        return self

    def __next__(self):
        self.i += 1
        try:
            return self.data[self.i - 1]
        except IndexError:
            self.i = 0
            raise StopIteration  # Done iterating.
