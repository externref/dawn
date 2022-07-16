from __future__ import annotations

import importlib
import logging
import typing as t

import hikari

from dawn.context import SlashContext
from dawn.errors import (
    BotNotInitialised,
    CommandAlreadyExists,
    ModuleAlreadyLoaded,
    ModuleNotLoaded,
)
from dawn.extensions import Extension
from dawn.slash import SlashCommand

__all__: t.Tuple[str, ...] = ("Bot",)

_LOGGER = logging.getLogger("dawn.bot")


class Bot(hikari.GatewayBot):
    """The handler's Bot class.
    This is a subclass of :class:`hikari.GatewayBot` with all the features of
    the parent class supported.

    Parameters
    ----------

        token: :class:`str`
            The bot token for your application.
        default_guilds: :class:`Optional[int]`
            Default guilds in which the commands will be added.
        purge_extra: :class:`bool`
            Commands not bound with this class get deleted if set to `True`.

    """

    def __init__(
        self,
        token: str,
        *,
        default_guilds: t.Sequence[int] | None = None,
        purge_extra: bool = False,
        banner: str | None = "dawn",
        **options,
    ) -> None:
        self._slash_commands: t.Dict[str, SlashCommand] = {}
        self._purge_extra = purge_extra
        self._loaded_modules: t.List[str] = []
        self._extensions: t.Dict[str, Extension] = {}
        self.default_guilds = default_guilds
        super().__init__(token, banner=banner, **options)
        self.event_manager.subscribe(
            hikari.InteractionCreateEvent, self.process_slash_commands
        )
        self.event_manager.subscribe(hikari.StartedEvent, self._update_slash_commands)

    @property
    def slash_commands(self) -> t.Mapping[str, SlashCommand]:
        """Mapping for slash command names to :class:`SlashCommadn` objects."""
        return self._slash_commands

    @property
    def extensions(self) -> t.Mapping[str, Extension]:
        """List of all extensions."""
        return self._extensions

    def add_slash_command(self, command: SlashCommand) -> None:

        if self._slash_commands.get(name := command.name):
            raise CommandAlreadyExists(name)
        self._slash_commands[name] = command

    def get_slash_context(self, event: hikari.InteractionCreateEvent) -> SlashContext:
        return SlashContext(self, event)

    def get_slash_command(self, name: str, /) -> SlashCommand | None:
        """Gets a :class:`.SlashCommand` by its name.

        Parameters
        ----------

            name: :class:`str`
                Name of the command.

        """
        return self._slash_commands.get(name)

    def get_extension(self, name: str, /) -> Extension | None:
        """Get a loaded extension object using it's name.

        Parameters
        ----------

            name: :class:`str`
                Name of the extension.

        """
        return self._extensions.get(name)

    async def process_slash_commands(
        self, event: hikari.InteractionCreateEvent, /
    ) -> None:
        """Filters and processes the slash command interactions.

        Parameters
        ----------

            event: :class:`hikari.InteractionCreateEvent`
                The event related to this call.

        """
        if isinstance(inter := event.interaction, hikari.CommandInteraction):
            if command := self._slash_commands.get(inter.command_name):
                await self.invoke_slash_command(event, command)

    async def invoke_slash_command(
        self, event: hikari.InteractionCreateEvent, command: SlashCommand
    ) -> None:
        """Executes a processed :class:`.SlashCommand`.

        Parameters
        ----------

            event: :class:`hikari.InteractionCreateEvent`
                The event related to this call.
            command: :class:`.SlashCommand`
                The slash command to process.

        """
        args: t.List[t.Any] = []
        if not isinstance(inter := event.interaction, hikari.CommandInteraction):
            return
        for opt in inter.options or []:
            if opt.type == hikari.OptionType.CHANNEL and isinstance(opt.value, int):
                args.append(self.cache.get_guild_channel(opt.value))
            elif opt.type == hikari.OptionType.USER and isinstance(opt.value, int):
                if (g_id := inter.guild_id) is None:
                    args.append(None)
                else:
                    args.append(
                        self.cache.get_member(g_id, opt.value)
                        or await self.rest.fetch_member(g_id, opt.value)
                    )
            elif opt.type == hikari.OptionType.ROLE and isinstance(opt.value, int):
                if not inter.guild_id:
                    args.append(None)
                else:
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
        await command(self.get_slash_context(event), *args)

    async def _update_slash_commands(self, event: hikari.StartedEvent) -> None:

        if not (b_user := self.get_me()):
            raise BotNotInitialised()
        if self._purge_extra is True:
            _LOGGER.debug(
                (
                    "Deleting unbound commands, this might take some time.\n"
                    "Set `purge_extra` option in Bot if you don't want this to happen every time."
                )
            )
            all_commands = await self.rest.fetch_application_commands(b_user.id)
            for registerd_command in all_commands:
                if (
                    not self._slash_commands.get(registerd_command.name)
                ) and registerd_command.type == hikari.CommandType.SLASH:
                    await registerd_command.delete()

        for command in self._slash_commands.values():

            (
                [
                    await self.rest.create_slash_command(
                        b_user.id,
                        command.name,
                        command.description,
                        options=command.options or hikari.UNDEFINED,
                        guild=guild_id,
                    )
                    for guild_id in command.guild_ids
                ]
                if command.guild_ids
                else (
                    await self.rest.create_slash_command(
                        b_user.id,
                        command.name,
                        command.description,
                        options=command.options or hikari.UNDEFINED,
                    )
                    if self.default_guilds is None
                    else [
                        await self.rest.create_slash_command(
                            b_user.id,
                            command.name,
                            command.description,
                            options=command.options or hikari.UNDEFINED,
                            guild=guild_id,
                        )
                        for guild_id in self.default_guilds
                    ]
                )
            )

    def register(self, command: SlashCommand) -> t.Callable[[], SlashCommand]:
        """
        Use this decorator to add a slash command to the bot.

        Returns
        -------

            :class:`t.Callable[[], SlashCommand]`
                A callable slash command.

        Example
        -------

            >>> import dawn
            >>>
            >>> bot = dawn.Bot("TOKEN")
            >>>
            >>> @bot.register
            >>> @dawn.slash_command("ping")
            >>> async def ping(context: dawn.SlashContext) -> None:
            >>>     await context.create_response("pong!")
            >>>
            >>> bot.run()

        """

        def inner() -> SlashCommand:
            nonlocal command
            self.add_slash_command(command)
            return command

        return inner()

    def add_extension(self, extension: Extension, /) -> None:
        """
        Adds an extension to the bot.

        Parameters
        ----------

            extension: :class:`.Extension`
                The extension to be loaded.

        Raises
        ------

            :class:`ValueError`
                The extension provided wasn't dervied from :class:`.Extension` class.

        """
        if not isinstance(extension, Extension):
            raise ValueError(f"Expected a `dawn.Extension`, got {type(extension)}")
        extension.create_setup(self)

    def load_module(self, module_path: str, /) -> None:
        """
        Loads a module and calls the `load` function of the module.

        Parameters
        ----------

            module_path: :class:`str`
                Path to the module.

        """
        if module_path in self._loaded_modules:
            raise ModuleAlreadyLoaded(module_path)
        ext = importlib.import_module(module_path)
        if not (load_function := getattr(ext, "load")):
            raise Exception("No load function found.")
        else:
            load_function(self)
            self._loaded_modules.append(module_path)
