from Src.Core.observer import Observer
from Src.reposity import reposity


class delete_guard_observer(Observer):

    def __init__(self, start_service):
        self.start_service = start_service

    def update(self, message: dict):
        if message["action"] != "delete":
            return

        obj = message["old"]
        obj_type = message["type"]

        # Номенклатуру нельзя удалить, если она есть в рецептах
        if obj_type.__name__ == "nomenclature_model":
            for recipe in self.start_service.data.get("recipe_model", []):
                if recipe.nomenclature == obj:
                    raise Exception(
                        f"Нельзя удалить номенклатуру '{obj.name}': она используется в рецепте {recipe.unique_code}"
                    )

            # Проверяем обороты и транзакции
            for tr in self.start_service.data.get("transaction_model", []):
                if tr.nomenclature == obj:
                    raise Exception(
                        f"Нельзя удалить номенклатуру '{obj.name}': она используется в транзакциях."
                    )

        # Нельзя удалить склад — если есть транзакции
        if obj_type.__name__ == "warehouse_model":
            for tr in self.start_service.data.get("transaction_model", []):
                if tr.warehouse == obj:
                    raise Exception(
                        f"Нельзя удалить склад '{obj.name}': он используется в транзакциях."
                    )
