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

class DiscordDMHandler(logging.Handler):
    def __init__(self, bot, user_id, enviar_dm_func):
        super().__init__(level=logging.ERROR)
        self.bot = bot
        self.user_id = user_id
        self.enviar_dm = enviar_dm_func

    def emit(self, record):
        try:
            msg = self.format(record)
            coro = self.bot.loop.create_task(self.enviar_dm(self.user_id, msg))
        except Exception as e:
            print(f"[DiscordDMHandler] Falha ao emitir: {e}")

logger = setup_logging()
