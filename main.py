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
from Src.reference_service import reference_service
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model

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


reference_map = {
    "nomenclature": nomenclature_model,
    "unit": range_model,
    "group": group_model,
    "warehouse": warehouse_model
}

ref_service = start_service.reference_service


def make_prototype(model_class, json_data):
    """Создаёт прототип из JSON"""
    proto = model_class()
    if "name" in json_data:
        proto.name = json_data["name"]
    return proto


# --------- GET: получить один элемент ---------
@app.route("/api/<string:ref_type>", methods=["GET"])
def get_reference(ref_type):
    try:
        if ref_type not in reference_map:
            return jsonify({"error": "Invalid reference type"}), 400

        model = reference_map[ref_type]

        name = request.args.get("name")
        if not name:
            return jsonify({"error": "Missing ?name="}), 400

        proto = model()
        proto.name = name

        result = ref_service.find(proto)
        if not result:
            return jsonify({"error": "Not found"}), 404

        from Src.Logics.reference_converter import reference_converter
        c = reference_converter()
        return jsonify({"result": c.convert(result[0])})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# --------- PUT: добавление ---------
@app.route("/api/<string:ref_type>", methods=["PUT"])
def add_reference(ref_type):
    try:
        if ref_type not in reference_map:
            return jsonify({"error": "Invalid reference type"}), 400

        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "Empty body"}), 400

        model = reference_map[ref_type]
        item = model()
        item.name = json_data["name"]

        ref_service.add(item)

        from Src.Logics.reference_converter import reference_converter
        c = reference_converter()

        return jsonify({"result": c.convert(item)})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# --------- PATCH: изменение ---------
@app.route("/api/<string:ref_type>", methods=["PATCH"])
def update_reference(ref_type):
    try:
        if ref_type not in reference_map:
            return jsonify({"error": "Invalid reference type"}), 400

        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "Empty body"}), 400

        model = reference_map[ref_type]

        # что ищем
        if "old_name" not in json_data:
            return jsonify({"error": "Missing old_name"}), 400

        proto = model()
        proto.name = json_data["old_name"]

        # на что меняем
        update_fields = {}
        if "name" in json_data:
            update_fields["name"] = json_data["name"]

        updated_count = ref_service.update(proto, update_fields)

        return jsonify({"updated": updated_count})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# --------- DELETE: удаление ---------
@app.route("/api/<string:ref_type>", methods=["DELETE"])
def delete_reference(ref_type):
    try:
        if ref_type not in reference_map:
            return jsonify({"error": "Invalid reference type"}), 400

        name = request.args.get("name")
        if not name:
            return jsonify({"error": "Missing ?name="}), 400

        model = reference_map[ref_type]

        proto = model()
        proto.name = name

        deleted = ref_service.delete(proto)

        return jsonify({"deleted": deleted})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
