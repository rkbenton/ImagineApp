import logging
from typing import List

from flask import Flask, render_template, request, jsonify

from DataManager import DataManager
from flask import send_from_directory
import os

from FileOps import FileOps
import time

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger.info(f'-- Started "{__name__}" --')

app = Flask(__name__)
data_manager = DataManager()
file_ops = FileOps(data_manager)

if __name__ == "__app__":
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')


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

        # merge new_config into config_data; new_config values take precedence
        data_manager.config_data = data_manager.config_data | new_config
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


@app.route("/file-management")
def get_file_management():
    return render_template("file_management.html")


@app.route('/favicon.ico')
def favicon():
    print("Sending images/favicon.ico")
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/total_files', methods=["GET"])
def total_files():
    file_count, total_size, max_num_saved_files = file_ops.count_local_files()
    time.sleep(3.0)
    response = f"""
    <b>File count:</b> {file_count}, <b>Total Size:</b> {total_size}, <b>Max number of saved files:</b> {max_num_saved_files}
"""
    return response