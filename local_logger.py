import logging
import sys


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[94m",     # Blue
        logging.INFO: "\033[92m",      # Green
        logging.WARNING: "\033[93m",   # Yellow
        logging.ERROR: "\033[91m",     # Red
        logging.CRITICAL: "\033[95m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


file_handler = logging.FileHandler('app.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(ColorFormatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger(__name__)
