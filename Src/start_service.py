from Src.reposity import reposity
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.validator import validator, argument_exception, operation_exception
import os
import json
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_item_model import receipt_item_model
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Dtos.range_dto import range_dto
from Src.Dtos.category_dto import category_dto

class start_service:
    # Репозиторий
    __repo: reposity = reposity()

    # Рецепт по умолчанию
    __default_receipt: receipt_model

    # Словарь который содержит загруженные и инициализованные инстансы нужных объектов
    # Ключ - id записи, значение - abstract_model
    __default_receipt_items = {}

    # Наименование файла (полный путь)
    __full_file_name:str = ""

    def __init__(self):
        self.__repo.initalize()

    # Singletone
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(start_service, cls).__new__(cls)
        return cls.instance 

    # Текущий файл
    @property
    def file_name(self) -> str:
        return self.__full_file_name

    # Полный путь к файлу настроек
    @file_name.setter
    def file_name(self, value:str):
        validator.validate(value, str)
        full_file_name = os.path.abspath(value)        
        if os.path.exists(full_file_name):
            self.__full_file_name = full_file_name.strip()
        else:
            raise argument_exception(f'Не найден файл настроек {full_file_name}')

    # Загрузить настройки из Json файла
    def load(self) -> bool:
        if self.__full_file_name == "":
            raise operation_exception("Не найден файл настроек!")

        try:
            with open( self.__full_file_name, 'r') as file_instance:
                settings = json.load(file_instance)

                if "default_receipt" in settings.keys():
                    data = settings["default_receipt"]
                    return self.convert(data)

            return False
        except Exception as e:
            error_message = str(e)
            return False
        
    # Сохранить элемент в репозитории
    def __save_item(self, key:str, dto, item):
        validator.validate(key, str)
        item.unique_code = dto.id
        self.__default_receipt_items.setdefault(dto.id, item)
        self.__repo.data[ key ].append(item)

    # Загрузить единицы измерений   
    def __convert_ranges(self, data: dict) -> bool:
        validator.validate(data, dict)
        ranges = data['ranges'] if 'ranges' in data else []    
        if len(ranges) == 0:
            return False
         
        for range in ranges:
            dto = range_dto().create(range)
            base  = self.__default_receipt_items[ dto.base_id ] if dto.base_id in self.__default_receipt_items else None
            item = range_model.create(dto.name, dto.value, base)
            self.__save_item( reposity.range_key(), dto, item )

        return True

    # Загрузить группы номенклатуры
    def __convert_groups(self, data: dict) -> bool:
        validator.validate(data, dict)
        categories =  data['categories'] if 'categories' in data else []    
        if len(categories) == 0:
            return False

        for category in  categories:
            dto = category_dto().create(category)    
            item = group_model.create(dto.name)
            self.__save_item( reposity.group_key(), dto, item )

        return True

    # Загрузить номенклатуру
    def __convert_nomenclatures(   self, data: dict) -> bool:
        validator.validate(data, dict)      
        nomenclatures = data['nomenclatures'] if 'nomenclatures' in data else []   
        if len(nomenclatures) == 0:
            return False
         
        for nomenclature in nomenclatures:
            dto = nomenclature_dto().create(nomenclature)
            range =  self.__default_receipt_items[ dto.range_id ] if dto.range_id in self.__default_receipt_items else None
            category =  self.__default_receipt_items[ dto.category_id] if dto.category_id in self.__default_receipt_items else None
            item  = nomenclature_model.create(dto.name, category, range)
            self.__save_item( reposity.nomenclature_key(), dto, item )

        return True        


    # Обработать полученный словарь    
    def convert(self, data: dict) -> bool:
        validator.validate(data, dict)

        # 1 Созданим рецепт
        cooking_time = data['cooking_time'] if 'cooking_time' in data else ""
        portions = int(data['portions']) if 'portions' in data else 0
        name =  data['name'] if 'name' in data else "НЕ ИЗВЕСТНО"
        self.__default_receipt = receipt_model.create(name, cooking_time, portions  )

        # Загрузим шаги приготовления
        steps =  data['steps'] if 'steps' in data else []
        for step in steps:
            if step.strip() != "":
                self.__default_receipt.steps.append( step )

        self.__convert_ranges(data)
        self.__convert_groups(data)
        self.__convert_nomenclatures(data)        


        # Собираем рецепт
        compositions =  data['composition'] if 'composition' in data else []      
        for composition in compositions:
            namnomenclature_id = composition['nomenclature_id'] if 'nomenclature_id' in composition else ""
            range_id = composition['range_id'] if 'range_id' in composition else ""
            value  = composition['value'] if 'value' in composition else ""
            nomenclature = self.__default_receipt_items[namnomenclature_id] if namnomenclature_id in self.__default_receipt_items else None
            range = self.__default_receipt_items[range_id] if range_id in self.__default_receipt_items else None
            item = receipt_item_model.create(  nomenclature, range, value)
            self.__default_receipt.composition.append(item)
            
        # Сохраняем рецепт
        self.__repo.data[ reposity.receipt_key() ].append(self.__default_receipt)
        return True

    """
    Стартовый набор данных
    """
    @property
    def data(self):
        return self.__repo.data   

    """
    Основной метод для генерации эталонных данных
    """
    def start(self):
        self.file_name = "settings.json"
        result = self.load()
        if result == False:
            raise operation_exception("Невозможно сформировать стартовый набор данных!")
        


