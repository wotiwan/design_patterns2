from datetime import datetime
from Src.Core.abstract_model import abstact_model
from Src.Core.validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.range_model import range_model


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
