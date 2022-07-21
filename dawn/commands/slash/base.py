from __future__ import annotations

import typing as t
import hikari

if t.TYPE_CHECKING:
    from dawn.context.slash import SlashContext

__all__: t.Tuple[str, ...] = ("Option", "SlashCallable")


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
    def __init__(self) -> None:
        self._autocompletes: t.Dict[
            str,
            t.Callable[
                [hikari.AutocompleteInteraction, hikari.AutocompleteInteractionOption],
                t.Awaitable[list[t.Any]],
            ],
        ] = {}

    @property
    def autocompletes(
        self,
    ) -> t.Mapping[
        str,
        t.Callable[
            [hikari.AutocompleteInteraction, hikari.AutocompleteInteractionOption],
            t.Awaitable[list[t.Any]],
        ],
    ]:
        """Mapping of autocomples for this command"""

        return self._autocompletes

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        return self.callback(*args, **kwargs)

    async def callback(
        self, context: "SlashContext", **kwargs: t.Dict[str, t.Any]
    ) -> t.Any:

        ...

    def autocomplete(
        self, option_name: str, /
    ) -> t.Callable[
        [
            t.Callable[
                [hikari.AutocompleteInteraction, hikari.AutocompleteInteractionOption],
                t.Awaitable[list[t.Any]],
            ]
        ],
        None,
    ]:
        def inner(
            callback: t.Callable[
                [hikari.AutocompleteInteraction, hikari.AutocompleteInteractionOption],
                t.Awaitable[list[t.Any]],
            ],
        ) -> None:
            nonlocal option_name
            self._autocompletes[option_name] = callback

        return inner
