import json
from Src.Core.observer import Observer


class settings_persistence_observer(Observer):

    def __init__(self, settings_file="appsettings.json"):
        self.settings_file = settings_file

    def update(self, message: dict):
        if message["type"].__name__ != "settings_model":
            return

        if message["action"] != "update":
            return

        new_settings = message["new"]

        data = {
            "lock_date": str(new_settings.lock_date),
            "other_settings": new_settings.other_settings_dict()
        }

        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print("[observer] Настройки сохранены в appsettings.json")
