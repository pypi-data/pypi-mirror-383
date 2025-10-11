from enum import Enum


class Element(str):
    def __new__(cls, value: str, name: str = None):
        instance = super().__new__(cls, value)
        if name is None:
            instance.name = value
        else:
            instance.name = name

        return instance


class ExitCode(Enum):
    SUCCESS = 0
    DECODING_ERROR = 1
    INVALID_SELECTION = 2
