"""This file is to handle logging and monitoring functionalities.
A class Logger is defined to log messages to a file with different severity levels.
Args:
    log_file (str): Path to the log file.
    level (int): Logging level (default: logging.INFO).
    time_format (str): Format for timestamps in log messages. Default is '%Y-%m-%d %H:%M:%S'. with current server time."""

import logging
from datetime import datetime

class Logger:
    def __init__(self, log_file: str, level: int = logging.INFO, time_format: str = '%Y-%m-%d %H:%M:%S'):
        self.logger = logging.getLogger('CustomLogger')
        self.logger.setLevel(level)
        self.time_format = time_format

        # Create file handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt=self.time_format)
        fh.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(fh)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)