from Src.Core.abstract_converter import abstract_converter
from Src.Core.validator import validator, argument_exception
from Src.Core.common import common


class reference_converter(abstract_converter):
    """
    Конвертер ссылочных типов (Reference).
    Преобразует объект справочника в словарь по его полям.

    """

    def convert(self, value):
        # Проверка на None
        if value is None:
            raise argument_exception("Передано пустое значение")

        # Проверка корректности аргумента
        validator.validate(value, object)

        # Если тип — базовый, возвращаем его напрямую
        if isinstance(value, (int, float, str, bool)):
            return {"value": value}

        # Если список или кортеж
        if isinstance(value, (list, tuple, set)):
            return [self.convert(v) for v in value]

        # Если словарь
        if isinstance(value, dict):
            return {k: self.convert(v) for k, v in value.items()}

        # Если объект модели
        fields = common.get_fields(value)
        if not fields:
            raise argument_exception("Объект не имеет атрибутов для конвертации")

        result = {}
        for field in fields:
            field_value = getattr(value, field, None)
            # рекурсивная обработка поля
            result[field] = self.convert(field_value) if not isinstance(field_value, (int, float, str, bool, type(None))) else field_value

        return result
