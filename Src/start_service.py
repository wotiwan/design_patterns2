from Src.reposity import reposity
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.transaction_model import transaction_model
from Src.Core.validator import validator, argument_exception, operation_exception
import os
import json
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_item_model import receipt_item_model
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Dtos.range_dto import range_dto
from Src.Dtos.category_dto import category_dto

class start_service:
    __repo: reposity = reposity()
    __default_receipt: receipt_model
    __cache = {}
    __full_file_name: str = ""

    def __init__(self):
        self.__repo.initalize()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(start_service, cls).__new__(cls)
        return cls.instance

    @property
    def file_name(self) -> str:
        return self.__full_file_name

    @file_name.setter
    def file_name(self, value: str):
        validator.validate(value, str)
        full_file_name = os.path.abspath(value)
        if os.path.exists(full_file_name):
            self.__full_file_name = full_file_name.strip()
        else:
            raise argument_exception(f'Не найден файл настроек {full_file_name}')

    def load(self) -> bool:
        if self.__full_file_name == "":
            raise operation_exception("Не найден файл настроек!")

        try:
            with open(self.__full_file_name, 'r', encoding='utf-8') as file_instance:
                settings = json.load(file_instance)
                first_start = settings.get("first_start", True)
                if first_start:
                    if "default_receipt" in settings.keys():
                        data = settings["default_receipt"]
                        return self.convert(data)
                return False
        except Exception as e:
            print(str(e))
            return False

    def __save_item(self, key: str, dto, item):
        validator.validate(key, str)
        item.unique_code = dto.id
        self.__cache.setdefault(dto.id, item)
        self.__repo.data[key].append(item)

    def __convert_ranges(self, data: dict) -> bool:
        validator.validate(data, dict)
        ranges = data.get('ranges', [])
        if not ranges:
            return False
        for range in ranges:
            dto = range_dto().create(range)
            item = range_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.range_key(), dto, item)
        return True

    def __convert_groups(self, data: dict) -> bool:
        validator.validate(data, dict)
        categories = data.get('categories', [])
        if not categories:
            return False
        for category in categories:
            dto = category_dto().create(category)
            item = group_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.group_key(), dto, item)
        return True

    def __convert_nomenclatures(self, data: dict) -> bool:
        validator.validate(data, dict)
        nomenclatures = data.get('nomenclatures', [])
        if not nomenclatures:
            return False
        for nomenclature in nomenclatures:
            dto = nomenclature_dto().create(nomenclature)
            item = nomenclature_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.nomenclature_key(), dto, item)
        return True

    def convert(self, data: dict) -> bool:
        validator.validate(data, dict)
        # Рецепт
        cooking_time = data.get('cooking_time', "")
        portions = int(data.get('portions', 0))
        name = data.get('name', "НЕ ИЗВЕСТНО")
        self.__default_receipt = receipt_model.create(name, cooking_time, portions)

        for step in data.get('steps', []):
            if step.strip():
                self.__default_receipt.steps.append(step)

        self.__convert_ranges(data)
        self.__convert_groups(data)
        self.__convert_nomenclatures(data)

        compositions = data.get('composition', [])
        for composition in compositions:
            nomenclature_id = composition.get('nomenclature_id', "")
            range_id = composition.get('range_id', "")
            value = composition.get('value', "")
            nomenclature = self.__cache.get(nomenclature_id)
            range_ = self.__cache.get(range_id)
            item = receipt_item_model.create(nomenclature, range_, value)
            self.__default_receipt.composition.append(item)

        self.__repo.data[reposity.receipt_key()].append(self.__default_receipt)

        # Создаём склад
        if not self.__repo.data[reposity.warehouse_key()]:
            main_warehouse = warehouse_model.create("Главный склад", "Адрес по умолчанию")
            self.__repo.data[reposity.warehouse_key()] = [main_warehouse]

        if not self.__repo.data[reposity.transaction_key()]:
            self.__repo.data[reposity.transaction_key()] = []

        return True

    @property
    def data(self):
        return self.__repo.data

    def start(self):
        self.file_name = "settings.json"
        result = self.load()
        if not result:
            raise operation_exception("Невозможно сформировать стартовый набор данных!")
