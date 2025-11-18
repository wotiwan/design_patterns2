from datetime import datetime
from Src.Core.validator import validator
from Src.reposity import reposity


class osv_service:
    """
    Сервис формирования оборотно-сальдовой ведомости (ОСВ)
    """

    def __init__(self, start_service):
        self.start_service = start_service

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

