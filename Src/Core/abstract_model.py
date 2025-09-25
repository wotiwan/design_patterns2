from abc import ABC
import uuid
from Src.Core.validator import validator

class abstact_model(ABC):
    __unique_code:str

    def __init__(self) -> None:
        super().__init__()
        self.__unique_code = uuid.uuid4().hex

    """
    Уникальный код
    """
    @property
    def unique_code(self) -> str:
        return self.__unique_code
    
    @unique_code.setter
    def unique_code(self, value: str):
        validator.validate(value, str)
        self.__unique_code = value.strip()
    

    """
    Перегрузка штатного варианта сравнения
    """
    def __eq__(self, value: str) -> bool:
        return self.__unique_code == value
