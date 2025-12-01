from abc import ABCMeta, abstractmethod


class Observer(metaclass=ABCMeta):
    """
    Абстрактный наблюдатель
    """

    @abstractmethod
    def update(self, message: dict) -> None:
        """
        Получение нового сообщения
        """
        pass
