from __future__ import annotations

import typing as t

import hikari

if t.TYPE_CHECKING:
    from dawn.extensions import Extension

from dawn.commands.slash.base import Option, SlashCallable

__all__: t.Tuple[str, ...] = ("SlashSubCommand", "SlashGroup")


class SlashSubCommand(SlashCallable):
    """This class represents a slash sub-command."""

    __slots__: t.Tuple[str, ...] = ("_name", "_description", "_options")

    def __init__(
        self,
        name: str,
        description: str,
        options: t.List[Option],
    ) -> None:
        self._name = name.lower()
        self._description = description
        self._options = options

    def _build_as_option(self) -> hikari.CommandOption:
        return hikari.CommandOption(
            type=hikari.OptionType.SUB_COMMAND,
            name=self._name,
            description=self._description,
            options=self._options,
        )

    @property
    def name(self) -> str:
        """Name of the subcommand."""
        return self._name

    @property
    def description(self) -> str:
        """Description of the subcommand."""
        return self._description

    @property
    def options(self) -> t.List[Option]:
        """Options for the subcommand"""
        return self._options

    def _compare_with(self, option: hikari.CommandOption) -> bool:
        return (
            self.name == option.name
            and self._description == option.description
            and len(self._options) == len(option.options or [])
            and all(
                (option.name, option.description, option.type)
                == (option_c.name, option_c.description, option.type)
                for option, option_c in zip(self.options, option.options or [])
            )
        )


class SlashSubGroup:
    def __init__(self, name: str, description: str) -> None:
        self._name = name.lower()
        self._description = description
        self._subcommands: t.Dict[str, SlashSubCommand] = {}
        self._parent: SlashGroup | None = None

    @property
    def name(self) -> str:
        """Name of the subcommand group"""
        return self._name

    @property
    def subcommands(self) -> t.List[SlashSubCommand]:
        """SubCommands in the group"""
        return list(self._subcommands.values())

    @property
    def description(self) -> str:
        """Description of the sub command group"""
        return self._description

    def get_subcommands(self) -> t.Mapping[str, SlashSubCommand]:
        return self._subcommands

    def subcommand(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        options: t.List[Option] | None = None,
    ) -> t.Callable[[t.Callable[..., t.Any]], SlashSubCommand]:
        """This decorator is used to create slash subcommands.

        Parameters
        ----------

            name: :class:`str`
                Name of the subcommand.
            description: :class:`str`
                Description of the subcommand.
            options: :class:`Option`
                Options for the subcommand.

        """

        def inner(callback: t.Callable) -> SlashSubCommand:
            nonlocal name, description, options
            sub_command = SlashSubCommand(
                name=name or callback.__name__,
                description=description or "No Description Provided",
                options=options or [],
            )
            sub_command.callback = callback  # type: ignore
            self._subcommands[sub_command._name] = sub_command
            return sub_command

        return inner

    def _build_as_option(self) -> hikari.CommandOption:
        return hikari.CommandOption(
            type=hikari.OptionType.SUB_COMMAND_GROUP,
            name=self.name,
            description=self.description,
            options=[command._build_as_option() for command in self.subcommands],
        )


class SlashGroup:
    """Represents a slash command group."""

    __slots__: t.Tuple[str, ...] = (
        "_name",
        "_description",
        "_extension",
        "_guild_ids",
        "_subcommands",
        "_subgroups",
    )

    def __init__(
        self,
        name: str,
        description: str = "No Description Provided",
        *,
        guild_ids: t.Sequence[int] | None = None,
    ) -> None:
        self._name = name.lower()
        self._description = description
        self._extension: Extension | None = None
        self._guild_ids = list(guild_ids) if guild_ids is not None else []
        self._subcommands: t.Dict[str, SlashSubCommand] = {}
        self._subgroups: t.Dict[str, SlashSubGroup] = {}

    @property
    def name(self) -> str:
        """Name of the group."""
        return self._name

    @property
    def description(self) -> str:
        """Description fo the group."""
        return self._description

    @property
    def guild_ids(self) -> t.Sequence[int]:
        """Sequence of guild_ids this group is bound to."""
        return self._guild_ids

    @property
    def subcommands(self) -> t.List[SlashSubCommand]:
        return list(self._subcommands.values())

    def get_subcommands(self) -> t.Mapping[str, SlashSubCommand]:
        return self._subcommands

    @property
    def subgroups(self) -> t.List[SlashSubGroup]:
        return list(self._subgroups.values())

    def get_subgroups(self) -> t.Mapping[str, SlashSubGroup]:
        return self._subgroups

    @property
    def extension(self) -> Extension | None:
        """Extension which is binded with this group"""
        return self._extension

    def subcommand(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        options: t.List[Option] | None = None,
    ) -> t.Callable[[t.Callable[..., t.Any]], SlashSubCommand]:
        """This decorator is used to create slash subcommands.

        Parameters
        ----------

            name: :class:`str`
                Name of the subcommand.
            description: :class:`str`
                Description of the subcommand.
            options: :class:`Option`
                Options for the subcommand.

        """

        def inner(callback: t.Callable) -> SlashSubCommand:
            nonlocal name, description, options
            sub_command = SlashSubCommand(
                name=name or callback.__name__,
                description=description or "No Description Provided",
                options=options or [],
            )
            sub_command.callback = callback  # type: ignore
            self._subcommands[sub_command._name] = sub_command
            return sub_command

        return inner

    def subgroup(
        self,
        *,
        name: str,
        description: str | None = None,
    ) -> SlashSubGroup:

        sub_group = SlashSubGroup(
            name=name,
            description=description or "No Description Provided",
        )
        self._subgroups[name] = sub_group
        return sub_group
