from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
CONFIG_PATH = "config.json"

def load_config():
    with open(CONFIG_PATH, "r") as file:
        return json.load(file)

def save_config(data):
    with open(CONFIG_PATH, "w") as file:
        json.dump(data, file, indent=4)

@app.route("/")
def index():
    config = load_config()
    return render_template("index.html", config=config)

@app.route("/update_config", methods=["POST"])
def update_config():
    data = request.json
    save_config(data)
    return jsonify({"message": "Configuration updated successfully!"})

if __name__ == "__main__":
    app.run(debug=True)
