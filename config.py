import configparser
import os
import platform
import sys
from typing import Optional


class Config:
    _instance = None

    def __new__(cls, f: Optional[str] = None) -> "Config":
        """
        Create a new instance of the Config class if it does not already exist.
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_settings(f)
        return cls._instance

    def _load_settings(self, f: Optional[str]) -> None:
        """
        Load settings from the configuration file. If no configuration file is found,
        initialize a new configuration file with default settings.

        :param f: Optional path to a specific configuration file.
        """
        settings_paths = []
        db_paths = []

        match platform.system():
            case "Linux" | "Darwin":
                settings_paths = [
                    os.path.expanduser("~/.config/sc/settings.ini"),
                    os.path.expanduser("~/.config/sc.ini"),
                    os.path.expanduser("~/.sc.ini"),
                ]
                db_paths = [
                    os.path.expanduser("~/.local/share/sc/notesdb.sqlite3"),
                    os.path.expanduser("~/.local/share/scdb.sqlite3"),
                    os.path.expanduser("~/.scdb.sqlite3"),
                ]
            case "Windows":
                settings_paths = [
                    os.path.expandvars("%APPDATA%\\sc\\settings.ini"),
                    os.path.expandvars("%APPDATA%\\sc.ini"),
                ]
                db_paths = [
                    os.path.expandvars("%APPDATA%\\sc\\notesdb.sqlite3"),
                    os.path.expandvars("%APPDATA%\\scdb.sqlite3"),
                ]
            case _:
                sys.exit(f"Unsupported platform: {platform.system()}")

        if f:
            settings_paths = [f] + settings_paths

        configur = configparser.ConfigParser()
        settings_found = False
        for path in settings_paths:
            if os.path.exists(path):
                configur.read(path)
                settings_found = True
                break

        if not settings_found:
            if not os.path.exists(os.path.dirname(settings_paths[0])):
                os.makedirs(os.path.dirname(settings_paths[0]))
            with open(settings_paths[0], "w") as configfile:
                configur.add_section("settings")
                configur.set("settings", "code_theme", "default")
                configur.set("settings", "db_file", db_paths[0])
                configur.write(configfile)
            configur.read(settings_paths[0])

        self.settings = {}
        self.settings["code_theme"] = configur.get(
            "settings", "code_theme", fallback="default"
        )

        if not configur.has_option("settings", "code_theme"):
            configur.set("settings", "code_theme", "default")
            with open(settings_paths[0], "w") as configfile:
                configur.write(configfile)

        self.settings["db_file"] = configur.get(
            "settings", "db_file", fallback=db_paths[0]
        )

        if not configur.has_option("settings", "db_file"):
            configur.set("settings", "db_file", db_paths[0])
            with open(settings_paths[0], "w") as configfile:
                configur.write(configfile)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a configuration value by key.

        :param key: The key of the configuration value to retrieve.
        :param default: The default value to return if the key is not found.
        :return: The configuration value or the default value if the key is not found.
        """
        return self.settings.get(key, default)


config = Config()
