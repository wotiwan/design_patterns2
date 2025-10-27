import unittest
from datetime import datetime
from Src.Logics.basic_converter import basic_converter
from Src.Logics.datetime_converter import datetime_converter
from Src.Logics.reference_converter import reference_converter
from Src.Core.validator import argument_exception


# Простейший объект для теста reference_converter
class DummyReference:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class TestConverters(unittest.TestCase):

    # Тесты basic_converter
    def test_basic_int(self):
        conv = basic_converter()
        self.assertEqual(conv.convert(42), {"value": 42})

    def test_basic_float(self):
        conv = basic_converter()
        self.assertEqual(conv.convert(3.14), {"value": 3.14})

    def test_basic_str(self):
        conv = basic_converter()
        self.assertEqual(conv.convert("hello"), {"value": "hello"})

    def test_basic_bool(self):
        conv = basic_converter()
        self.assertEqual(conv.convert(True), {"value": True})

    def test_basic_none(self):
        conv = basic_converter()
        with self.assertRaises(argument_exception):
            conv.convert(None)

    # Тесты datetime_converter
    def test_datetime_conversion(self):
        conv = datetime_converter()
        dt = datetime(2025, 10, 27, 14, 5, 30)
        self.assertEqual(conv.convert(dt), {"value": "2025-10-27T14:05:30"})

    def test_datetime_none(self):
        conv = datetime_converter()
        with self.assertRaises(argument_exception):
            conv.convert(None)

    # Тесты reference_converter
    def test_reference_conversion(self):
        conv = reference_converter()
        obj = DummyReference(id=1, name="Test")
        self.assertEqual(conv.convert(obj), {"id": 1, "name": "Test"})

    def test_reference_empty_fields(self):
        conv = reference_converter()
        class Empty:
            pass
        obj = Empty()
        with self.assertRaises(argument_exception):
            conv.convert(obj)

    def test_reference_none(self):
        conv = reference_converter()
        with self.assertRaises(argument_exception):
            conv.convert(None)


if __name__ == "__main__":
    unittest.main()
