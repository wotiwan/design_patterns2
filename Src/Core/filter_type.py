from enum import Enum


class filter_type(Enum):
    EQUALS = "equals"   # Полное совпадение
    LIKE = "like"       # Вхождение строки
