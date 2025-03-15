import logging
import os
import threading
import time
from typing import List

from flask import Flask, jsonify, render_template_string, Response
from flask import render_template, request
from flask import send_from_directory

import imim_utils
from DummyFileCopyTask import DummyFileCopyTask
from ImImConfigManager import ImImConfigManager
from JobManager import JobManager
from LocalFileUtils import LocalFileUtils
from LongTaskABC import LongTaskABC

# Configure logging
logging.basicConfig(
    filename="logfile.log", encoding='utf-8',
    level=20,  # 20 INFO, 10 DEBUG
    filemode='w',  # 'a' == append, 'w' over-write
    format="%(asctime)s:%(levelname)s:%(message)s"
)
logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

logger.info(f'-- Started "{__name__}" --')

app = Flask(__name__)
job_manager = JobManager()
data_manager = ImImConfigManager()
local_file_utils = LocalFileUtils(data_manager)

if __name__ == "__app__":
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')


def simulate_job():
    global job_progress, job_running, job_failure
    # Simulate progress in 10 steps over 5 seconds (0.5 sec per step)
    for i in range(1, 11):
        time.sleep(0.5)
        job_progress = i * 10  # Increase progress by 10% each step.
    job_running = False


@app.route("/")
def index():
    config = data_manager.get_config()

    # create several datastructures to simplify the presentation layer's job
    try:
        all_theme_display_names = data_manager.all_theme_display_names
        current_theme_disk_name = config["active_theme"]  # will be like "christmas.yaml"
        current_theme = data_manager.get_theme_by_disk_name(current_theme_disk_name)
        current_theme_display_name = current_theme["display_name"]
        current_styles = list(current_theme["styles"].keys())

        return render_template("index.html",
                               config=config,
                               config_error=f"There was a heinous problem",
                               all_theme_names=all_theme_display_names,
                               current_theme_display_name=current_theme_display_name,
                               current_styles=current_styles,
                               )
    except Exception as e:
        logger.error(e)
        return render_template("index.html",
                               config_error=f"There was a heinous problem: {str(e)}",
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
    logger.info("Sending images/favicon.ico")
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/total_files', methods=["GET"])
def total_files():
    file_count, total_size, num_unrated_images, max_num_saved_files = local_file_utils.count_local_files()
    time.sleep(3.0)
    response = f"""
    <b>File count:</b> {file_count}, <b>Total Size:</b> 
{total_size}, <b>Num unrated files:</b> {num_unrated_images}, <b>Max number of saved files:</b> {max_num_saved_files}
"""
    return response


@app.route('/theme_list', methods=["GET"])
def theme_list():
    list_items: list[str] = []
    themes = data_manager.get_themes()

    list_item = render_template("theme_list_item.html", dir_display_name="Totals")
    list_items.append(list_item)
    for dir_display_name in themes.keys():
        list_item = render_template("theme_list_item.html", dir_display_name=dir_display_name)
        list_items.append(list_item)

    delimiter = "\n"
    result_string = delimiter.join(list_items)

    return result_string


@app.route('/directory-info')
def directory_info():
    display_name = request.args.get('dir', 'Unknown Directory')
    if display_name == 'Totals':
        # get image_out data manually
        file_count, total_size, num_unrated_images, max_files = local_file_utils.count_local_files()
        html_content = f"""
                <h5>Overall stats for image_out:</h5>
                <p>
                <ul>
                    <li><b>File count:</b> {file_count}</li>
                    <li><b>Num unrated files:</b> {num_unrated_images}</li>
                    <li><b>Total size:</b> {LocalFileUtils.sizeof_fmt(total_size)}</li>
                    <li><b>Max number of saved files:</b> {max_files}</li>
                <ul>
"""
    else:
        themes = data_manager.get_themes()
        if display_name in themes.keys():
            theme_data = themes[display_name]
            dir_name = theme_data["disk_name"].replace(".yaml", "")
            file_count, total_size, num_unrated_images, _ = local_file_utils.count_local_files(dir_name)
            total_file_size_human_readable = imim_utils.sizeof_fmt(total_size)

            html_content = render_template("file_panel.html",
                                           display_name=display_name,
                                           dir_name=dir_name,
                                           file_count=file_count,
                                           total_file_size_human_readable=total_file_size_human_readable,
                                           num_unrated_images=num_unrated_images)
        else:
            html_content = f"<h5>Directory <i>{display_name}<i> unknown</h5>"

    return html_content


# Endpoint to return the modal HTML
@app.route('/start-job-modal')
def start_job_modal():
    logger.info("top of /start-job-modal")
    modal = render_template("file_copy_modal_dlg.html")
    return modal


@app.route('/start-job', methods=['POST'])
def start_job():
    logger.info("top of /start-job")

    # Create a dummy task and start it.
    task = DummyFileCopyTask(fail=False)
    job_id: str = job_manager.start_task(task)
    # Start the simulated job in a separate thread
    threading.Thread(target=simulate_job).start()

    # Return initial HTML for the progress container with polling enabled.
    return render_template_string("""
    <div id="job-status-container" hx-get="/job-progress?job_id={{job_id}}" hx-trigger="every 600ms" hx-swap="outerHTML">
      <div class="progress mb-3">
        <div id="progress-bar" class="progress-bar" role="progressbar" style="width: 0%;" 
             aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
      </div>
      <div id="job-status">Copying files...</div>
    </div>
    """, job_id=job_id)


@app.route('/job-progress')
def job_progress_endpoint():
    job_id = request.args.get('job_id')
    task: LongTaskABC = job_manager.get_task(job_id)
    if not task:
        logger.warning(f"Job {job_id} not found by job_manager")
        return "Invalid job", 404

    # Out-of-band update for the cancel button to change it to a Done button.
    # HTMX will automatically update the element with id="cancel-btn" on the
    # page with the out‐of‐band content. Only used when we want to change the
    # text of the Cancel button to something else.
    cancel_button_html: str = ''
    cancel_button_html_template: str = """
        <button id="cancel-btn" type="button" class="btn btn-secondary" data-bs-dismiss="modal"
                hx-post="/cancel-job?job_id={job_id}" hx-trigger="click" hx-swap-oob="outerHTML">
          {button_txt}
        </button>
        """
    polling: str = ""
    cur_progress = task.get_progress()
    # Decide what status message to show
    if cur_progress >= 100:
        logger.info("job-progress is 100%")
        status_text = "Job complete!"
        cancel_button_html = cancel_button_html_template.format(button_txt="Done!", job_id=job_id)
    elif task.failed():
        logger.warning("The job failed.")
        reason: Exception = task.get_failure()
        status_text = f"An error occurred! {str(reason)}"
        cancel_button_html = cancel_button_html_template.format(button_txt="Wah!", job_id=job_id)
    elif task.is_canceled():
        status_text = "Job cancelled"
        cancel_button_html = cancel_button_html_template.format(button_txt="Golly!", job_id=job_id)
    else:
        status_text = "Working..."
        polling: str = f'hx-get="/job-progress?job_id={job_id}" hx-trigger="every 600ms" hx-swap="outerHTML"'
        cancel_button_html = cancel_button_html_template.format(button_txt="Cancel", job_id=job_id)
    # Return updated HTML for the progress container.
    return render_template_string(f"""
    <div id="job-status-container" {polling}>
      <div class="progress mb-3">
        <div id="progress-bar" class="progress-bar" role="progressbar" style="width: {cur_progress}%;"
             aria-valuenow="{cur_progress}" aria-valuemin="0" aria-valuemax="100">{cur_progress}%</div>
      </div>
      <div id="job-status">{status_text}</div>
    </div>
    {cancel_button_html}
    """)


# Stub endpoint to simulate cancellation (for now, simply return a modified button)
@app.route('/cancel-job', methods=['POST'])
def cancel_job():
    # Here we would implement the cancellation logic
    # For now, just change the Cancel button to Done
    # new_button = '<button type="button" class="btn btn-primary" data-bs-dismiss="modal">Done</button>'
    # return new_button
    job_running = False
    job_complete = True
    job_progress = 0
    # Insert your cancellation logic here.
    return Response('', status=204)


@app.route('/copy-to-s3', methods=['POST'])
def copy_to_s3():
    # Stub: implement S3 copy logic here
    return "Copy to S3 initiated."


@app.route('/copy-from-s3', methods=['POST'])
def copy_from_s3():
    # Stub: implement S3 copy-from logic here
    return "Copy from S3 initiated."
