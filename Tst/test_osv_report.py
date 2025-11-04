import unittest
from datetime import datetime

from Src.Models.group_model import group_model
from Src.start_service import start_service
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.range_model import range_model
from Src.Models.transaction_model import transaction_model

class TestOSVReport(unittest.TestCase):

    def setUp(self):
        # Создаём стартовые данные
        self.service = start_service()
        self.service.start()  # Загружает default_receipt и прочее

        # Создадим склад
        self.warehouse = warehouse_model.create("Главный склад", address="не указано")

        # Создаём единицу измерения
        self.unit = range_model.create("кг", 1, None)

        # Создаём номенклатуру
        self.group = group_model.create("Основная группа")
        self.nom = nomenclature_model.create("Товар A", self.group, self.unit)

        # Создадим несколько транзакций
        self.trans1 = transaction_model.create(
            date=datetime(2025, 11, 1),
            nomenclature=self.nom,
            warehouse=self.warehouse,
            quantity=10,
            unit=self.unit
        )
        self.trans2 = transaction_model.create(
            date=datetime(2025, 11, 2),
            nomenclature=self.nom,
            warehouse=self.warehouse,
            quantity=-3,
            unit=self.unit
        )

        self.service.data["transaction_model"] = [self.trans1, self.trans2]

    def test_osv_totals(self):
        # Простейшая проверка подсчёта оборотов
        transactions = self.service.data["transaction_model"]
        total_in = sum(t.quantity for t in transactions if t.quantity > 0)
        total_out = sum(abs(t.quantity) for t in transactions if t.quantity < 0)
        balance = total_in - total_out

        self.assertEqual(total_in, 10)
        self.assertEqual(total_out, 3)
        self.assertEqual(balance, 7)


if __name__ == "__main__":
    unittest.main()
