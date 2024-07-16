import configparser


class Config:
    _instance = None

    def __new__(cls, f="settings.ini"):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_settings(f)
        return cls._instance

    def _load_settings(self, f):
        configur = configparser.ConfigParser()
        configur.read(f)

        self.settings = {}
        try:
            self.settings["code_theme"] = configur.get("settings", "code_theme")
        except configparser.NoSectionError:
            self.settings["code_theme"] = "default"

    def get(self, key, default=None):
        return self.settings.get(key, default)


config = Config()
