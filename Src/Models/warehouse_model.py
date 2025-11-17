from Src.Core.abstract_model import abstact_model
from Src.Core.validator import validator
from Src.Dtos.warehouse_dto import warehouse_dto


class warehouse_model(abstact_model):
    """
    Модель склада
    Хранит информацию о конкретном складе (место хранения номенклатуры)
    """

    def __init__(self, name: str, address: str = ""):
        super().__init__()
        self.name = name
        self.address = address

    @staticmethod
    def create(name: str, address: str = ""):
        """
        Фабричный метод для создания склада
        """
        validator.validate(name, str)
        validator.validate(address, str)
        return warehouse_model(name, address)

    @staticmethod
    def from_dto(dto: warehouse_dto, cache: dict) -> "warehouse_model":
        """
        Преобразование warehouse_dto в warehouse_model.
        """
        validator.validate(dto, warehouse_dto)
        validator.validate(cache, dict)

        # Если объект уже создан — вернуть из кэша
        if dto.id in cache:
            return cache[dto.id]

        # Создание нового объекта склада
        item = warehouse_model.create(dto.name, dto.address)
        item.unique_code = dto.id

        cache[dto.id] = item
        return item
