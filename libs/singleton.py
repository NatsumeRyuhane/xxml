import logging

class Singleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            logging.warning(f'{cls.__name__} is a singleton class and should not be created more than once')
        return cls.__instances[cls]