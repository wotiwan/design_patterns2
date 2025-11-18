import copy
from Src.Core.filter_type import filter_type
from Src.Dtos.filter_dto import filter_dto
from Src.Core.validator import validator


class prototype_report:

    def __init__(self, data: list):
        self.data = data

    def clone(self, new_data: list = None):
        obj = copy.deepcopy(self)
        if new_data is not None:
            obj.data = new_data
        return obj

    # Вспомогательная функция: получение вложенного атрибута

    @staticmethod
    def get_nested(obj, field: str):
        parts = field.split(".")
        cur = obj
        for p in parts:
            if not hasattr(cur, p):
                return None
            cur = getattr(cur, p)
        return cur

    # Универсальный фильтр (поддерживает вложенные структуры)
    @staticmethod
    def filter(items: list, dto: filter_dto) -> list:
        validator.validate(items, list)
        validator.validate(dto, filter_dto)

        field = dto.field
        value = dto.value.lower()
        mode = dto.mode

        # Разрешаем вложенные поля
        # Примеры:
        #   name
        #   unique_code
        #   base_unit.name
        #   owner.unique_code

        allowed_fields = ("name", "unique_code")
        if not any(field == f or field.endswith("." + f) for f in allowed_fields):
            raise ValueError(f"Поле '{field}' не поддерживается для фильтрации")

        result = []

        for item in items:
            field_val = prototype_report.get_nested(item, field)

            if field_val is None:
                continue

            field_val = str(field_val).lower()

            if mode == filter_type.EQUALS:
                if field_val == value:
                    result.append(item)

            elif mode == filter_type.LIKE:
                if value in field_val:
                    result.append(item)

        return result
