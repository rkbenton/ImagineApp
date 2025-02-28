import json
import logging
import os
import threading
from typing import Dict, Any, List

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


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

        self.theme_data = None
        self.all_theme_display_names: List[str] = []
        self.disk_name_to_theme = {}
        self.display_name_to_theme = {}

        self.config_error = None  # No errors
        load_dotenv()

        # Required environment variables
        try:
            self.im_im_path = os.environ['IM_IM_PATH']
            self.config_path = os.path.join(self.im_im_path, os.environ["IM_IM_CONFIG_FILE_NAME"])
            self.themes_path = os.path.join(self.im_im_path, os.environ["IM_IM_THEMES_DIR_NAME"])
        except KeyError as e:
            self.config_error = f"Missing required environment variable(s): {e}"
            logger.error(self.config_error)
            self.config_data = {}
            return

        self._fetch_data()

        self._initialized = True

    def _fetch_data(self):
        """Read config and theme data from disk."""
        logger.info(f"Loading config from {self.config_path}")

        self.theme_data = None
        self.all_theme_display_names: List[str] = []
        self.disk_name_to_theme = {}
        self.display_name_to_theme = {}

        try:
            self.config_data = self._load_configuration()
            print(f"Configuration loaded from {self.config_path}:\n{json.dumps(self.config_data, indent=2)}")
            self.theme_data = self._load_theme_data()
        except Exception as e:
            self.config_error = f"Error loading configuration: {e}"

    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration JSON file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        try:
            with open(self.config_path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON format in {self.config_path}: {e}"
            print(msg)
            raise ValueError(msg)

    def get_config(self) -> Dict[str, Any]:
        """Return the current configuration, along with any startup errors."""
        return self.config_data

    def save_configuration(self) -> bool:
        """Save the current config data to file."""
        try:
            with self._lock, open(self.config_path, "w") as file:
                json.dump(self.config_data, file, indent=4)  # type: ignore
            return True
        except OSError as e:
            print(f"Error saving config: {e}")
            return False

    def get_config_error(self) -> str:
        """Return any configuration error message."""
        return self.config_error

    def _load_theme_data(self) -> Dict[str, Dict[str, str]]:
        """Load themes from YAML files and return a dictionary indexed by display_name."""
        # key is display_name, data is dict of disk_name and styles list
        themes = {}

        if not os.path.exists(self.themes_path):
            print(f"Themes directory not found: {self.themes_path}")
            return themes

        for filename in os.listdir(self.themes_path):
            if filename.endswith(".yaml"):
                try:
                    with open(os.path.join(self.themes_path, filename), "r") as file:
                        theme_data = yaml.safe_load(file)
                        self.all_theme_display_names.append(theme_data["display_name"])
                        self.disk_name_to_theme[filename] = theme_data
                        self.display_name_to_theme[theme_data["display_name"]] = theme_data
                        themes[theme_data["display_name"]] = {
                            "disk_name": filename,  # Store the actual file name for updates
                            "styles": theme_data.get("styles", {})
                        }
                except yaml.YAMLError as e:
                    print(f"Error loading theme {filename}: {e}")
        self.all_theme_display_names.sort()
        return themes

    def get_themes(self) -> Dict[str, Dict[str, str]]:
        """Return the available themes (display_name mapped to metadata)."""
        return self.theme_data

    def get_theme_by_disk_name(self, disk_name: str):
        return self.disk_name_to_theme[disk_name]

    def get_style_names_by_display_name(self, display_name: str) -> List[str]:
        """Return a list of style names associated with the given display_name."""
        theme_data = self.display_name_to_theme[display_name]
        if theme_data:
            return list(theme_data["styles"].keys())
        else:
            return ["no styles found!"]
