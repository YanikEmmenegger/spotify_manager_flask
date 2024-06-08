# app/logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler
import colorlog


def configure_logging(log_file='app'):
    """
    Configure logging for the application.

    Args:
        log_file (str): The name of the log file.
    """
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )

    # Stream handler for console output
    stream_handler = colorlog.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    # File handler for log file output with rotation
    file_handler = RotatingFileHandler(
        f'{log_dir}/{log_file}.log',
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)

    # Suppress noisy loggers
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('supabase').setLevel(logging.ERROR)
    logging.getLogger('httpx').setLevel(logging.ERROR)
