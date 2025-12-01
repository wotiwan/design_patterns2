from datetime import datetime
from Src.Core.validator import validator
from Src.reposity import reposity
from Src.Models.osv_line import osv_line


class osv_service:
    """
    Сервис формирования оборотно-сальдовой ведомости (ОСВ)
    """

    def __init__(self, start_service):
        self.start_service = start_service
        self.locked_period_result = {}

    def generate(self, start_date, end_date, warehouse, transactions_override=None):
        items = transactions_override or self.start_service.data["transaction_model"]

        lines = {}

        for tr in items:
            if tr.warehouse.name != warehouse:
                continue

            if tr.date < start_date or tr.date > end_date:
                continue

            code = tr.nomenclature.unique_code

            if code not in lines:
                lines[code] = osv_line(tr.nomenclature)

            line = lines[code]

            if tr.quantity > 0:
                line.incoming += tr.quantity
            else:
                line.outgoing += abs(tr.quantity)

        # итог: список настоящих доменных объектов
        return list(lines.values())

    def calculate_with_block(self, start_date: datetime, end_date: datetime, warehouse_name: str):
        """
        Расчёт ОСВ с учетом даты блокировки.
        Использует заранее сохраненные locked_period_result.
        """

        # Проверка наличия данных до даты блокировки
        if not hasattr(self, "locked_period_result") or not self.locked_period_result:
            raise ValueError("Обороты до даты блокировки не рассчитаны. "
                             "Сначала вызовите calculate_locked_period().")

        warehouses = self.start_service.data.get(reposity.warehouse_key(), [])
        transactions = self.start_service.data.get(reposity.transaction_key(), [])
        nomenclatures = self.start_service.data.get(reposity.nomenclature_key(), [])

        warehouse = next((w for w in warehouses if w.name == warehouse_name), None)
        if warehouse is None:
            raise ValueError(f"Склад '{warehouse_name}' не найден")

        import copy
        result = copy.deepcopy(self.locked_period_result)

        # Дата блокировки
        settings = self.start_service.data.get("settings_model")
        block_period = settings.block_period

        # Проверка диапазона
        if start_date < block_period:
            raise ValueError("start_date < block_period. "
                             "Используйте calculate_locked_period() для до-блокировочного периода")

        for tr in transactions:

            if tr.warehouse != warehouse:
                continue

            # Транзакции только в диапазоне block_period → end_date
            if not (block_period <= tr.date <= end_date):
                continue

            code = tr.nomenclature.unique_code

            if tr.quantity > 0:
                result[code]["incoming"] += tr.quantity
            else:
                result[code]["outgoing"] += abs(tr.quantity)

        for code, rec in result.items():
            rec["closing_balance"] = (
                    rec["opening_balance"] +
                    rec["incoming"] -
                    rec["outgoing"]
            )

        return result
