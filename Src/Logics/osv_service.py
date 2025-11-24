from datetime import datetime
from Src.Core.validator import validator
from Src.reposity import reposity


class osv_service:
    """
    Сервис формирования оборотно-сальдовой ведомости (ОСВ)
    """

    def __init__(self, start_service):
        self.start_service = start_service
        self.locked_period_result = {}

    def generate(self, start_date: datetime, end_date: datetime, warehouse_name: str,
                 transactions_override=None) -> list:
        """
        Формирует отчет ОСВ по указанному складу и диапазону дат.
        """
        validator.validate(start_date, datetime)
        validator.validate(end_date, datetime)
        validator.validate(warehouse_name, str)

        warehouses = self.start_service.data.get(reposity.warehouse_key(), [])

        # используем override, если он передан
        transactions = transactions_override if transactions_override is not None else self.start_service.data.get(
            reposity.transaction_key(), [])

        nomenclatures = self.start_service.data.get(reposity.nomenclature_key(), [])

        warehouse = next((w for w in warehouses if getattr(w, "name", None) == warehouse_name), None)
        if not warehouse:
            raise ValueError(f"Склад '{warehouse_name}' не найден")

        report = {}
        for nom in nomenclatures:
            report[nom.unique_code] = {
                "nomenclature": nom.name,
                "unit": getattr(nom.unit, "name", "") if hasattr(nom, "unit") else "",
                "opening_balance": 0,
                "incoming": 0,
                "outgoing": 0,
                "closing_balance": 0
            }

        for tr in transactions:
            if getattr(tr, "warehouse", None) != warehouse:
                continue

            n_key = tr.nomenclature.unique_code
            if tr.date < start_date:
                report[n_key]["opening_balance"] += tr.quantity
            elif start_date <= tr.date <= end_date:
                if tr.quantity > 0:
                    report[n_key]["incoming"] += tr.quantity
                else:
                    report[n_key]["outgoing"] += abs(tr.quantity)

            report[n_key]["closing_balance"] = (
                    report[n_key]["opening_balance"] +
                    report[n_key]["incoming"] -
                    report[n_key]["outgoing"]
            )

        return list(report.values())

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
