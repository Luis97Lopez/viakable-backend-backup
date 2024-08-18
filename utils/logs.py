import os
import logging
import logging.config


def initialize_logs_service():
    # Creating logs directory
    if not os.path.exists('./logs/'):
        os.makedirs('logs/')


def get_logger(name: str):
    # Setup loggers
    logging.config.fileConfig('./logging.conf', disable_existing_loggers=False)

    logger = logging.getLogger(name)
    return logger
