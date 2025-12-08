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
from Src.Logics.log_service import log_service

class start_service:
    __repo: reposity = reposity()
    __default_receipt: receipt_model = None
    __cache = {}
    __full_file_name: str = ""

    def __init__(self):
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
        log = log_service.get_instance()
        log.info("Loading initial data")
        if self.__full_file_name == "":
            log.error("No settings file specified")
            raise operation_exception("Не найден файл настроек!")
        try:
            with open(self.__full_file_name, "r", encoding="utf-8") as file_instance:
                settings = json.load(file_instance)
            first_start = settings.get("first_start", True)
            if first_start:
                log.debug("First start, converting data")
                return self.convert(settings)
            else:
                log.info("Not first start, skipping conversion")
                return False
        except Exception as e:
            log.error(f"Error loading data: {str(e)}")
            print(str(e))
            return False

    def __save_item(self, key: str, dto, item):
        log = log_service.get_instance()
        log.debug(f"Saving {key} item with ID {dto.id}")
        validator.validate(key, str)
        item.unique_code = dto.id
        self.__cache[dto.id] = item
        self.__repo.data[key].append(item)

    def __convert_ranges(self, data: dict) -> bool:
        log = log_service.get_instance()
        validator.validate(data, dict)
        ranges = data.get("ranges", [])
        if not ranges:
            log.debug("No ranges to convert")
            return False
        for r in ranges:
            dto = range_dto().create(r)
            item = range_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.range_key(), dto, item)
        log.info("Ranges converted")
        return True

    def __convert_groups(self, data: dict) -> bool:
        log = log_service.get_instance()
        validator.validate(data, dict)
        categories = data.get("categories", [])
        if not categories:
            log.debug("No groups to convert")
            return False
        for category in categories:
            dto = category_dto().create(category)
            item = group_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.group_key(), dto, item)
        log.info("Groups converted")
        return True

    def __convert_nomenclatures(self, data: dict) -> bool:
        log = log_service.get_instance()
        validator.validate(data, dict)
        nomenclatures = data.get("nomenclatures", [])
        if not nomenclatures:
            log.debug("No nomenclatures to convert")
            return False
        for nom in nomenclatures:
            dto = nomenclature_dto().create(nom)
            item = nomenclature_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.nomenclature_key(), dto, item)
        log.info("Nomenclatures converted")
        return True

    def __create_warehouse(self):
        log = log_service.get_instance()
        if not self.__repo.data[reposity.warehouse_key()]:
            main_wh = warehouse_model.create("Главный склад", "Адрес по умолчанию")
            self.__repo.data[reposity.warehouse_key()] = [main_wh]
            log.info("Default warehouse created")
        return True

    def convert(self, data: dict) -> bool:
        log = log_service.get_instance()
        log.info("Starting data conversion")
        validator.validate(data, dict)
        default_receipt = data.get("default_receipt", {})
        try:
            cooking_time = default_receipt.get('cooking_time', "")
            portions = int(default_receipt.get('portions', 0))
            name = default_receipt.get('name', "НЕ ИЗВЕСТНО")
            self.__default_receipt = receipt_model.create(name, cooking_time, portions)
            log.debug(f"Created default receipt: {name}")
            for step in default_receipt.get('steps', []):
                if step.strip():
                    self.__default_receipt.steps.append(step)
            self.__convert_ranges(default_receipt)
            self.__convert_groups(default_receipt)
            self.__convert_nomenclatures(default_receipt)
            warehouses = data.get('warehouses', [])
            self.__repo.data[reposity.warehouse_key()] = []
            for warehouse in warehouses:
                dto = warehouse_dto().create(warehouse)
                item = warehouse_model.from_dto(dto, self.__cache)
                self.__save_item(reposity.warehouse_key(), dto, item)
            transactions = data.get('transactions', [])
            self.__repo.data[reposity.transaction_key()] = []
            for tr in transactions:
                dto = transaction_dto().create(tr)
                item = transaction_model.from_dto(dto, self.__cache)
                self.__save_item(reposity.transaction_key(), dto, item)
            compositions = default_receipt.get('composition', [])
            for composition in compositions:
                nomenclature_id = composition.get('nomenclature_id', "")
                range_id = composition.get('range_id', "")
                value = composition.get('value', "")
                nomenclature = self.__cache.get(nomenclature_id)
                range_ = self.__cache.get(range_id)
                item = receipt_item_model.create(nomenclature, range_, value)
                self.__default_receipt.composition.append(item)
                log.debug("Added composition item")
            self.__repo.data[reposity.receipt_key()].append(self.__default_receipt)
            log.info("Data conversion completed")
            return True
        except Exception as e:
            log.error(f"Conversion error: {str(e)}")
            raise

    @property
    def data(self):
        return self.__repo.data

    def start(self):
        log = log_service.get_instance()
        log.info("Starting service")
        self.file_name = "settings.json"
        result = self.load()
        if not result:
            log.error("Failed to form initial data set")
            raise operation_exception("Невозможно сформировать стартовый набор данных!")