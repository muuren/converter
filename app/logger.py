import logging

LOG_FORMAT = "%(levelname)s: [%(asctime)s.%(msecs)03d] %(message)s"
LOG_DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
log_formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)


def setup_logger(
    log_level: int = logging.INFO, formatter: logging.Formatter = log_formatter
):
    # set level for root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    logger.addHandler(handler)
    return logger
