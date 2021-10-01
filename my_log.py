import sys
import log.server_log_config
import log.client_log_config
import logging

# метод определения модуля, источника запуска.
if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('app.server')
else:
    logger = logging.getLogger('app.client')


def log(func):
    def callf(*args, **kwargs):
        logger.debug(f"Вызвана функция: {func.__name__} c позиционными аргументами {args} и имнованными аргументами {kwargs} из модуля {func.__module__}")
        r = func(*args, **kwargs)
        return r
    return callf
