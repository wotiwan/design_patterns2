from datetime import datetime
from Src.Core.validator import validator
from Src.reposity import reposity
from Src.Models.osv_line import osv_line
from Src.Logics.log_service import log_service

class osv_service:
    def __init__(self, start_service):
        self.start_service = start_service

    def generate(self, start_date, end_date, warehouse, transactions_override=None):
        log = log_service.get_instance()
        log.info(f"Generating OSV for {warehouse} from {start_date} to {end_date}")
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
            log.debug(f"Processed transaction {tr.unique_code}")
        log.info("OSV generation completed")
        return list(lines.values())