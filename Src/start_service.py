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
from Src.Dtos.transaction_dto import transaction_dto
from Src.Dtos.warehouse_dto import warehouse_dto
from Src.reference_service import reference_service
from Src.reference_observer import reference_observer

from Src.Observers.delete_guard_observer import delete_guard_observer
from Src.Observers.balance_recalculate_observer import balance_recalculate_observer
from Src.Observers.settings_persistence_observer import settings_persistence_observer
from Src.Observers.update_propagation_observer import update_propagation_observer


class start_service:
    __repo: reposity = reposity()
    __default_receipt: receipt_model
    __cache = {}
    __full_file_name: str = ""

    def __init__(self):
        self.observer = reference_observer(self)
        self.reference_service = reference_service()

        self.reference_service.register(delete_guard_observer(start_service))
        self.reference_service.register(balance_recalculate_observer(start_service))
        self.reference_service.register(update_propagation_observer(start_service))
        self.reference_service.register(settings_persistence_observer("appsettings.json"))

        self.__repo.initalize()

    def __new__(cls):
        if not hasattr(cls, "instance"):
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
            raise argument_exception(f"Не найден файл настроек {full_file_name}")

    def load(self) -> bool:
        if self.__full_file_name == "":
            raise operation_exception("Не найден файл настроек!")

        try:
            with open(self.__full_file_name, "r", encoding="utf-8") as file_instance:
                settings = json.load(file_instance)
                first_start = settings.get("first_start", True)
                if first_start:
                    return self.convert(settings)
                return False
        except Exception as e:
            print(str(e))
            return False

    def __save_item(self, key: str, dto, item):
        validator.validate(key, str)
        item.unique_code = dto.id
        self.__cache[dto.id] = item
        self.__repo.data[key].append(item)

    def __convert_ranges(self, data: dict) -> bool:
        validator.validate(data, dict)
        ranges = data.get("ranges", [])
        if not ranges:
            return False
        for r in ranges:
            dto = range_dto().create(r)
            item = range_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.range_key(), dto, item)
        return True

    def __convert_groups(self, data: dict) -> bool:
        validator.validate(data, dict)
        categories = data.get("categories", [])
        if not categories:
            return False
        for category in categories:
            dto = category_dto().create(category)
            item = group_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.group_key(), dto, item)
        return True

    def __convert_nomenclatures(self, data: dict) -> bool:
        validator.validate(data, dict)
        nomenclatures = data.get("nomenclatures", [])
        if not nomenclatures:
            return False
        for nom in nomenclatures:
            dto = nomenclature_dto().create(nom)
            item = nomenclature_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.nomenclature_key(), dto, item)
        return True

    def __create_warehouse(self):
        """
        Создание базового склада (если отсутствует)
        """
        if not self.__repo.data[reposity.warehouse_key()]:
            main_wh = warehouse_model.create("Главный склад", "Адрес по умолчанию")
            self.__repo.data[reposity.warehouse_key()] = [main_wh]
        return True

    def convert(self, data: dict) -> bool:
        validator.validate(data, dict)
        default_receipt = data.get("default_receipt", {})

        try:
            # --- 1. Создание рецепта
            cooking_time = default_receipt.get('cooking_time', "")
            portions = int(default_receipt.get('portions', 0))
            name = default_receipt.get('name', "НЕ ИЗВЕСТНО")
            self.__default_receipt = receipt_model.create(name, cooking_time, portions)

            for step in default_receipt.get('steps', []):
                if step.strip():
                    self.__default_receipt.steps.append(step)

            # --- 2. Диапазоны, категории, номенклатура
            self.__convert_ranges(default_receipt)
            self.__convert_groups(default_receipt)
            self.__convert_nomenclatures(default_receipt)

            # --- 3. Склады
            warehouses = data.get('warehouses', [])
            self.__repo.data[reposity.warehouse_key()] = []
            for warehouse in warehouses:
                dto = warehouse_dto().create(warehouse)
                item = warehouse_model.from_dto(dto, self.__cache)
                self.__save_item(reposity.warehouse_key(), dto, item)

            # --- 4. Транзакции
            transactions = data.get('transactions', [])
            self.__repo.data[reposity.transaction_key()] = []
            for tr in transactions:
                dto = transaction_dto().create(tr)
                item = transaction_model.from_dto(dto, self.__cache)
                self.__save_item(reposity.transaction_key(), dto, item)

            # --- 5. Состав рецепта
            compositions = default_receipt.get('composition', [])
            for composition in compositions:
                nomenclature_id = composition.get('nomenclature_id', "")
                range_id = composition.get('range_id', "")
                value = composition.get('value', "")
                nomenclature = self.__cache.get(nomenclature_id)
                range_ = self.__cache.get(range_id)
                item = receipt_item_model.create(nomenclature, range_, value)
                self.__default_receipt.composition.append(item)

            self.__repo.data[reposity.receipt_key()].append(self.__default_receipt)
            return True

        except Exception as e:
            raise

    @property
    def data(self):
        return self.__repo.data

    def start(self):
        self.file_name = "settings.json"
        result = self.load()
        if not result:
            raise operation_exception("Невозможно сформировать стартовый набор данных!")
