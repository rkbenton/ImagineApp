import os
import json
import yaml
import threading
from typing import Dict, Any
from dotenv import load_dotenv
class DataManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern to ensure only one instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DataManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return  # Prevent re-initialization

        self.config_error = None  # No errors
        load_dotenv()

        # Required environment variables
        try:
            self.config_path = os.environ["IM_IM_CONFIG_PATH"]
            self.themes_path = os.environ["IM_IM_THEMES_PATH"]
        except KeyError as e:
            self.config_error = f"Missing required environment variable: {e}"
            self.config_data = {}
            return

        try:
            self.config_data = self._load_configuration()
        except Exception as e:
            self.config_error = f"Error loading configuration: {e}"
            self.config_data = {}

        self.theme_data = self._load_theme_data()
        self._initialized = True

    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration JSON file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        try:
            with open(self.config_path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {self.config_path}: {e}")

    def get_config(self) -> Dict[str, Any]:
        """Return the current configuration, along with any startup errors."""
        return self.config_data

    def save_configuration(self) -> bool:
        """Save the current config data to file."""
        try:
            with self._lock, open(self.config_path, "w") as file:
                json.dump(self.config_data, file, indent=4) # type: ignore
            return True
        except OSError as e:
            print(f"Error saving config: {e}")
            return False

    def get_config_error(self) -> str:
        """Return any configuration error message."""
        return self.config_error

    def _load_theme_data(self) -> Dict[str, str]:
        """Load themes from YAML files."""
        themes = {}
        if not os.path.exists(self.themes_path):
            return themes

        for filename in os.listdir(self.themes_path):
            if filename.endswith(".yaml"):
                try:
                    with open(os.path.join(self.themes_path, filename), "r") as file:
                        theme_data = yaml.safe_load(file)
                        themes[filename] = theme_data
                except yaml.YAMLError as e:
                    print(f"Error loading theme {filename}: {e}")
        return themes

