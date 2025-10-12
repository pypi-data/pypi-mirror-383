import os
import yaml

class Config:
    ATHENA_HOME = os.getenv("ATHENA_HOME", os.getcwd())

    def __init__(self, filename: str):
        self.path = os.path.join(Config.ATHENA_HOME, "config", filename)
        self.config: dict[str, Any] = {}
        self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            self.config = {}
        except Exception as e:
            raise RuntimeError(f"Failed to load config file {self.path}") from e

    def get_value(self, key: str, default=None):
        if self.config is None:
            raise RuntimeError("Configuration not loaded.")

        parts = key.split('/')
        val = self.config
        try:
            for part in parts:
                val = val[part]
            return val
        except (KeyError, TypeError):
            return default