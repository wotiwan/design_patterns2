from Src.Core.abstract_dto import abstact_dto
from Src.Core.validator import validator
from datetime import datetime

# DTO для модели транзакции (transaction_model)
# Пример:
# {
#     "id": "d8c12a0f2b8841bfb4dc93cb12d22f85",
#     "date": "2025-01-10 00:00:00",
#     "nomenclature_id": "0c101a7e5934415583a6d2c388fcc11a",
#     "warehouse_id": "1a2b3c4d000100020003000000000001",
#     "quantity": 50,
#     "range_id": "adb7510f687d428fa69726e53d3f65b7"
# }


class transaction_dto(abstact_dto):
    __date: datetime = None
    __nomenclature_id: str = ""
    __warehouse_id: str = ""
    __quantity: float = 0
    __range_id: str = ""

    @property
    def date(self) -> datetime:
        return self.__date

    @date.setter
    def date(self, value):
        if isinstance(value, str) and value.strip():
            try:
                self.__date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError(f"Некорректный формат даты: {value}")
        elif isinstance(value, datetime):
            self.__date = value
        else:
            self.__date = None

    @property
    def nomenclature_id(self) -> str:
        return self.__nomenclature_id

    @nomenclature_id.setter
    def nomenclature_id(self, value: str):
        validator.validate(value, str)
        self.__nomenclature_id = value

    @property
    def warehouse_id(self) -> str:
        return self.__warehouse_id

    @warehouse_id.setter
    def warehouse_id(self, value: str):
        validator.validate(value, str)
        self.__warehouse_id = value

    @property
    def quantity(self) -> float:
        return self.__quantity

    @quantity.setter
    def quantity(self, value: float):
        validator.validate(value, (int, float))
        self.__quantity = float(value)

    @property
    def range_id(self) -> str:
        return self.__range_id

    @range_id.setter
    def range_id(self, value: str):
        validator.validate(value, str)
        self.__range_id = value

    def create(self, data) -> "transaction_dto":
        """
        Создание DTO из словаря
        """
        validator.validate(data, dict)

        # Базовые поля (id)
        if "id" in data:
            self.id = data["id"]

        # Поля транзакции
        self.date = data.get("date", "")
        self.nomenclature_id = data.get("nomenclature_id", "")
        self.warehouse_id = data.get("warehouse_id", "")
        self.quantity = data.get("quantity", 0)
        self.range_id = data.get("range_id", "")

        return self
