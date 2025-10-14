from Src.Core.abstract_dto import abstact_dto

# Модель категории (dto)
# Пример
#               "name":"Ингредиенты",
#               "id":"7f4ecdab-0f01-4216-8b72-4c91d22b8918"
class category_dto(abstact_dto):
    __name:str = ""
    __id:str = ""

    @property
    def name(self) ->str:
        return self.__name
    
    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def id(self) -> str:
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value   