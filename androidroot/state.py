from typing import Optional, Any

from .utilities import Singleton


class State(metaclass=Singleton):
    def __init__(self):
        self.state = {}

    def set(self, key: Any, value: Any) -> None:
        self.state[key] = value

    def get(self, key: Any) -> Optional[Any]:
        return self.state.get(key)


state = State()
