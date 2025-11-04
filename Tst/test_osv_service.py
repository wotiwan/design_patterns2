import unittest
from datetime import datetime
from Src.Logics.osv_service import osv_service
from Src.start_service import start_service


class TestOSVService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        s = start_service()
        s.start()
        cls.service = osv_service(s)

    def test_generate_report(self):
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)
        warehouse_name = "Главный склад"

        report = self.service.generate(start_date, end_date, warehouse_name)
        self.assertIsInstance(report, list)
        self.assertGreater(len(report), 0)
        first_item = report[0]
        self.assertIn("nomenclature", first_item)
        self.assertIn("opening_balance", first_item)


if __name__ == '__main__':
    unittest.main()
