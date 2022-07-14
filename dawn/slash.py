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
        description: str,
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

    name: str
    description: str
    guild_ids: t.Sequence[int]
    options: t.Tuple[Option, ...]

    def __init__(
        self,
        name: str,
        description: str,
        guild_ids: t.Sequence | None = None,
        options: t.Tuple[Option, ...] = (),
    ) -> None:
        self.name = name
        self.description = description
        self.guild_ids = guild_ids or []
        self.options = options

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        return self.callback(*args, **kwargs)

    def _set_options(self) -> None:
        ...

    async def callback(
        self, context: "SlashContext", *args: t.Tuple[Option | str, ...]
    ) -> t.Any:
        ...
