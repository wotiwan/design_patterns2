from Src.Core.abstract_converter import abstract_converter
from Src.Core.validator import validator, argument_exception


class basic_converter(abstract_converter):
    """
    Конвертер базовых типов (int, float, str, bool) в словарь.
    """

    def convert(self, value):
        # Проверка на None
        if value is None:
            raise argument_exception("Передано пустое значение")

        # Проверяем тип
        allowed_types = (int, float, str, bool)

        # Проверка корректности аргумента через validator
        validator.validate(value, allowed_types)

        # Возвращаем словарь
        return {"value": value}
