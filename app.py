import os
import json
import logging
from flask import Flask, render_template, request, jsonify
from DataManager import DataManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
data_manager = DataManager()

@app.route("/")
def index():
    cfg_err=data_manager.get_config_error()
    return render_template("index.html", config=data_manager.get_config(), config_error=cfg_err)

@app.route("/update_config", methods=["POST"])
def update_config():
    if data_manager.get_config_error():
        return jsonify({"error": data_manager.get_config_error()}), 500

    try:
        data_manager.config_data = request.json
        success = data_manager.save_configuration()

        if not success:
            return jsonify({"error": "Failed to save configuration"}), 500

        return jsonify({"message": "Configuration updated successfully!"})
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500
