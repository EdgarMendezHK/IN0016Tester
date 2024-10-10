import logging


def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with the specified name.

    This function creates a logger with the given name, sets its logging level to INFO,
    and attaches a StreamHandler with a specific formatter. If the logger already has handlers,
    it avoids adding dupplicate handlers.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: THe configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)

    # end if

    return logger


# end def
