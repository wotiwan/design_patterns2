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

        # Проверка через валидатор
        validator.validate(value, object)

        # Определяем поля объекта
        fields = common.get_fields(value)

        # Если объект не имеет ни одного поля — ошибка
        if not fields:
            raise argument_exception("Объект не имеет атрибутов для конвертации")

        # Собираем словарь
        result = {}
        for field in fields:
            result[field] = getattr(value, field, None)

        return result
