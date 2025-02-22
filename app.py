import logging
from typing import List

from flask import Flask, render_template, request, jsonify

from DataManager import DataManager

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger.info('-- Started --')

app = Flask(__name__)
data_manager = DataManager()


@app.route("/")
def index():
    config = data_manager.get_config()

    # create several datastructures to simplify the presentation layer's job
    all_theme_display_names = data_manager.all_theme_display_names
    current_theme_disk_name = config["active_theme"]  # will be like "christmas.yaml"
    current_theme = data_manager.get_theme_by_disk_name(current_theme_disk_name)
    current_theme_display_name = current_theme["display_name"]
    current_styles = list(current_theme["styles"].keys())

    return render_template("index.html",
                           config=config,
                           all_theme_names=all_theme_display_names,
                           current_theme_display_name=current_theme_display_name,
                           current_styles=current_styles,
                           )


@app.route("/update_config", methods=["POST"])
def update_config():
    if data_manager.get_config_error():
        return jsonify({"error": data_manager.get_config_error()}), 500

    try:
        new_config = request.json

        # look up theme filename based on theme_display_name
        theme_display_name = new_config["theme_display_name"]
        new_config["active_theme"] = data_manager.get_themes()[theme_display_name]["disk_name"]
        del new_config['theme_display_name']

        data_manager.config_data = new_config
        success = data_manager.save_configuration()

        if not success:
            return jsonify({"error": "Failed to save configuration"}), 500

        return jsonify({"message": "Configuration updated successfully!"})
    except Exception as e:
        logger.error(f"Failed to update configuration: {e}")
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


@app.route("/get_styles")
def get_styles():
    # get the selected theme display name
    theme_display_name = request.args.get("theme")
    # get the theme's styles based on the display name
    style_names: List[str] = data_manager.get_style_names_by_display_name(theme_display_name)
    return jsonify(style_names)
