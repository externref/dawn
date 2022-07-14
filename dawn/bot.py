from __future__ import annotations

import logging
import typing as t

import hikari

from dawn.context import SlashContext
from dawn.slash import SlashCommand

__all__: t.Tuple[str, ...] = ("Bot",)

_LOGGER = logging.getLogger("dawn.bot")


class Bot(hikari.GatewayBot):
    def __init__(self, token: str, *, purge_extra=True, **options) -> None:
        self._slash_commands: t.Dict[str, SlashCommand] = {}
        self._purge_extra = purge_extra
        super().__init__(token, **options)
        self.event_manager.subscribe(
            hikari.InteractionCreateEvent, self.process_slash_commands
        )
        self.event_manager.subscribe(hikari.StartedEvent, self._update_commands)

    def add_slash_command(self, command: SlashCommand) -> None:

        if self._slash_commands.get(name := command.name):
            raise Exception(f"Command named {name} already exists.")
        self._slash_commands[name] = command

    async def process_slash_commands(
        self, event: hikari.InteractionCreateEvent
    ) -> None:
        if isinstance(inter := event.interaction, hikari.CommandInteraction):
            if command := self._slash_commands.get(inter.command_name):
                await self.invoke_slash_command(event, command)

    async def invoke_slash_command(
        self, event: hikari.InteractionCreateEvent, command: SlashCommand
    ) -> None:
        args: t.List[t.Any] = []
        if not isinstance(inter := event.interaction, hikari.CommandInteraction):
            return
        for opt in inter.options or []:
            if opt.type == hikari.OptionType.CHANNEL and isinstance(opt.value, int):
                args.append(self.cache.get_guild_channel(opt.value))
            elif opt.type == hikari.OptionType.USER and isinstance(opt.value, int):
                if g_id := inter.guild_id is None:
                    args.append(None)
                args.append(self.cache.get_member(g_id, opt.value))
            elif opt.type == hikari.OptionType.ROLE and isinstance(opt.value, int):
                if not inter.guild_id:
                    args.append(None)
                args.append(self.cache.get_role(opt.value))
            elif opt.type == hikari.OptionType.ATTACHMENT and isinstance(
                opt.value, hikari.Snowflake
            ):
                if (res := inter.resolved) is None:
                    return
                attachment = res.attachments.get(opt.value)
                args.append(attachment)
            else:
                args.append(opt.value)
        await command(SlashContext(self, event), *args)

    def get_command(self, name: str) -> SlashCommand | None:
        return self._slash_commands.get(name)

    async def _update_commands(self, event: hikari.StartedEvent) -> None:
        if not (b_user := self.get_me()):
            raise Exception("Bot is not initialised yet.")
        for command in self._slash_commands.values():
            if command.guild_ids == []:
                await self.rest.create_slash_command(
                    b_user.id,
                    command.name,
                    command.description,
                    options=command.options or hikari.UNDEFINED,
                )

    def include(self, command: SlashCommand) -> t.Callable[[], SlashCommand]:
        def inner() -> SlashCommand:
            nonlocal command
            self.add_slash_command(command)
            return command

        return inner()
