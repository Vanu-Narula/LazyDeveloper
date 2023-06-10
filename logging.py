import os, sys
import datetime
import logging
import streamlit as st


class Logger:
    def __init__(self, name=__name__):
        self.log_folder = "logs"
        self.log_file = self._get_log_file_name()
        self.logger = self._create_logger(name)

    def _get_log_file_name(self):
        """
        Generate a log file name based on the current datetime.
        """
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        return f"{self.log_folder}/log_{timestamp}.txt"

    def _create_log_folder(self):
        """
        Create the log folder if it doesn't exist.
        """
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)

    def _create_logger(self, name):
        """
        Create a logger instance with handlers to log messages.
        """
        self._create_log_folder()

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def log(self, message, log_type=logging.INFO):
        """
        Log a message with the specified log type.
        """
        self.logger.log(log_type, message)

    def info(self, message):
        """
        Log an info message.
        """
        self.log(message, logging.INFO)

    def warning(self, message):
        """
        Log a warning message.
        """
        self.log(message, logging.WARNING)

    def error(self, message):
        """
        Log an error message.
        """
        self.log(message, logging.ERROR)

    def exception(self, message):
        """
        Log an exception message.
        """
        self.log(message, logging.ERROR)


    def get_logger_name(self):
            """
            Get the name for the logger.
            If running with Streamlit, use the script name as the logger name.
            Otherwise, use the default logger name.
            """
            if "streamlit" in sys.modules:
                return os.path.basename(sys.argv[0])
            else:
                return None
