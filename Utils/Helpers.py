import os
import subprocess
from datetime import datetime

from .Logger import Logger, LogLevel


def get_pretty_time_spent_string_from_seconds(time_spent: float) -> str:
    days = int(time_spent // (24 * 3600))
    hours = int((time_spent % (24 * 3600)) // 3600)
    minutes = int((time_spent % 3600) // 60)
    seconds = int(time_spent % 60)

    pretty_str = []
    if days > 0:
        pretty_str.append(f"{days} day{'s' if days > 1 else ''}")
    if hours > 0:
        pretty_str.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        pretty_str.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if seconds > 0 or len(pretty_str) == 0:
        pretty_str.append(f"{seconds} second{'s' if seconds > 1 else ''}")

    return ', '.join(pretty_str)


def convert_ns_to_s(ns: int) -> float:
    return float(ns / (1000 * 1000 * 1000))


def convert_s_to_ns(s: float) -> int:
    return int(s * 1000 * 1000 * 1000)


def run_shell_command(command: str, cwd: str | None = None):
    Logger().log_info(f"Running shell command: {command}...", LogLevel.LOW_FREQ)

    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
    except Exception as e:
        Logger().log_error(f"Failed to execute shell command: {command} by error: {e}", LogLevel.LOW_FREQ)


def dump_content_to_file_on_crash(content: str) -> None:
    file_name = f"{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}_{os.getpid()}.dump"

    with open(file_name, "w") as file:
        file.write(content)

def validate_dir(dir_path: str) -> None:
    if not os.path.exists(dir_path):
        raise ValueError(f"Path {dir_path} does not exist")
    if not os.path.isdir(dir_path):
        raise ValueError(f"Path {dir_path} is not a directory")

def validate_file(file_path: str) -> None:
    if not os.path.exists(file_path):
        raise ValueError(f"Path {file_path} does not exist")
    if not os.path.isfile(file_path):
        raise ValueError(f"Path {file_path} is not a file")


def validate_string(obj: any) -> None:
    if not isinstance(obj, str):
        raise ValueError(f"Object {obj} is not a string")


def validate_int(obj: any) -> None:
    if not isinstance(obj, int):
        raise ValueError(f"Object {obj} is not an integer")


def validate_float(obj: any) -> None:
    if not isinstance(obj, float):
        raise ValueError(f"Object {obj} is not a float")


def validate_list_str(obj: any) -> None:
    if not isinstance(obj, list):
        raise ValueError(f"Object {obj} is not a list")
    if not all(isinstance(x, str) for x in obj):
        raise ValueError(f"Object {obj} is not a list of strings")


def validate_dict(obj: any) -> None:
    if not isinstance(obj, dict):
        raise ValueError(f"Object {obj} is not a dictionary")


def validate_dict_str(obj: any) -> None:
    if not isinstance(obj, dict):
        raise ValueError(f"Object {obj} is not a dictionary")
    if not all(isinstance(x, str) for x in obj.keys()):
        raise ValueError(f"Object {obj} is not a dictionary with string keys")


def validate_dict_str_str(obj: any) -> None:
    validate_dict_str(obj)
    if not all(isinstance(x, str) for x in obj.values()):
        raise ValueError(f"Object {obj} is not a dictionary with string values")


def validate_dict_str_int(obj: any) -> None:
    validate_dict_str(obj)

    if not all(isinstance(x, int) for x in obj.values()):
        raise ValueError(f"Object {obj} is not a dictionary with int values")


def validate_dict_str_list_str(obj: any) -> None:
    validate_dict_str(obj)

    if not all(isinstance(x, list) for x in obj.values()):
        raise ValueError(f"Object {obj} is not a dictionary with list values")

    if not all(all(isinstance(y, str) for y in x) for x in obj.values()):
        raise ValueError(f"Object {obj} is not a dictionary with list of strings values")


def validate_string_dict_string_string_dict(obj: any) -> None:
    validate_dict_str(obj)

    for value in obj.values():
        validate_dict_str_str(value)

def ensure_path_exists(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        Logger().log_info(f"Created directory: {path}", LogLevel.LOW_FREQ)
    elif not os.path.isdir(path):
        raise ValueError(f"Path {path} exists but is not a directory")
