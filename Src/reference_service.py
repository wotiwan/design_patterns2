from typing import List

from Src.Core.observable import observable
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model


class reference_service(observable):

    def __init__(self):
        super().__init__()
        self._store = {
            nomenclature_model: [],
            range_model: [],
            group_model: [],
            warehouse_model: []
        }

    def add(self, item):
        t = type(item)
        if t not in self._store:
            raise ValueError("Unsupported type")

        self._store[t].append(item)

        self.notify({
            "action": "add",
            "type": t.__name__,
            "item": item
        })

        return item

    def update(self, prototype, update_data: dict):
        items = self.find(prototype)
        for obj in items:
            old = obj.clone()

            for field, value in update_data.items():
                setattr(obj, field, value)

            self.notify({
                "action": "update",
                "type": type(obj).__name__,
                "old": old,
                "new": obj
            })

        return len(items)

    def delete(self, prototype):
        items = self.find(prototype)
        for obj in items:

            self.notify({
                "action": "delete",
                "type": type(obj).__name__,
                "item": obj
            })

            self._store[type(obj)].remove(obj)

        return len(items)

    def find(self, prototype) -> List:
        t = type(prototype)
        if t not in self._store:
            raise ValueError("Unsupported type")

        return [x for x in self._store[t] if prototype.is_match(x)]
