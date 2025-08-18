import inspect
import logging
import re
import sys
from pathlib import Path

import yaml
from loguru import logger
from loguru_config import LoguruConfig

CONFIG_PATH = Path(__file__).parent.parent.parent / "logging.yaml"
LOG_FILTER_PATH = Path(__file__).parent.parent.parent / "log_filter.yaml"

UVICORN_LOGGERS = (
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
    "uvicorn.asgi",
    "uvicorn.warning",
    "uvicorn.server",
    "uvicorn.info",
)


def normalize_level(level: str) -> str:
    """Normalize a logging level string to uppercase."""
    return level.upper() if isinstance(level, str) else level


class InterceptHandler(logging.Handler):
    """Redirect std logging to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        msg = record.getMessage()
        if record.name == "uvicorn.access" and msg.startswith("INFO:"):
            msg = msg[5:].lstrip()

        logger.opt(depth=depth, exception=record.exc_info).log(level, msg)


class StreamToLogger:
    """Redirect stdout/stderr to loguru."""

    def __init__(self, level: str = "INFO"):
        self._level = normalize_level(level)

    def write(self, buffer: str):
        for line in buffer.rstrip().splitlines():
            logger.opt(depth=1).log(self._level, line.rstrip())

    def flush(self):
        pass

    def isatty(self):
        return False


def load_sensitive_words(path: str | Path) -> list[str]:
    """Load sensitive words from a YAML file."""
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("sensitive_words", [])
    except Exception:
        return []


def load_noisy_modules(path: str | Path) -> list[str]:
    """Load noisy modules from a YAML file."""
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("noisy_modules", [])
    except Exception:
        return []


def get_logger(env: str | None = None):
    noisy_modules = load_noisy_modules(LOG_FILTER_PATH)
    sensitive_words = load_sensitive_words(LOG_FILTER_PATH)

    def loguru_filter(record):
        if any(record["name"].startswith(mod) for mod in noisy_modules):
            return False
        msg = record["message"]
        for word in sensitive_words:
            msg = re.sub(rf"({word}=)\S+", r"\1<REDACTED>", msg, flags=re.IGNORECASE)
        record["message"] = msg
        return True

    logger.remove()
    logger.add(sys.stderr, filter=loguru_filter)
    LoguruConfig.load(str(CONFIG_PATH))  # <-- re-apply YAML config last

    if env is not None:
        return logger.patch(lambda record: record["extra"].update({"env": env}) or None)
    return logger


def init_logging(env: str | None = None):
    """Initialize logging for the whole app (intercept std logging, redirect stdout/stderr)."""
    log = get_logger(env)
    # Intercept std logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for logger_name in UVICORN_LOGGERS:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = [InterceptHandler()]
        uvicorn_logger.propagate = False
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    # Redirect stdout/stderr to loguru
    sys.stdout = StreamToLogger("INFO")
    sys.stderr = StreamToLogger("ERROR")
    log.debug("🔄 Enhanced YAML-driven logging initialized")


logcst = get_logger()  # Initialize logger globally
