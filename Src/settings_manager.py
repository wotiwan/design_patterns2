from src.models.company_model import company_model
import os
import json

####################################################3
# Менеджер настроек. 
# Предназначен для управления настройками и хранения параметров приложения
class settings_manager:
    __file_name:str = ""
    __company:company_model = None

    # Singletone
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance 
    
    def __init__(self, file_name:str):
        self.file_name =file_name
        self.default()

    # Параметры организации из настроек
    @property
    def company_setting(self) -> company_model:
        return self.__company


    # Полный путь к файлу настроек
    @file_name.setter
    def file_name(self, value:str):
        if value.strip() == "":
            return
        
        if os.path.exists(value):
            self.__file_name = value.strip()

    # Загрузить настройки из Json файла
    def load(self) -> bool:
        if self.__file_name.strip() == "":
            raise Exception("Не найден файл настроек!")

        try:
            file = file.open(self.__file_name)
            data = json.load(file)

            if "company" in data.keys():
                item = data["company"]
                
                self.__company.name = item["name"]
                return True

            return False
        except:
            return False

    # Параметры настроек по умолчанию
    def default(self):
        self.__company = company_model()
        self.__company.name = "Рога и копыта"


