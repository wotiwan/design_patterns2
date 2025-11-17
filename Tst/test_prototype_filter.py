import unittest
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Logics.prototype_report import prototype_report
from Src.Dtos.filter_dto import filter_dto
from Src.Core.filter_type import filter_type


class TestPrototypeFilter(unittest.TestCase):
    def setUp(self):
        # Создаем реальные объекты моделей
        self.group1 = group_model()
        self.group1.name = "Группа 1"
        self.group1.unique_code = "G001"

        self.base_unit = range_model.create("грамм", 1, None)
        self.unit_kg = range_model.create("киллограмм", 1000, self.base_unit)

        self.nom1 = nomenclature_model.create("Мука", self.group1, self.unit_kg)
        self.nom1.unique_code = "N001"
        self.nom2 = nomenclature_model.create("Сахар", self.group1, self.unit_kg)
        self.nom2.unique_code = "N002"

        self.items = [self.nom1, self.nom2]
        self.proto = prototype_report(self.items)

    def test_filter_equals_name(self):
        f = filter_dto()
        f.create({"entity": "nomenclature", "field": "name", "value": "Мука", "mode": "equals"})
        result = prototype_report.filter(self.proto.data, f)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Мука")

    def test_filter_like_name(self):
        f = filter_dto()
        f.create({"entity": "nomenclature", "field": "name", "value": "у", "mode": "like"})
        result = prototype_report.filter(self.proto.data, f)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Мука")

    def test_filter_equals_unique_code(self):
        f = filter_dto()
        f.create({"entity": "nomenclature", "field": "unique_code", "value": "N002", "mode": "equals"})
        result = prototype_report.filter(self.proto.data, f)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].unique_code, "N002")

    def test_filter_nested_base_unit(self):
        f = filter_dto()
        f.create({"entity": "nomenclature", "field": "range.base.name", "value": "грамм", "mode": "equals"})
        result = prototype_report.filter(self.proto.data, f)
        self.assertEqual(len(result), 2)  # оба имеют base = грамм

if __name__ == "__main__":
    unittest.main()
