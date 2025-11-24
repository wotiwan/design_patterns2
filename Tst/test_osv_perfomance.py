import unittest
from datetime import datetime, timedelta
import time
import random
import os

from Src.start_service import start_service
from Src.Logics.osv_service import osv_service
from Src.reposity import reposity
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.transaction_model import transaction_model

class TestOSVPerformance(unittest.TestCase):

    def setUp(self):

        self.ss = start_service()
        self.ss.repo.data.clear()
        self.ss.repo.data.update({
            reposity.transaction_key(): [],
            reposity.warehouse_key(): [],
            reposity.nomenclature_key(): [],
            reposity.group_key(): [],
            reposity.range_key(): []
        })

        # Создаем базовые объекты
        self.gram = range_model.create("грамм", 1, None)
        self.ss.repo.data[reposity.range_key()].append(self.gram)

        self.group = group_model()
        self.group.name = "Ингредиенты"
        self.ss.repo.data[reposity.group_key()].append(self.group)

        self.wh = warehouse_model.create("Главный склад", "ул. Нагрузочная, 1")
        self.ss.repo.data[reposity.warehouse_key()].append(self.wh)

        self.nom = nomenclature_model.create("Мука", self.group, self.gram)
        self.nom.unique_code = "nom1"
        self.ss.repo.data[reposity.nomenclature_key()].append(self.nom)

        # Генерируем 1000+ транзакций
        start_date = datetime(2023, 1, 1)
        for i in range(1000):
            date = start_date + timedelta(days=random.randint(0, 365))
            qty = random.randint(-50, 100)
            tr = transaction_model(date, self.nom, self.wh, qty, self.gram)
            self.ss.repo.data[reposity.transaction_key()].append(tr)

        self.osv = osv_service(self.ss)

        # Markdown файл для отчета
        self.report_file = "osv_perf_report.md"
        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write("# Результаты нагрузочного теста ОСВ\n\n")
            f.write("| Дата блокировки | Время расчета (сек) |\n")
            f.write("|----------------|------------------|\n")

    def test_osv_performance_with_block_dates(self):
        block_dates = [
            datetime(2023, 1, 1),
            datetime(2023, 3, 1),
            datetime(2023, 6, 1),
            datetime(2023, 12, 31)
        ]

        for block_date in block_dates:
            start_time = time.time()
            self.osv.generate(datetime(1900, 1, 1), datetime(2024, 1, 1), "Главный склад")
            elapsed = time.time() - start_time

            # Записываем в Markdown
            with open(self.report_file, "a", encoding="utf-8") as f:
                f.write(f"| {block_date.date()} | {elapsed:.4f} |\n")

        print(f"\nОтчет сохранен в {os.path.abspath(self.report_file)}")

if __name__ == "__main__":
    unittest.main()
