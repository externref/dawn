from __future__ import annotations

import sys


class DawnException(Exception):
    ...


class AshUwuxception(DawnException):
    def __init__(self) -> None:
        super().__init__("You are UwU")
        sys.exit()
