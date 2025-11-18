from Src.Core.common import common
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_dto import filter_type

"""
Репозиторий данных
"""
class reposity:
    __data = {}

    @property
    def data(self):
        return self.__data
    
    """
    Ключ для единц измерений
    """
    @staticmethod
    def range_key():
        return "range_model"
    

    """
    Ключ для категорий
    """
    @staticmethod
    def group_key():
        return "group_model"
    

    """
    Ключ для номенклатуры
    """
    @staticmethod
    def nomenclature_key():
        return "nomenclature_model"
    

    """
    Ключ для рецептов
    """
    @staticmethod
    def receipt_key():
        return "receipt_model"

    @staticmethod
    def warehouse_key():
        return "warehouse_model"

    @staticmethod
    def transaction_key():
        return "transaction_model"
    
    """
    Получить список всех ключей
    Источник: https://github.com/Alyona1619
    """
    @staticmethod
    def keys() -> list:
        result = []
        methods = [method for method in dir(reposity) if
                    callable(getattr(reposity, method)) and method.endswith('_key')]
        for method in methods:
            key = getattr(reposity, method)()
            result.append(key)

        return result

    @staticmethod
    def apply_filter(items: list, filter_data: filter_dto) -> list:
        """
        Универсальная фильтрация по 'name' и 'unique_code'
        """
        field = filter_data.field
        value = filter_data.value.lower()
        mode = filter_data.mode

        if field not in ("name", "unique_code"):
            raise ValueError(f"Фильтрация по полю '{field}' не поддерживается")

        result = []

        for item in items:
            if not hasattr(item, field):
                continue

            field_value = str(getattr(item, field)).lower()

            if mode == filter_type.EQUALS:
                if field_value == value:
                    result.append(item)

            elif mode == filter_type.LIKE:
                if value in field_value:
                    result.append(item)

        return result


    """
    Инициализация
    """
    def initalize(self):
        keys = reposity.keys()
        for key in keys:
            self.__data[ key ] = []
    
    
