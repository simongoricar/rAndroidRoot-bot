import uuid
import random
import string


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


def generate_id(length: int = 4):
    return int(str(uuid.uuid4().int)[:length])


CODE_CHARS = string.ascii_uppercase + string.digits


def generate_code(length: int = 4):
    return "".join([random.choice(CODE_CHARS) for _ in range(length)])