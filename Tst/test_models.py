from Src.settings_manager import settings_manager
from Src.Models.company_model import company_model
import unittest


class test_models(unittest.TestCase):

    # Провери создание основной модели
    # Данные после создания должны быть пустыми
    def test_empty_createmodel_companymodel(self):
        # Подготовка
        model = company_model()

        # Действие

        # Проверки
        assert model.name == ""


    # Проверить создание основной модели
    # Данные меняем. Данные должны быть
    def test_notEmpty_createmodel_companymodel(self):
        # Подготовка
        model = company_model()
        
        # Действие
        model.name = "test"
        
        # Проверки
        assert model.name != ""

    def test_load_createmodel_companymodel(self):
        # Подготовка
       file_name = "/home/valex/Projects/Patterns2025/settings.json"
       manager = settings_manager(file_name)
       
       # Дейсвтие
       result = manager.load()
            
       # Проверки
       assert result == True



    def test_loadCombo_createmodel_companymodel(self):
        # Подготовка
       file_name = "/home/valex/Projects/Patterns2025/settings.json"
       manager1 = settings_manager(file_name)
       manager2 = settings_manager(file_name)


       # Дейсвтие
       manager1.load()
       # manager2.load()

       # Проверки
       assert manager1.company == manager2.company
  
if __name__ == '__main__':
    unittest.main()   
