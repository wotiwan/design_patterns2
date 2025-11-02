from Src.Core.abstract_model import abstact_model
from Src.Core.validator import validator


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
