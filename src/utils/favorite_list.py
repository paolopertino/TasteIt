class FavoriteList:
    def __init__(self, listId: int, listCategory: str):
        self.__id = listId
        self.__category = listCategory

    @property
    def id(self) -> int:
        return self.__id

    @property
    def category(self) -> str:
        return self.__category
