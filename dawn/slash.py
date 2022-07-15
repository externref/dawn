from __future__ import annotations

import typing as t

import hikari

if t.TYPE_CHECKING:
    from dawn.context import SlashContext

__all__: t.Tuple[str, ...] = (
    "Option",
    "SlashCommand",
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


class SlashCommand:
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

    def __init__(
        self,
        name: str,
        description: str,
        guild_ids: t.Sequence | None = None,
        options: t.Tuple[Option, ...] = (),
    ) -> None:
        self._name = name
        self._description = description
        self._guild_ids = guild_ids or []
        self._options = options

    @property
    def name(self) -> str:
        """Name of the command.

        Returns
        -------

            :class:`str`

        """
        return self._name

    @property
    def description(self) -> str:
        """Description fo the command.

        Returns
        -------

            :class:`str`

        """
        return self._description

    @property
    def guild_ids(self) -> t.Sequence[int]:
        """Sequence of guild_ids this command is bound to.

        Returns
        -------

            :class:`t.Sequence[int]`

        """
        return self._guild_ids

    @property
    def options(self) -> t.Tuple[Option, ...]:
        """Tuple of command options

        Returns
        -------

            :class:`t.Tuple[Option, ...]`

        """
        return self._options

    def _compare_with(self, command: "SlashCommand") -> bool:
        return (
            self.name == command.name
            and self.description == command.description
            and len(self.options) == len(command.options or [])
            and all(
                (option.name, option.description, option.type)
                == (option_c.name, option_c.description, option.type)
                for option, option_c in zip(self.options, command.options or [])
            )
            and True
        )

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        return self.callback(*args, **kwargs)

    def _set_options(self) -> None:
        ...

    async def callback(
        self, context: "SlashContext", *args: t.Tuple[Option | str, ...]
    ) -> t.Any:
        ...
