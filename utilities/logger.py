import logging
import sys
from datetime import datetime


def setup_logger():
    logger = logging.getLogger('pizzeria_test')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(levelname)s][%(asctime)s][%(name)s] %(message)s')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    log_filename = f"logs/test_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    import os
    os.makedirs('logs', exist_ok=True)

    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
