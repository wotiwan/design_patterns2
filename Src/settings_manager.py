from Src.Models.settings_model import settings_model
from Src.Core.validator import argument_exception, operation_exception, validator
from Src.Models.company_model import company_model
from Src.Core.common import common
import os
import json

class settings_manager:
    __full_file_name: str = ""
    __settings: settings_model = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.set_default()

    @property
    def settings(self) -> settings_model:
        return self.__settings

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
        from Src.Logics.log_service import log_service
        log = log_service.get_instance()
        log.info("Loading settings from file")
        if self.__full_file_name == "":
            log.error("Settings file not found")
            raise operation_exception("Не найден файл настроек!")
        try:
            with open(self.__full_file_name, 'r') as file_instance:
                settings = json.load(file_instance)
            if "company" in settings:
                data = settings["company"]
                self.convert(data)
            if "response_format" in settings:
                self.__settings.response_format = settings["response_format"]
            if "log_level" in settings:
                self.__settings.log_level = settings["log_level"]
            if "log_output" in settings:
                self.__settings.log_output = settings["log_output"]
            if "log_file" in settings:
                self.__settings.log_file = settings["log_file"]
            log.info("Settings loaded successfully")
            return True
        except Exception as e:
            log.error(f"Error loading settings: {str(e)}")
            return False

    def convert(self, data: dict) -> bool:
        from Src.Logics.log_service import log_service
        log = log_service.get_instance()
        log.debug("Converting company data")
        validator.validate(data, dict)
        fields = common.get_fields(self.__settings.company)
        matching_keys = list(filter(lambda key: key in fields, data.keys()))
        try:
            for key in matching_keys:
                setattr(self.__settings.company, key, data[key])
            log.debug("Company data converted successfully")
            return True
        except Exception as e:
            log.error(f"Error converting company data: {str(e)}")
            return False

    def set_default(self):
        company = company_model()
        company.name = "Рога и копыта"
        company.inn = -1
        self.__settings = settings_model()
        self.__settings.company = company