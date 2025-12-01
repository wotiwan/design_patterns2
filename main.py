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

app = Flask(__name__)

start_service = start_service()
start_service.start()
factory = factory_entities()

formats = {}

"""
Проверить доступность REST API
"""


@app.route("/api/accessibility", methods=['GET'])
def formats():
    return "SUCCESS"


@app.route("/api/data/<data_type>/<format>", methods=['GET'])
def get_data_formatted(data_type: str, format: str):
    if data_type not in reposity.keys():
        return {"error": "Wrong data_type"}, 400

    if format not in response_formats.get_all_formats():
        return {"error": "Wrong format"}, 400

    try:
        data = start_service.data[data_type]



        # Создаём экземпляр класса ответа
        logic = factory.create(format)()
        result = logic.build(format, data)

        return {"result": result}

    except Exception as e:
        return {"error": str(e)}, 400


# Получить список всех рецептов (JSON)
@app.route("/api/receipts", methods=["GET"])
def get_receipts():
    try:
        # Получаем все рецепты из репозитория или start_service
        if "receipt_model" not in start_service.data:
            return jsonify({"error": "No receipts found"}), 404

        receipts = start_service.data["receipt_model"]

        # Создаём JSON-ответ через фабрику
        response_class = factory.create("json")
        response_instance = response_class()
        result = response_instance.build("json", receipts)

        # Возвращаем уже сериализованный JSON
        return jsonify({"receipts": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Получить конкретный рецепт по уникальному коду
@app.route("/api/receipts/code/<string:unique_code>", methods=["GET"])
def get_receipt_by_code(unique_code: str):
    try:
        key = "receipt_model"  # ключ в start_service.data
        if key not in start_service.data or len(start_service.data[key]) == 0:
            return jsonify({"error": "No receipts available"}), 404

        receipts = start_service.data[key]
        # ищем рецепт по unique_code

        recipe = None
        for r in receipts:
            cur_attr = getattr(r, "unique_code", None)
            # Проверяем, есть ли у объекта атрибут unique_code и совпадает ли он с нужным кодом
            if cur_attr == unique_code:
                recipe = r
                break

        if not recipe:
            return jsonify({"error": f"Receipt with code {unique_code} not found"}), 404

        response_class = factory.create("json")
        response_instance = response_class()
        result = response_instance.build("json", [recipe])

        return jsonify({"receipt": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/report/osv", methods=["GET"])
def get_osv_report():
    try:
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")
        warehouse_name = request.args.get("warehouse")

        if not start_date_str or not end_date_str or not warehouse_name:
            return jsonify({"error": "Missing parameters: start_date, end_date, warehouse"}), 400

        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)

        from Src.Logics.osv_service import osv_service
        osv = osv_service(start_service)

        report_objects = osv.generate(start_date, end_date, warehouse_name)

        converter = reference_converter()
        report_serialized = [converter.convert(item) for item in report_objects]

        return jsonify({"report": report_serialized})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# POST /api/data/save — Сохранить все данные в файл
@app.route("/api/data/save", methods=["POST"])
def save_all_data():
    try:
        file_name = getattr(start_service, "file_name", None) or "settings.json"
        data = start_service.data
        converter = reference_converter()

        serialized = {}
        for key, items in data.items():
            serialized[key] = [converter.convert(i) for i in items]

        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(serialized, f, ensure_ascii=False, indent=4)

        return jsonify({"status": "SUCCESS", "file": file_name})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/filter/<string:entity>", methods=["POST"])
def api_filter_entity(entity: str):
    try:
        # Проверяем, что сущность существует в репозитории
        if entity not in reposity.keys():
            return jsonify({"error": f"Unknown entity '{entity}'"}), 400

        # Получаем входной DTO
        data_json = request.get_json()
        if not data_json:
            return jsonify({"error": "Empty request body"}), 400

        dto = filter_dto().create(data_json)

        # Получаем список элементов
        source_items = start_service.data.get(entity, [])

        # Оборачиваем в прототип
        proto = prototype_report(source_items)

        # Применяем фильтр
        result = prototype_report.filter(source_items, dto)

        # Сериализация результата — JSON
        converter = reference_converter()
        converted = [converter.convert(i) for i in result]

        return jsonify({"result": converted})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/filter/osv", methods=["POST"])
def api_filter_osv():
    try:
        data_json = request.get_json()
        if not data_json:
            return jsonify({"error": "Empty request body"}), 400

        # Создаём DTO фильтра
        dto = filter_dto().create(data_json)

        # Фильтрация транзакций через прототип
        all_transactions = start_service.data.get(reposity.transaction_key(), [])
        proto = prototype_report(all_transactions)
        filtered_transactions = prototype_report.filter(all_transactions, dto)

        # Создаём временный сервис ОСВ
        from Src.Logics.osv_service import osv_service
        osv = osv_service(start_service)

        osv.temp_transactions = filtered_transactions

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2030, 1, 1)
        warehouse_name = data_json.get("warehouse", "Главный склад")

        report = osv.generate(start_date, end_date, warehouse_name,
                              transactions_override=filtered_transactions)

        return jsonify({"report": report})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/settings/block_date", methods=["POST"])
def set_block_date():
    try:
        data = request.get_json()
        if not data or "block_date" not in data:
            return jsonify({"error": "Missing 'block_date' in request body"}), 400

        block_date_str = data["block_date"]

        try:
            block_date = datetime.fromisoformat(block_date_str)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        # Сохраняем дату блокировки в settings_model через start_service
        if not hasattr(start_service, "settings") or start_service.settings is None:
            return jsonify({"error": "Settings not initialized in start_service"}), 500

        start_service.settings.block_date = block_date

        return jsonify({"status": "SUCCESS", "block_date": block_date.isoformat()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings/block_date", methods=["GET"])
def get_block_date():
    try:
        if not hasattr(start_service, "settings") or start_service.settings is None:
            return jsonify({"error": "Settings not initialized in start_service"}), 500

        block_date = getattr(start_service.settings, "block_date", None)

        if block_date is None:
            return jsonify({"block_date": None})
        else:
            return jsonify({"block_date": block_date.isoformat()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/balance", methods=["GET"])
def get_balance_on_date():
    try:
        date_str = request.args.get("date")
        warehouse_name = request.args.get("warehouse")

        if not date_str or not warehouse_name:
            return jsonify({"error": "Missing parameters: date, warehouse"}), 400

        try:
            target_date = datetime.fromisoformat(date_str)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        from Src.Logics.osv_service import osv_service
        osv = osv_service(start_service)

        # Для временного теста используем start_date = 1900-01-01
        balances = osv.generate(datetime(1900, 1, 1), target_date, warehouse_name)

        return jsonify({"date": target_date.isoformat(), "warehouse": warehouse_name, "balances": balances})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
