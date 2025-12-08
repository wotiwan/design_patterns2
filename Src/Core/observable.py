from Src.Core.observer import Observer
from abc import ABCMeta


class observable(metaclass=ABCMeta):

    def __init__(self):
        self._observers: list[Observer] = []

    def register(self, obs: Observer):
        self._observers.append(obs)

    def notify(self, message: dict):
        for obs in self._observers:
            obs.update(message)
