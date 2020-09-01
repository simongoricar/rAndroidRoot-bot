# Singleton can only be instantiated once, subsequent instances are the same
class Singleton(type):
    """
    Only allows one instantiation. On subsequent __init__ calls, returns the first instance
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
