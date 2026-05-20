import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os

# Cria o caminho para armazenar os logs
log_name = 'C:\\CHAMADOS\\Logs'
os.makedirs(log_name, exist_ok=True)


data_log = datetime.now().strftime("%Y-%m-%d")

log_file = os.path.join(log_name, f"{data_log}.log")

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)