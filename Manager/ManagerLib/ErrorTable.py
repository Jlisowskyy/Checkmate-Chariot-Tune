from enum import IntEnum


class ErrorTable(IntEnum):
    SUCCESS = 0
    WORKER_ALREADY_REGISTERED = 1
    UNKNOWN_ERROR = 2
    WORKER_NOT_FOUND = 3
    INVALID_TOKEN = 4
