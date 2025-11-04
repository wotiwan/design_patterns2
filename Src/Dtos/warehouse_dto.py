from Src.Core.abstract_dto import abstact_dto
from Src.Core.validator import validator

# DTO для модели склада (warehouse_model)
# Пример:
# {
#     "id": "1a2b3c4d-0001-0002-0003-000000000001",
#     "name": "Главный склад",
#     "address": "г. Москва, ул. Промышленная, д. 5"
# }


class warehouse_dto(abstact_dto):
    __address: str = ""

    @property
    def address(self) -> str:
        return self.__address

    @address.setter
    def address(self, value: str):
        validator.validate(value, str)
        self.__address = value

    def create(self, data) -> "warehouse_dto":
        """
        Создание DTO на основе словаря
        """
        validator.validate(data, dict)

        # Базовые поля (id и name)
        if "id" in data:
            self.id = data["id"]
        if "name" in data:
            self.name = data["name"]

        # Поле address
        self.address = data.get("address", "")

        return self
