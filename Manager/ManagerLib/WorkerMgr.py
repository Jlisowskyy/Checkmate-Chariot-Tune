from .GlobalObj import GlobalObj


class WorkerMgr(metaclass=GlobalObj):
    def __init__(self, workers: int):
        print(f"workers: {workers}")