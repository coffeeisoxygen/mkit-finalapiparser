import sys

from app.config import get_settings
from app.mlogg import logger

test_settings = get_settings()


def test_log_print(capsys):
    # Add a temporary sink to stderr so capsys can capture loguru output
    sink_id = logger.add(sys.stderr, format="{message}", level="INFO")
    logger.info("Hello from loguru!")
    out, err = capsys.readouterr()
    logger.remove(sink_id)

    assert "Hello from loguru!" in out or "Hello from loguru!" in err


def test_print_and_loguru(capsys):
    print("Hello from print!")
    sink_id = logger.add(sys.stderr, format="{message}", level="INFO")
    logger.info("Hello from loguru!")
    out, err = capsys.readouterr()
    logger.remove(sink_id)
    assert "Hello from print!" in out or "Hello from print!" in err
    assert "Hello from loguru!" in out or "Hello from loguru!" in err
