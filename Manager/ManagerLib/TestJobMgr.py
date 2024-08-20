from ...Utils.GlobalObj import GlobalObj


class TestJobMgr(metaclass=GlobalObj):
    def __init__(self, workers: int):
        print(f"workers: {workers}")