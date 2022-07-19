from __future__ import annotations

import typing as t

import hikari

if t.TYPE_CHECKING:
    from dawn.context import SlashContext
    from dawn.extensions import Extension

__all__: t.Tuple[str, ...] = (
    "Option",
    "SlashCommand",
    "SlashGroup",
    "SlashSubCommand",
    "SlashCallable",
)


class Option(hikari.CommandOption):
    """Option constructor for slash commands.
    This is a subclass of :class:`hikari.CommandOption`

    Parameters
    ----------

        name: :class:`str`
            Name of the option.
        description: :class:`str`
            Description of the option, defaults to `...`
        type: :class:`Any`
            Any of these classes can be used for the following
            option types.

            :class:`hikari.User`: :class:`hikari.OptionType.USER`

            :class:`hikari.Member`: :class:`hikari.OptionType.USER`

            :class:`hikari.Role`: :class:`hikari.OptionType.ROLE`

            :class:`hikari.GuildChannel`: :class:`hikari.OptionType.CHANNEL`

            :class:`hikari.Attachment`: :class:`hikari.OptionType.ATTACHMENT`

            :class:`bool`: :class:`hikari.OptionType.BOOLEAN`

            :class:`int`: :class:`hikari.OptionType.INTEGER`

            :class:`float`: :class:`hikari.OptionType.FLOAT`

            :class:`str`: :class:`hikari.OptionType.STRING`

        required: :class:`bool`
            Weather the argument is a required or optional.

        channel_types: :class:`Optional[Sequence[Union[hikari.ChannelType, int]]`
            The channel types to check if the `type` was `hikari.GuildChannel`

        autocomplete: :class:`bool`
            Is autocomplete enabled for this option?.

    """

    __slots__: t.Tuple[str, ...] = ()
    option_types: dict[t.Any, t.Any] = {
        hikari.User: hikari.OptionType.USER,
        hikari.Member: hikari.OptionType.USER,
        hikari.Role: hikari.OptionType.ROLE,
        hikari.GuildChannel: hikari.OptionType.CHANNEL,
        hikari.Attachment: hikari.OptionType.ATTACHMENT,
        bool: hikari.OptionType.BOOLEAN,
        int: hikari.OptionType.INTEGER,
        float: hikari.OptionType.FLOAT,
        str: hikari.OptionType.STRING,
    }

    def __init__(
        self,
        name: str,
        description: str = "...",
        *,
        type: t.Any = str,
        required: bool = True,
        channel_types: t.Sequence[hikari.ChannelType | int] | None = None,
        autocomplete: bool = False,
    ) -> None:
        option_type = self.option_types.get(type, hikari.OptionType.STRING)
        super().__init__(
            type=option_type,
            name=name,
            description=description,
            is_required=required,
            channel_types=channel_types,
            autocomplete=autocomplete,
        )


class SlashCallable:
    def __call__(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        return self.callback(*args, **kwargs)

    async def callback(
        self, context: "SlashContext", **kwargs: t.Dict[str, t.Any]
    ) -> t.Any:

        ...


class SlashCommand(SlashCallable):

    """
    This object represents a discord slash command.

    Parameters
    ----------

        name: :class:`str`
            Name of the command.

        description: :class:`str`
            Description of the command.

        guild_ids: :class:`Sequence[int]`
            List of guild ids this command is bound to.

        options: :class:`Tuple[Option, ...]`
            A tuple of command options.

    """

    __slots__: t.Tuple[str, ...] = (
        "_extension",
        "_name",
        "_description",
        "_guild_ids",
        "_options",
    )

    def __init__(
        self,
        name: str,
        description: str,
        guild_ids: t.Sequence | None = None,
        options: t.Tuple[Option, ...] = (),
    ) -> None:
        self._extension: Extension | None = None
        self._name = name
        self._description = description
        self._guild_ids = guild_ids or []
        self._options = options

    @property
    def name(self) -> str:
        """Name of the command."""
        return self._name

    @property
    def description(self) -> str:
        """Description fo the command."""
        return self._description

    @property
    def guild_ids(self) -> t.Sequence[int]:
        """Sequence of guild_ids this command is bound to."""
        return self._guild_ids

    @property
    def options(self) -> t.Tuple[Option, ...]:
        """Tuple of command options"""
        return self._options

    @property
    def extension(self) -> Extension | None:
        """Extension which is binded with this command"""
        return self._extension

    def _compare_with(self, command: hikari.SlashCommand) -> bool:
        return (
            self.name == command.name
            and self.description == command.description
            and len(self.options) == len(command.options or [])
            and all(
                (option.name, option.description, option.type)
                == (option_c.name, option_c.description, option.type)
                for option, option_c in zip(self.options, command.options or [])
            )
        )


class SlashSubCommand(SlashCallable):
    """This class represents a slash sub-command."""

    __slots__: t.Tuple[str, ...] = ("_name", "_description", "_options")

    def __init__(
        self,
        name: str,
        description: str,
        options: t.List[Option],
    ) -> None:
        self._name = name
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


class SlashGroup:
    """Represents a slash command group."""

    __slots__: t.Tuple[str, ...] = (
        "_name",
        "_description",
        "_extension",
        "_guild_ids",
        "_subcommands",
    )

    def __init__(
        self,
        name: str,
        description: str = "No Description Provided",
        *,
        guild_ids: t.Sequence[int] | None = None,
    ) -> None:
        self._name = name
        self._description = description
        self._extension: Extension | None = None
        self._guild_ids = list(guild_ids) if guild_ids is not None else []
        self._subcommands: t.Dict[str, SlashSubCommand] = {}

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
