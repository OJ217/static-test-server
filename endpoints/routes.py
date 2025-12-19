from flask import Blueprint, jsonify, send_file, request, current_app

from .processor import StaticTestProcessor
from .manager import StaticTestManager
from .validator import validate_meta_payload

import io
import csv

st_api = Blueprint("st_api", __name__)

@st_api.route("/tests", methods=["GET"])
def get_st_list():
    try:
        list = StaticTestManager().get_list()
        return jsonify(list)
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({"error": "Failed to get static test list"}), 500

@st_api.route("/tests/<id>", methods=["GET"])
def get_st_result(id):
    if not id:
        return jsonify({"error": "Invalid static test id"}), 400

    try:
        manager = StaticTestManager()
        result = manager.get_by_id(id)

        if result is None:
            return jsonify({"error": "Static test not found"}), 404

        return jsonify(result)
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({"error": "Failed to get static test"}), 500

@st_api.route("/tests/<id>/export", methods=["GET"])
def export_st_result(id):
    if not id:
        return jsonify({"error": "Invalid static test id"}), 400

    try:
        manager = StaticTestManager()
        zip_buffer = manager.export_by_id(id)

        if zip_buffer is None:
            return jsonify({"error": "Static test not found"}), 404

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="static_test_export.zip",
        )
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({"error": "Failed to get static test"}), 500

@st_api.route("/process", methods=["POST"])
def process_st_result():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "Invalid payload"}), 400

    meta, validation_error = validate_meta_payload(payload)
    if validation_error is not None:
        return jsonify(validation_error), 400

    raw_data = payload.get("raw_data")
    if not isinstance(raw_data, list):
        return jsonify({"error": "Invalid payload: data"}), 400

    load_cell_values = [float(value) for value in raw_data]

    try:
        processor = StaticTestProcessor(
            raw_data=load_cell_values,
            name=meta.get("name"),
            total_mass_loss=meta.get("mass_loss"),
            time_interval=meta.get("time_interval"),
        )
        processor.process()
        result = processor.get_aggregated_result()
        return jsonify(result)
    except Exception as e:
        print(e)
        current_app.logger.error(e)
        return jsonify({"error": "Failed to process static test result"}), 500

@st_api.route("/process/file", methods=["POST"])
def process_st_result_file():
    payload = request.form.to_dict()
    meta, validation_error = validate_meta_payload(payload)
    if validation_error is not None:
        return jsonify(validation_error)

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input_data = csv.reader(stream)
        load_cell_values = [float(row[0]) for row in csv_input_data]

        processor = StaticTestProcessor(
            raw_data=load_cell_values,
            name=meta.get("name"),
            total_mass_loss=meta.get("mass_loss"),
            time_interval=meta.get("time_interval"),
        )
        processor.process()
        result = processor.get_aggregated_result()
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({"error": "Failed to process static test result"}), 500