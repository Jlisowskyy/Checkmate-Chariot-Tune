from threading import Lock


class GlobalObj(type):
    # Dictionary of all instances created
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
            return cls._instances[cls]

    def get_instance(cls):
        return cls._instances[cls]
