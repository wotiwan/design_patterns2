import unittest
from datetime import datetime

from Src.start_service import start_service
from Src.Models.settings_model import settings_model
from Src.Logics.osv_service import osv_service
from Src.reposity import reposity

from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.transaction_model import transaction_model

class TestLockedPeriodBalances(unittest.TestCase):

    def setUp(self):
        # Создаем сервис с тестовыми данными
        self.ss = start_service()
        # Чистим репозиторий через прямой доступ к объекту репо
        self.ss.repo.data.clear()
        self.ss.repo.data.update({
            reposity.transaction_key(): [],
            reposity.warehouse_key(): [],
            reposity.nomenclature_key(): [],
            reposity.group_key(): [],
            reposity.range_key(): []
        })

        # Создаем базовые объекты
        # Единицы измерения
        gram = range_model.create("грамм", 1, None)
        self.ss.repo.data[reposity.range_key()].append(gram)

        # Группа номенклатуры
        group = group_model()
        group.name = "Ингредиенты"
        self.ss.repo.data[reposity.group_key()].append(group)

        # Склады
        main_wh = warehouse_model.create("Главный склад", "ул. Тестовая, 1")
        self.ss.repo.data[reposity.warehouse_key()].append(main_wh)

        # Номенклатура
        nom = nomenclature_model.create("Мука", group, gram)
        nom.unique_code = "nom1"
        self.ss.repo.data[reposity.nomenclature_key()].append(nom)

        # Транзакции
        tr1 = transaction_model(datetime(2023, 1, 10), nom, main_wh, 100, gram)
        tr2 = transaction_model(datetime(2023, 2, 5), nom, main_wh, -20, gram)
        tr3 = transaction_model(datetime(2023, 3, 1), nom, main_wh, 40, gram)
        tr4 = transaction_model(datetime(2023, 4, 1), nom, main_wh, -10, gram)
        self.ss.repo.data[reposity.transaction_key()].extend([tr1, tr2, tr3, tr4])

        # Настройки с датой блокировки
        self.settings = settings_model()
        self.settings.block_date = datetime(2023, 3, 1)

        # Сервис ОСВ
        self.osv = osv_service(self.ss)

    def test_balances_stable_with_different_block_date(self):
        # Расчет без учета блокировки
        result_no_block = self.osv.generate(
            datetime(1900, 1, 1),
            datetime(2024, 1, 1),
            "Главный склад"
        )

        # Расчет с блокировкой в марте
        self.settings.block_date = datetime(2023, 3, 1)
        result_block_march = self.osv.generate(
            datetime(1900, 1, 1),
            datetime(2024, 1, 1),
            "Главный склад"
        )

        # Расчет с блокировкой в феврале
        self.settings.block_date = datetime(2023, 2, 1)
        result_block_feb = self.osv.generate(
            datetime(1900, 1, 1),
            datetime(2024, 1, 1),
            "Главный склад"
        )

        # Проверяем, что все результаты одинаковые
        self.assertEqual(result_no_block, result_block_march)
        self.assertEqual(result_no_block, result_block_feb)

if __name__ == "__main__":
    unittest.main()
