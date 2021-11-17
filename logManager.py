from datetime import datetime
from enum import Enum

log_file_path = "./log.txt"

_print_func=print

class Level(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


def set_print_func(func):
    global _print_func
    _print_func = func

last_log=False
__file_view_level:Level = Level.INFO
__print_view_level:Level = Level.INFO


def set_file_level(level: Level):
    global __file_view_level
    __file_view_level = level


def set_stdout_level(level: Level):
    global __print_view_level
    __print_view_level = level


def __file_write(header_level: Level, message: str):
    if __file_view_level.value <= header_level.value:
        to_write = f'{datetime.now().strftime("%y%m%d %H%M%S %f")} [{header_level.name}] {message}\n'
        with open(log_file_path, "a") as f:
            f.write(to_write)


def __print(header_level: Level, message: str):
    global last_log
    if __print_view_level.value <= header_level.value:
        to_write = f'[{header_level.name}] {message}'
        if not last_log:
            _print_func("\n" + to_write)
            last_log = True
        else:
            _print_func(to_write)


def pass_to_log(header_level: Level, message: str):
    __file_write(header_level, message)
    __print(header_level, message)


def debug(message: str):
    pass_to_log(Level.DEBUG, message)


def info(message: str):
    pass_to_log(Level.INFO, message)


def warning(message: str):
    pass_to_log(Level.WARNING, message)


def error(message: str):
    pass_to_log(Level.ERROR, message)


def critical(message: str):
    pass_to_log(Level.CRITICAL, message)


def lprint(message: str):
    global last_log
    if last_log:
        last_log = False
    _print_func(message, end='')


if __name__ == '__main__':
    debug("hello2")