from __future__ import annotations

import typing as t

from dawn.slash import Option, SlashCommand

if t.TYPE_CHECKING:
    from dawn.slash import Option

__all__: t.Tuple[str, ...] = ("slash_command",)


def slash_command(
    name: str | None = None,
    description: str | None = None,
    *,
    options: t.Sequence[Option] | None = None,
    guild_ids: t.Sequence[int] | None = None,
) -> t.Callable[[t.Callable], SlashCommand]:
    """This decorator is used to define a slash command.

    Parameters
    ----------

        name: :class:`str`
            Name of the slash command, defaults to the function name
        description: :class:`str`
            Slash command description, "No Description provided" is used in case
            this argument wasn't provided.
        `options`: :class:`Sequence[.Option]`
            List of :class:`.Option` objects for the slash command.
            These represent discord slash command options.
        `guild_ids`: :class:`Sequence[int]`
            List of guild IDs to add the command to.

    """

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
