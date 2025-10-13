import logging

def logger(**decorator_kwargs):
    def actual_decorator(func):
        def wrapper(*args, **kwargs):
            logging.basicConfig(level=logging.DEBUG, 
                                filename=f'{decorator_kwargs["logfile"]}', filemode='a+',
                                format='%(asctime)s [%(levelname)s]: %(message)s',
                                encoding="utf-8")
            result = func(*args, **kwargs)
            log = logging.getLogger(__name__)
            log.debug("Функция вызвана")
            return result
        return wrapper
    return actual_decorator