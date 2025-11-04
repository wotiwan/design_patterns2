from datetime import datetime
from Src.Core.abstract_model import abstact_model
from Src.Core.validator import validator, operation_exception
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.range_model import range_model
from Src.Dtos.transaction_dto import transaction_dto


class transaction_model(abstact_model):
    """
    Модель транзакции (операции движения номенклатуры)
    """

    def __init__(
        self,
        date: datetime,
        nomenclature: nomenclature_model,
        warehouse: warehouse_model,
        quantity: float,
        unit: range_model
    ):
        super().__init__()

        validator.validate(date, datetime)
        validator.validate(nomenclature, nomenclature_model)
        validator.validate(warehouse, warehouse_model)
        validator.validate(quantity, (int, float))
        validator.validate(unit, range_model)

        self.date = date
        self.nomenclature = nomenclature
        self.warehouse = warehouse
        self.quantity = quantity
        self.unit = unit

    @staticmethod
    def create(date, nomenclature, warehouse, quantity, unit):
        """
        Фабричный метод для создания экземпляра транзакции
        """
        return transaction_model(date, nomenclature, warehouse, quantity, unit)

    @staticmethod
    def from_dto(dto: transaction_dto, cache: dict) -> "transaction_model":
        """
        Преобразование transaction_dto → transaction_model
        """

        validator.validate(dto, transaction_dto)
        validator.validate(cache, dict)

        # Проверяем кэш
        if dto.id in cache:
            return cache[dto.id]

        if dto.date is None:
            raise operation_exception(f"Дата транзакции пуста для ID {dto.id}")

        nomenclature = cache.get(dto.nomenclature_id)
        if nomenclature is None:
            raise ValueError(f"Номенклатура с id {dto.nomenclature_id} не найдена")

        warehouse = cache.get(dto.warehouse_id)
        if warehouse is None:
            raise ValueError(f"Склад с id {dto.warehouse_id} не найден")

        unit = cache.get(dto.range_id)
        if unit is None:
            raise ValueError(f"Единица измерения с id {dto.range_id} не найдена")

        # Создаём транзакцию
        item = transaction_model.create(dto.date, nomenclature, warehouse, dto.quantity, unit)
        item.unique_code = dto.id

        # Добавляем в кэш
        cache[dto.id] = item
        return item
