import logging

logger = logging.getLogger('std_logger')


def log(*args, level="info"):
    s = " ".join([str(x) for x in args])
    if level == "info":
        logger.info(s)
    elif level == 'warning':
        logger.warning(s)
    elif level == 'error':
        logger.error(s)


def log_info(*args):
    log(*args, level="info")


def log_warning(*args):
    log(*args, level="warning")


def log_error(*args):
    log(*args, level="error")
