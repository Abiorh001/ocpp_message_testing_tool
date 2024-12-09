import logging

# ANSI escape codes for colors
RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        # Colorize the entire log message based on the log level
        if record.levelno == logging.INFO:
            record.msg = f"{GREEN}{record.msg}{RESET}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{RED}{record.msg}{RESET}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{YELLOW}{record.msg}{RESET}"
        elif record.levelno == logging.DEBUG:
            record.msg = f"{BLUE}{record.msg}{RESET}"
        return super().format(record)


def setup_logger(name=__name__, level=logging.DEBUG):
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Check if the logger already has handlers
    if not logger.handlers:
        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Create and set a formatter
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)

    return logger
