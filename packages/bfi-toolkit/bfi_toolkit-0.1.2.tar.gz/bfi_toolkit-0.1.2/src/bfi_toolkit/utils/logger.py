import logging

def get_logger(name: str = "bfi_toolkit", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler()
        f = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        h.setFormatter(f)
        logger.addHandler(h)
    logger.setLevel(level)
    return logger

