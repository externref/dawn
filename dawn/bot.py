import typing as t

import hikari

from dawn.slash import SlashCommand
from dawn.context import SlashContext

__all__: t.Tuple[str, ...] = ("Bot",)


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
                await command(SlashContext(self, event))

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
