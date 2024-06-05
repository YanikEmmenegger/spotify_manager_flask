import logging
import colorlog


def configure_logging(logFile='app'):
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

    stream_handler = colorlog.StreamHandler()
    stream_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)
    root_logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(f'logs/{logFile}.log')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    supabase_logger = logging.getLogger('supabase')
    supabase_logger.setLevel(logging.ERROR)

    httpx_logger = logging.getLogger('httpx')
    httpx_logger.setLevel(logging.ERROR)
