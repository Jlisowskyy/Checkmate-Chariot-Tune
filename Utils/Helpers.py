import subprocess

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
