import abc
from Src.Core.common import common
from Src.Core.validator import validator, operation_exception


"""
Абстрактный класс для наследования только dto структур
"""
class abstact_dto:

    # Универсальный фабричный метод для загрузщки dto из словаря
    @abc.abstractmethod
    def create(self, data:dict) -> "abstact_dto":
        validator.validate(data, dict)
        fields = common.get_fields(self)
        matching_keys = list(filter(lambda key: key in fields, data.keys()))

        try:
            for key in matching_keys:
                setattr(self, key, data[key])
        except:
            raise   operation_exception("Невозможно загрузить данные!")    

        return self