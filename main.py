import json
from datetime import datetime
import connexion
from Src.Logics.factory_entities import factory_entities
from Src.settings_manager import settings_manager
from Src.Core.response_format import response_formats
from flask import Flask, request, jsonify
from Src.reposity import reposity
from Src.start_service import start_service
from Src.Models.transaction_model import transaction_model
from Src.Models.warehouse_model import warehouse_model
from Src.Logics.reference_converter import reference_converter
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.prototype_report import prototype_report
from Src.Logics.osv_service import osv_service
from Src.Logics.log_service import log_service

app = Flask(__name__)
start_service = start_service()
factory = factory_entities()
formats = {}

@app.route("/api/accessibility", methods=['GET'])
def accessibility():
    log = log_service.get_instance()
    log.info("Accessibility endpoint called")
    return "SUCCESS"

@app.route("/api/data/<data_type>/<format>", methods=['GET'])
def get_data_formatted(data_type: str, format: str):
    log = log_service.get_instance()
    log.info(f"Get data endpoint called for type {data_type} format {format}")
    if data_type not in reposity.keys():
        log.error(f"Invalid data_type: {data_type}")
        return {"error": "Wrong data_type"}, 400
    if format not in response_formats.get_all_formats():
        log.error(f"Invalid format: {format}")
        return {"error": "Wrong format"}, 400
    try:
        data = start_service.data[data_type]
        logic = factory.create(format)()
        result = logic.build(format, data)
        log.debug("Data formatted successfully")
        return {"result": result}
    except Exception as e:
        log.error(f"Error formatting data: {str(e)}")
        return {"error": str(e)}, 400

@app.route("/api/receipts", methods=["GET"])
def get_receipts():
    log = log_service.get_instance()
    log.info("Get receipts endpoint called")
    try:
        if "receipt_model" not in start_service.data:
            log.error("No receipts found")
            return jsonify({"error": "No receipts found"}), 404
        receipts = start_service.data["receipt_model"]
        response_class = factory.create("json")
        response_instance = response_class()
        result = response_instance.build("json", receipts)
        return jsonify({"receipts": result})
    except Exception as e:
        log.error(f"Error getting receipts: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route("/api/receipts/code/<string:unique_code>", methods=["GET"])
def get_receipt_by_code(unique_code: str):
    log = log_service.get_instance()
    log.info(f"Get receipt by code {unique_code}")
    try:
        key = "receipt_model"
        if key not in start_service.data or len(start_service.data[key]) == 0:
            log.error("No receipts available")
            return jsonify({"error": "No receipts available"}), 404
        receipts = start_service.data[key]
        recipe = None
        for r in receipts:
            cur_attr = getattr(r, "unique_code", None)
            if cur_attr == unique_code:
                recipe = r
                break
        if not recipe:
            log.error(f"Receipt with code {unique_code} not found")
            return jsonify({"error": f"Receipt with code {unique_code} not found"}), 404
        response_class = factory.create("json")
        response_instance = response_class()
        result = response_instance.build("json", [recipe])
        return jsonify({"receipt": result})
    except Exception as e:
        log.error(f"Error getting receipt by code: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route("/api/report/osv", methods=["GET"])
def get_osv_report():
    log = log_service.get_instance()
    log.info("Get OSV report endpoint called")
    try:
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")
        warehouse_name = request.args.get("warehouse")
        if not start_date_str or not end_date_str or not warehouse_name:
            log.error("Missing parameters for OSV report")
            return jsonify({"error": "Missing parameters: start_date, end_date, warehouse"}), 400
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
        osv = osv_service(start_service)
        report_objects = osv.generate(start_date, end_date, warehouse_name)
        converter = reference_converter()
        report_serialized = [converter.convert(item) for item in report_objects]
        return jsonify({"report": report_serialized})
    except Exception as e:
        log.error(f"Error generating OSV report: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route("/api/data/save", methods=["POST"])
def save_all_data():
    log = log_service.get_instance()
    log.info("Save all data endpoint called")
    try:
        file_name = getattr(start_service, "file_name", None) or "settings.json"
        data = start_service.data
        converter = reference_converter()
        serialized = {}
        for key, items in data.items():
            serialized[key] = [converter.convert(i) for i in items]
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(serialized, f, ensure_ascii=False, indent=4)
        log.info(f"Data saved to {file_name}")
        return jsonify({"status": "SUCCESS", "file": file_name})
    except Exception as e:
        log.error(f"Error saving data: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route("/api/filter/<string:entity>", methods=["POST"])
def api_filter_entity(entity: str):
    log = log_service.get_instance()
    log.info(f"Filter entity {entity} endpoint called")
    try:
        if entity not in reposity.keys():
            log.error(f"Unknown entity {entity}")
            return jsonify({"error": f"Unknown entity '{entity}'"}), 400
        data_json = request.get_json()
        if not data_json:
            log.error("Empty request body")
            return jsonify({"error": "Empty request body"}), 400
        dto = filter_dto().create(data_json)
        source_items = start_service.data.get(entity, [])
        result = prototype_report.filter(source_items, dto)
        converter = reference_converter()
        converted = [converter.convert(i) for i in result]
        return jsonify({"result": converted})
    except Exception as e:
        log.error(f"Error filtering entity: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route("/api/filter/osv", methods=["POST"])
def api_filter_osv():
    log = log_service.get_instance()
    log.info("Filter OSV endpoint called")
    try:
        data_json = request.get_json()
        if not data_json:
            log.error("Empty request body")
            return jsonify({"error": "Empty request body"}), 400
        dto = filter_dto().create(data_json)
        all_transactions = start_service.data.get(reposity.transaction_key(), [])
        filtered_transactions = prototype_report.filter(all_transactions, dto)
        osv = osv_service(start_service)
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2030, 1, 1)
        warehouse_name = data_json.get("warehouse", "Главный склад")
        report = osv.generate(start_date, end_date, warehouse_name,
                              transactions_override=filtered_transactions)
        return jsonify({"report": report})
    except Exception as e:
        log.error(f"Error filtering OSV: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    log = log_service.get_instance()
    log.info("Starting Flask app")
    start_service.start()
    app.run(host="0.0.0.0", port=8080)