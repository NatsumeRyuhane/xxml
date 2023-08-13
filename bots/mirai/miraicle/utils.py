import logging

def start_log(func):
    def wrapper(*args, **kwargs):
        try:
            logging.info(f"method '{func.__name__}' starts")
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logging.error(f"method '{func.__name__}' raised an error: {e.__class__.__name__}")
            raise e

    return wrapper


def end_log(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            logging.info(f"method '{func.__name__}' has called")
            return result
        except Exception as e:
            logging.error(f"method '{func.__name__}' raised an error: {e.__class__.__name__}")
            raise e

    return wrapper


def color(string, to_color):
    color_code_dict = {'black': 30,
                       'red': 31,
                       'green': 32,
                       'yellow': 33,
                       'blue': 34,
                       'violet': 35,
                       'cyan': 36,
                       'white': 37}
    color_code = color_code_dict.get(to_color, 30)
    return f'\033[0;{color_code}m{string}\033[0m'


class Singleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            logging.warn(f'{cls.__name__} is a singleton class and should not be created more than once')
        return cls.__instances[cls]
