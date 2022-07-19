from __future__ import annotations


class DawnException(Exception):
    """All the exceptions raised by library are subclasses of this class."""
    ...


class CommandAlreadyExists(DawnException):
    """Raised when two commands with same name are tried to register."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Command {name} already exists.")


class ModuleAlreadyLoaded(DawnException):
    """Raised when an already loaded module is tried to load again."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Module {path} is already loaded.")


class BotNotInitialised(DawnException):
    """Raised when bot is accessed without initlization."""

    def __init__(self) -> None:
        super().__init__("Bot cannot be accessed yet.")
