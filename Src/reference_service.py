from typing import List

from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model
from Src.Core.observer import observer

class reference_service:

    def __init__(self):
        self._store = {
            nomenclature_model: [],
            range_model: [],
            group_model: [],
            warehouse_model: []
        }
        self.observers: list[observer] = []

    def subscribe(self, observer: observer):
        self.observers.append(observer)

    def notify_added(self, item):
        for obs in self.observers:
            obs.on_added(item)

    def notify_updated(self, old_item, new_item):
        for obs in self.observers:
            obs.on_updated(old_item, new_item)

    def notify_deleted(self, item):
        for obs in self.observers:
            obs.on_deleted(item)

    def add(self, item):
        item_type = type(item)
        if item_type not in self._store:
            raise ValueError(f"Unsupported reference type: {item_type}")
        self._store[item_type].append(item)
        self.notify_added(item)
        return item

    def update(self, prototype, update_data: dict):
        """
        update_data — словарь с изменяемыми полями
        """
        items = self.find(prototype)
        for obj in items:
            old_copy = obj.clone()
            for field, value in update_data.items():
                setattr(obj, field, value)
            self.notify_updated(old_copy, obj)
        return len(items)

    def delete(self, prototype):
        items = self.find(prototype)
        for obj in items:
            self.notify_deleted(obj)
            self._store[type(obj)].remove(obj)
        return len(items)

    def find(self, prototype) -> List:
        entity_type = type(prototype)
        if entity_type not in self._store:
            raise ValueError(f"Unsupported reference type: {entity_type}")

        return [x for x in self._store[entity_type] if prototype.is_match(x)]


    def add_nomenclature(self, item: nomenclature_model): return self.add(item)
    def add_unit(self, item: range_model): return self.add(item)
    def add_group(self, item: group_model): return self.add(item)
    def add_warehouse(self, item: warehouse_model): return self.add(item)

    def find_nomenclature(self, proto: nomenclature_model): return self.find(proto)
    def find_unit(self, proto: range_model): return self.find(proto)
    def find_group(self, proto: group_model): return self.find(proto)
    def find_warehouse(self, proto: warehouse_model): return self.find(proto)

    def delete_nomenclature(self, proto: nomenclature_model): return self.delete(proto)
    def delete_unit(self, proto: range_model): return self.delete(proto)
    def delete_group(self, proto: group_model): return self.delete(proto)
    def delete_warehouse(self, proto: warehouse_model): return self.delete(proto)

    def update_nomenclature(self, proto, data): return self.update(proto, data)
    def update_unit(self, proto, data): return self.update(proto, data)
    def update_group(self, proto, data): return self.update(proto, data)
    def update_warehouse(self, proto, data): return self.update(proto, data)
