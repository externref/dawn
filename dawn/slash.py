import typing as t

import hikari

if t.TYPE_CHECKING:
    from dawn.context import SlashContext

__all__: t.Tuple[str, ...] = ("SlashCommand",)


class SlashCommand:

    name: str
    description: str
    guild_ids: t.Sequence[int]
    options: list[hikari.CommandOption]

    def __init__(
        self, name: str, description: str, guild_ids: t.Sequence | None = None
    ) -> None:
        self.name = name
        self.description = description
        self.guild_ids = guild_ids or []
        self.options = []

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        return self.callback(*args, **kwargs)

    async def callback(self, context: "SlashContext") -> t.Any:
        ...
