from Src.Core.observer import Observer
from Src.Logics.osv_service import osv_service


class balance_recalculate_observer(Observer):

    def __init__(self, start_service):
        self.start_service = start_service

    def update(self, message: dict):
        if message["action"] not in ("update", "delete"):
            return

        lock_date = self.start_service.settings.lock_date

        osv = osv_service(self.start_service)
        osv.recalculate_until(lock_date)
