from .GlobalObj import GlobalObj


class TestTaskMgr(metaclass=GlobalObj):
    def __init__(self, workers: int):
        print(f"workers: {workers}")