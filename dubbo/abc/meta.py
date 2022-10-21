"""Meta classes"""
from threading import Lock

__all__ = ("SingletonMeta",)


class SingletonMeta(type):
    __slots__ = ()

    _instances: dict = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]
