import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logging(level=logging.INFO) -> logging.Logger:
    """Configura logging global e devolve o logger principal."""
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"

    handlers = [
        logging.StreamHandler(),                           # console
        RotatingFileHandler(
            LOG_DIR / "bot.log",
            maxBytes=5_000_000,    # ~5 MB
            backupCount=3,         # rota até 3 arquivos
            encoding="utf-8"
        )
    ]

    logging.basicConfig(level=level, format=fmt, handlers=handlers)
    return logging.getLogger("NKBot")

logger = setup_logging()
