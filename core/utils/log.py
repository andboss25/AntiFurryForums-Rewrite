"""A utility file to log all traffic and actions on the forums"""

import os
import logging

try:
    from core.utils import logging_webhooks
except ModuleNotFoundError:
    import logging_webhooks


class DataLogger():
    """A class containing a logger to log data to."""
    def __init__(self, file_name, webhook_identifier = ''):
        # Declare the logger
        self.file_path = os.path.join("logs", f"{file_name}.log")
        self.logger = logging.getLogger(file_name)
        self.logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler(self.file_path)
        fh.setLevel(logging.INFO)

        ch = logging.StreamHandler()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s'
            + ' - %(levelname)s - %(message)s'
        )

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        def on_log(record):
            if not webhook_identifier:
                return True
            else:
                if record.levelname == "INFO":
                    message =f"`{record.getMessage()}`"
                elif record.levelname == "CRITICAL":
                    message =f"{record.levelname} - `{record.getMessage()}` @here"
                else:
                    message = f"{record.levelname} - `{record.getMessage()}`"
                
                logging_webhooks.available_webhooks[
                    webhook_identifier
                ].log_action(
                    message
                )

            return True

        self.logger.addFilter(on_log)

    def get_logger(self):
        """
        Method to get a logger from the DataLogger class.
        returns a logging.Logger class"""

        return self.logger

# I dont know how to test this
