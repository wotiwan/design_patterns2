import connexion
from Src.Logics.factory_entities import factory_entities
from Src.settings_manager import settings_manager
from Src.Core.response_format import response_formats
from flask import Flask, request, jsonify
from Src.reposity import reposity
from Src.start_service import start_service

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


# Получить конкретный рецепт по коду
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)