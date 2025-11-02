from datetime import datetime
from Src.Core.abstract_converter import abstract_converter
from Src.Core.validator import validator, argument_exception


class datetime_converter(abstract_converter):
    """
    Конвертер для объектов datetime.
    Преобразует дату/время в словарь с ISO-строкой.
    """

    def convert(self, value):
        # Проверка на None
        if value is None:
            raise argument_exception("Передано пустое значение")

        # Проверка через валидатор
        validator.validate(value, datetime)

        # Возвращаем словарь
        return {"value": value.isoformat(timespec="seconds")}
