import sys
from abc import ABC, abstractmethod


class OptionError(ABC):
    operation: str = ""

    def __init__(self, option: str):
        if not self.operation:
            raise Exception(
                "Can't instantiate abstract OptionError class, it must be inherited and its attribute `operation` set.")
        self.option = option
        # get module name of function that raised error
        self.module = sys._getframe(1).f_globals['__name__']

    def __str__(self):
        return f"Unknown {self.operation} option '{self.option}'. Use the `{self.module}.get_{self.operation}_options()` functions to find compatible encryption options."


class EncryptionOptionError(OptionError, Exception):
    operation = "encryption"


class SignatureOptionError(OptionError, Exception):
    operation = "signature"
