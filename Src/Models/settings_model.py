from Src.Models.company_model import company_model
from Src.Core.validator import validator

class settings_model:
    __company: company_model = None
    __response_format: str = "Json"
    __log_level: str = "INFO"
    __log_output: str = "console"
    __log_file: str = "app.log"

    @property
    def company(self) -> company_model:
        return self.__company

    @company.setter
    def company(self, value: company_model):
        validator.validate(value, company_model)
        self.__company = value

    @property
    def response_format(self) -> str:
        return self.__response_format

    @response_format.setter
    def response_format(self, value: str):
        allowed_formats = ["CSV", "Markdown", "Json", "XML"]
        validator.validate(value, str)
        if value not in allowed_formats:
            raise ValueError(f"Некорректный формат ответа: {value}. Допустимые значения: {allowed_formats}")
        self.__response_format = value

    @property
    def log_level(self) -> str:
        return self.__log_level

    @log_level.setter
    def log_level(self, value: str):
        allowed_levels = ["DEBUG", "INFO", "ERROR"]
        if value.upper() not in allowed_levels:
            raise ValueError(f"Некорректный уровень логирования: {value}")
        self.__log_level = value.upper()

    @property
    def log_output(self) -> str:
        return self.__log_output

    @log_output.setter
    def log_output(self, value: str):
        allowed_outputs = ["console", "file", "both"]
        if value.lower() not in allowed_outputs:
            raise ValueError(f"Некорректный вывод логирования: {value}")
        self.__log_output = value.lower()

    @property
    def log_file(self) -> str:
        return self.__log_file

    @log_file.setter
    def log_file(self, value: str):
        validator.validate(value, str)
        self.__log_file = value