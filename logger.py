import logging


def convert_str_to_logging_level(level_str: str='warning') -> int:
    level_logging = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }
    return level_logging.get(level_str, logging.WARNING)


logger = logging.getLogger('geocoder')
