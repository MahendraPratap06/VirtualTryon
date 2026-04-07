import configparser
import os

# Resolve path relative to this file — works no matter where you run from
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_BASE_DIR, "uiconfigfile.ini")

_config = configparser.ConfigParser()
_config.read(_CONFIG_PATH)


class AppConfig:
    """Single source of truth for all project-wide settings."""

    # ── App ────────────────────────────────────────────────────────────────────
    APP_NAME: str = _config["DEFAULT"]["app_name"]
    APP_VERSION: str = _config["DEFAULT"]["app_version"]

    # ── API ────────────────────────────────────────────────────────────────────
    HF_SPACE: str = _config["API"]["hf_space"]
    MAX_RETRIES: int = int(_config["API"]["max_retries"])
    TIMEOUT_SECONDS: int = int(_config["API"]["timeout_seconds"])

    # ── Image ──────────────────────────────────────────────────────────────────
    MAX_WIDTH: int = int(_config["IMAGE"]["max_width"])
    MAX_HEIGHT: int = int(_config["IMAGE"]["max_height"])
    ALLOWED_EXTENSIONS: list[str] = _config["IMAGE"]["allowed_extensions"].split(",")
    MAX_FILE_SIZE_BYTES: int = int(_config["IMAGE"]["max_file_size_mb"]) * 1024 * 1024

    # ── Server ─────────────────────────────────────────────────────────────────
    HOST: str = _config["SERVER"]["host"]
    PORT: int = int(_config["SERVER"]["port"])
    RELOAD: bool = _config["SERVER"].getboolean("reload")