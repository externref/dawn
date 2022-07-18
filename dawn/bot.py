from __future__ import annotations

import concurrent.futures
import importlib
import logging
import typing as t

import hikari

from dawn.context import SlashContext
from dawn.errors import BotNotInitialised, CommandAlreadyExists, ModuleAlreadyLoaded
from dawn.extensions import Extension
from dawn.slash import SlashCommand

__all__: t.Tuple[str, ...] = ("Bot",)

_LOGGER = logging.getLogger("dawn.bot")


class Bot(hikari.GatewayBot):
    """The handler's Bot class.
    This is a subclass of :class:`~hikari.GatewayBot` with all the features of
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

    __slots__: t.Tuple[str, ...] = (
        "_slash_commands",
        "_purge_extra",
        "_loaded_modules",
        "_extensions",
        "default_guilds",
    )

    def __init__(
        self,
        token: str,
        *,
        default_guilds: t.Sequence[int] | None = None,
        purge_extra: bool = False,
        allow_color: bool = True,
        banner: str | None = "dawn",
        executor: concurrent.futures.Executor | None = None,
        force_color: bool = True,
        cache_settings: hikari.impl.CacheSettings | None = None,
        intents: hikari.Intents = hikari.Intents.ALL_UNPRIVILEGED,
        auto_chunk_members: bool = True,
        logs: None | int | str | t.Dict[str, t.Any] = "INFO",
        max_rate_limit: float = 300,
        max_retries: int = 3,
        proxy_settings: hikari.impl.ProxySettings | None = None,
        rest_url: str | None = None,
    ) -> None:
        self._slash_commands: t.Dict[str, SlashCommand] = {}
        self._purge_extra = purge_extra
        self._loaded_modules: t.List[str] = []
        self._extensions: t.Dict[str, Extension] = {}
        self.default_guilds = default_guilds
        super().__init__(
            token,
            allow_color=allow_color,
            banner=banner,
            executor=executor,
            force_color=force_color,
            cache_settings=cache_settings,
            intents=intents,
            auto_chunk_members=auto_chunk_members,
            logs=logs,
            max_rate_limit=max_rate_limit,
            max_retries=max_retries,
            proxy_settings=proxy_settings,
            rest_url=rest_url,
        )
        self.event_manager.subscribe(
            hikari.InteractionCreateEvent, self.process_slash_commands
        )
        self.event_manager.subscribe(hikari.StartedEvent, self._update_slash_commands)

    @property
    def slash_commands(self) -> t.Mapping[str, SlashCommand]:
        """Mapping for slash command names to :class:`SlashCommand` objects."""
        return self._slash_commands

    @property
    def extensions(self) -> t.Mapping[str, Extension]:
        """List of all extensions."""
        return self._extensions

    def add_slash_command(self, command: SlashCommand) -> None:
        """Add a slash command to the bot's bucket.

        Parameters
        ----------

            command: :class:`SlashCommand`
                The slash command to be added to bucket.

        """
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

            event: :class:`~hikari.InteractionCreateEvent`
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
        kwargs: t.Dict[str, t.Any] = {}
        if not isinstance(inter := event.interaction, hikari.CommandInteraction):
            return
        for opt in inter.options or []:
            if opt.type == hikari.OptionType.CHANNEL and isinstance(opt.value, int):
                kwargs[opt.name] = self.cache.get_guild_channel(opt.value)
            elif opt.type == hikari.OptionType.USER and isinstance(opt.value, int):
                if (g_id := inter.guild_id) is None:
                    kwargs[opt.name] = None
                else:
                    kwargs[opt.name] = self.cache.get_member(
                        g_id, opt.value
                    ) or await self.rest.fetch_member(g_id, opt.value)
            elif opt.type == hikari.OptionType.ROLE and isinstance(opt.value, int):
                if not inter.guild_id:
                    kwargs[opt.name] = None
                else:
                    kwargs[opt.name] = self.cache.get_role(opt.value)
            elif opt.type == hikari.OptionType.ATTACHMENT and isinstance(
                opt.value, hikari.Snowflake
            ):
                if (res := inter.resolved) is None:
                    return
                attachment = res.attachments.get(opt.value)
                kwargs[opt.name] = attachment
            else:
                kwargs[opt.name] = opt.value
        await command(self.get_slash_context(event), *kwargs)

    def _has_guild_binded(self, command: SlashCommand) -> bool:
        return (
            True
            if any(
                [
                    command.guild_ids,
                    (command.extension.default_guilds if command.extension else []),
                    self.default_guilds,
                ]
            )
            else False
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

    async def _update_slash_commands(self, event: hikari.StartedEvent) -> None:
        await self._handle_global_command()
        await self._handle_guild_commands()

    async def _handle_global_command(self) -> None:
        if not (b_user := self.get_me()):
            raise BotNotInitialised()
        global_command_builders: t.List[hikari.api.SlashCommandBuilder] = []
        for command in [
            c
            for c in self._slash_commands.values()
            if self._has_guild_binded(c) is False
        ]:

            command_builder = self.rest.slash_command_builder(
                command.name, command.description
            )

            [command_builder.add_option(option) for option in command.options]
            global_command_builders.append(command_builder)

        if self._purge_extra is True:
            _LOGGER.info(
                f"Bulk over-writing {len(global_command_builders)} global commands."
            )
            await self.rest.set_application_commands(b_user.id, global_command_builders)

        else:

            [
                await _command.create(self.rest, b_user.id)
                for _command in global_command_builders
            ]

    async def _handle_guild_commands(self) -> None:
        if not (b_user := self.get_me()):
            raise BotNotInitialised()
        for command in [
            c
            for c in self._slash_commands.values()
            if self._has_guild_binded(c) is True
        ]:
            command_builder = self.rest.slash_command_builder(
                command.name, command.description
            )
            [command_builder.add_option(option) for option in command.options]
            for guild in (
                command.guild_ids
                or (command.extension.default_guilds if command.extension else [])
                or self.default_guilds
                or []
            ):
                await command_builder.create(self.rest, b_user.id, guild=guild)
