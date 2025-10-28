from Src.Core.abstract_response import abstract_response
from Src.Logics.convert_factory import convert_factory
from Src.Core.common import common
import json


class response_json(abstract_response):
    """
    Реализация ответа в формате JSON
    """

    def build(self, format: str, data: list) -> str:
        # Проверяем и подготавливаем базовую структуру
        super().build(format, data)

        # Преобразуем данные через фабрику
        factory = convert_factory()
        converted = factory.create(data)

        return json.dumps(converted, ensure_ascii=False, indent=2)
