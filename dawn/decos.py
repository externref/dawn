import typing as t

from dawn.slash import ArgumentOption, SlashCommand

if t.TYPE_CHECKING:
    from dawn.slash import ArgumentOption
__all__: t.Tuple[str, ...] = ("slash_command",)


def slash_command(
    name: str | None = None,
    description: str | None = None,
    *,
    options: t.Sequence[ArgumentOption] | None = None,
    guild_ids: t.Sequence[int] | None = None,
) -> t.Callable[[t.Callable], SlashCommand]:
    def inner(callback: t.Callable):
        nonlocal name, description, guild_ids

        slash_command = SlashCommand(
            name or callback.__name__,
            description or "No description provided",
            guild_ids,
            options=tuple(options or []),
        )

        slash_command.callback = callback  # type: ignore

        return slash_command

    return inner
