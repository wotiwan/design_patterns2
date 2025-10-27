
# Форматы ответов
class response_formats:

    @staticmethod
    def csv() -> str:
        return "csv"
    
    @staticmethod
    def excel() -> str:
        return "excel"
    
    @staticmethod
    def json() -> str:
        return "json"

    @staticmethod
    def markdown() -> str:
        return "markdown"

    @staticmethod
    def get_all_formats() -> list:
        return ["scv", "excel", "json", "markdown"]