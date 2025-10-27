from abc import ABC, abstractmethod


class abstract_converter(ABC):
    @abstractmethod
    def convert(self, obj) -> dict:
        """
        Абстрактный метод для преобразования объекта в словарь.
        :param obj: любой объект
        :return: словарь вида { 'имя_поля': 'значение_поля' }
        """
        pass
