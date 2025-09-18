
###############################################
# Модель организации
class company_model:
    __name:str = ""
    __inn:str = ""

    # Наименование
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value:str):
        if value.strip() != "":
            self.__name = value.strip()


