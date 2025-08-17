import inspect
import logging
import sys
from pathlib import Path

from loguru import logger
from loguru_config import LoguruConfig

CONFIG_PATH = Path(__file__).parent.parent.parent / "logging.yaml"

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
    """Normalize the logging level string."""
    return level.upper() if isinstance(level, str) else level


class InterceptHandler(logging.Handler):
    """Intercept standard logging and forward to loguru."""

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
        """Flush method does nothing, required for compatibility."""
        pass

    def isatty(self):
        return False


def init_logging(env: str | None = None):
    """Centralized logging setup for the whole app.

    - Load loguru config from YAML
    - Intercept std logging
    - Redirect stdout/stderr
    - Optionally patch `extra` with environment name
    """
    LoguruConfig.load(str(CONFIG_PATH))

    # Intercept Python's std logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Replace handlers for uvicorn loggers
    for logger_name in UVICORN_LOGGERS:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = [InterceptHandler()]
        uvicorn_logger.propagate = False

    # Adjust uvicorn access log level
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    # Redirect stdout/stderr to loguru
    sys.stdout = StreamToLogger("INFO")
    sys.stderr = StreamToLogger("ERROR")

    # Optional patch for env
    global logger
    if env is not None:
        logger = logger.patch(
            lambda record: record["extra"].update({"env": env}) or None
        )

    logger.debug("🔄 Centralized logging initialized")
