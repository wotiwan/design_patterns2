from Src.Core.observer import Observer


class update_propagation_observer(Observer):

    def __init__(self, start_service):
        self.start_service = start_service

    def update(self, message: dict):
        if message["action"] != "update":
            return

        old = message["old"]
        new = message["new"]
        obj_type = message["type"]

        # Если изменилась номенклатура — обновляем рецепты, транзакции и остатки
        if obj_type.__name__ == "nomenclature_model":
            self._update_recipe_links(old, new)
            self._update_transactions(old, new)

    def _update_recipe_links(self, old, new):
        for recipe in self.start_service.data.get("recipe_model", []):
            if recipe.nomenclature == old:
                recipe.nomenclature = new

    def _update_transactions(self, old, new):
        for tr in self.start_service.data.get("transaction_model", []):
            if tr.nomenclature == old:
                tr.nomenclature = new
