from enum import Enum


class Status(Enum):
    UNFINISHED = 0
    VALID_AND_CONTINUABLE = 1
    DONE = 2
    PASS = 3


class CustomInterpreter:
    def __init__(self, status: Status=Status.VALID_AND_CONTINUABLE):
        self.status: Status = status

    def interpret_single_line(self, one_line: str):
        pass

    def get_status(self) -> Status:
        return self.status

    def values(self):
        return None



