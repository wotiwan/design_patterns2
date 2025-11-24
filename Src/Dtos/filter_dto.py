from Src.Core.validator import validator
from Src.Core.abstract_dto import abstact_dto
from Src.Core.filter_type import filter_type


class filter_dto(abstact_dto):
    __entity: str = ""
    __field: str = ""
    __value: str = ""
    __mode: filter_type = filter_type.EQUALS

    @property
    def entity(self) -> str:
        return self.__entity

    @entity.setter
    def entity(self, value: str):
        validator.validate(value, str)
        self.__entity = value

    @property
    def field(self) -> str:
        return self.__field

    @field.setter
    def field(self, value: str):
        validator.validate(value, str)
        self.__field = value

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, val: str):
        validator.validate(val, str)
        self.__value = val

    @property
    def mode(self) -> filter_type:
        return self.__mode

    @mode.setter
    def mode(self, val):
        if isinstance(val, str):
            val = val.lower().strip()
            if val == "equals":
                self.__mode = filter_type.EQUALS
            elif val == "like":
                self.__mode = filter_type.LIKE
            else:
                raise ValueError(f"Неизвестный тип фильтра: {val}")
        elif isinstance(val, filter_type):
            self.__mode = val
        else:
            raise ValueError("Некорректный тип фильтра")

    def create(self, data: dict) -> "filter_dto":
        validator.validate(data, dict)
        self.entity = data.get("entity", "")
        self.field = data.get("field", "")
        self.value = data.get("value", "")
        self.mode = data.get("mode", "equals")
        return self
