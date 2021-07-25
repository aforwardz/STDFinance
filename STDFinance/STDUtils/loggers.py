import logging

logger = logging.getLogger('std_logger')


def log(level="info", *args):
    s = " ".join([str(x) for x in args])
    if level == "info":
        logger.info(s)
    elif level == 'warning':
        logger.warning(s)
    elif level == 'error':
        logger.error(s)


def log_info(*args):
    log(level="info", *args)


def log_warning(*args):
    log(level="warning", *args)


def log_error(*args):
    log(level="error", *args)