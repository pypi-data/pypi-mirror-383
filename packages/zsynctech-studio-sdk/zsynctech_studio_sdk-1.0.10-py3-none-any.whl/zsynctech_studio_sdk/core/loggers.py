from loguru import logger as _base_logger
import sys


def get_logger(name: str = "zsynctech-studio-sdk"):
    """_summary_

    Args:
        name (str, optional): _description_. Defaults to "zsynctech-studio-sdk".

    Returns:
        _type_: _description_
    """
    logger = _base_logger.bind(library=name)
    logger.remove()

    logger.add(
        sys.stdout,
        colorize=True,
        level="DEBUG",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[library]}</cyan> | "
            "<magenta>{module}</magenta>:<yellow>{name}</yellow>:<red>{line}</red> | "
            "<level>{message}</level>"
        ),
    )

    return logger