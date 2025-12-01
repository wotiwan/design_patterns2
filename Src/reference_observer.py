import json
from Src.reposity import reposity
from Src.Logics.prototype_report import prototype_report
from datetime import datetime
from Src.Logics.osv_service import osv_service


class reference_observer:
    def __init__(self, start_service):
        self.start_service = start_service

    def on_deleted(self, item):
        repo_key = item.__class__.repo_key()

        # 1. Если удаляем номенклатуру – она могла использоваться в рецептах
        if repo_key == reposity.nomenclature_key():
            recipes = self.start_service.data.get(reposity.receipt_key(), [])
            for r in recipes:
                if item in r.items:
                    raise Exception(f"Нельзя удалить — номенклатура '{item.name}' используется в рецепте '{r.name}'")

        # 2. Она могла использоваться в транзакциях
        transactions = self.start_service.data.get(reposity.transaction_key(), [])
        for t in transactions:
            if t.nomenclature == item:
                raise Exception(f"Нельзя удалить — '{item.name}' используется в движениях (transaction #{t.id})")

        # 3. Если склад — могут быть транзакции
        if repo_key == reposity.warehouse_key():
            for t in transactions:
                if t.warehouse == item:
                    raise Exception(f"Нельзя удалить — склад '{item.name}' используется в транзакции {t.id}")

    def on_updated(self, old_item, new_item):
        repo_key = new_item.__class__.repo_key()

        # Номенклатура — обновить в рецептах
        if repo_key == reposity.nomenclature_key():
            recipes = self.start_service.data.get(reposity.receipt_key(), [])
            for r in recipes:
                r.replace_nomenclature(old_item, new_item)

        # Обновить в транзакциях
        transactions = self.start_service.data.get(reposity.transaction_key(), [])
        for t in transactions:
            if t.nomenclature == old_item:
                t.nomenclature = new_item

        # Пересчитать остатки
        self.recalculate_osv()

        # Записать изменения в настройки
        self.write_settings()

    def on_added(self, item):
        self.write_settings()

    def recalculate_osv(self):
        block_date = self.start_service.settings.block_date
        osv = osv_service(self.start_service)
        osv.generate(block_date, datetime.now(), None)

    def write_settings(self):
        file = self.start_service.file_name or "appsettings.json"
        with open(file, "w", encoding="utf-8") as f:
            json.dump(self.start_service.settings.to_dict(), f, ensure_ascii=False, indent=4)
