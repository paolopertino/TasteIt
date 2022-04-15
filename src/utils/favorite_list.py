class FavoriteList:
    def __init__(self, listId, listCategory):
        self.__id = listId
        self.__category = listCategory

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, id: int) -> None:
        self.__id = id

    @property
    def category(self) -> str:
        return self.__category

    @category.setter
    def category(self, category: str) -> None:
        self.__category = category
