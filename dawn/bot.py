from __future__ import annotations

import concurrent.futures
import importlib
import logging
import typing as t

import hikari

from dawn.context import SlashContext
from dawn.errors import CommandAlreadyExists, ModuleAlreadyLoaded
from dawn.extensions import Extension
from dawn.internals import CommandManager
from dawn.slash import SlashCommand, SlashGroup

__all__: t.Tuple[str, ...] = ("Bot",)

_LOGGER = logging.getLogger("dawn.bot")


class Bot(hikari.GatewayBot, CommandManager):
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
        "_slash_groups",
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
        self._slash_groups: t.Dict[str, SlashGroup] = {}
        self._purge_extra = purge_extra
        self._loaded_modules: t.List[str] = []
        self._extensions: t.Dict[str, Extension] = {}
        self.default_guilds = default_guilds
        self._LOGGER = _LOGGER
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
        self.event_manager.subscribe(hikari.StartedEvent, self._update_commands)

    @property
    def slash_commands(self) -> t.Mapping[str, SlashCommand]:
        """Mapping for slash command names to :class:`SlashCommand` objects."""
        return self._slash_commands

    @property
    def slash_groups(self) -> t.Mapping[str, SlashGroup]:
        """Mapping for slash group names to :class:`SlashGroup` objects."""
        return self._slash_groups

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

    def add_slash_group(self, group: SlashGroup) -> None:
        """Add a slash command group to bot's bucket.

        Parameters
        ----------

            group: :class:`SlashGroup`
                The group to be added.

        """
        if self._slash_groups.get(name := group.name) or self._slash_commands.get(name):
            raise CommandAlreadyExists(name)
        self._slash_groups[name] = group

    def get_slash_context(self, event: hikari.InteractionCreateEvent) -> SlashContext:
        """Wrap an :class:`~hikari.InteractionCreateEvent` into a  :class:`SlashContext` class."""
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

    def slash(self, command: SlashCommand) -> SlashCommand:
        """
        Use this decorator to add a slash command to the bot.

        Example
        -------

            >>> import dawn
            >>>
            >>> bot = dawn.Bot("TOKEN")
            >>>
            >>> @bot.slash
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
            elif group := self._slash_groups.get(inter.command_name):
                await self.invoke_slash_command(event, group)

    async def invoke_slash_command(
        self, event: hikari.InteractionCreateEvent, command: SlashCommand | SlashGroup
    ) -> None:
        """Executes a processed :class:`.SlashCommand`.

        Parameters
        ----------

            event: :class:`hikari.InteractionCreateEvent`
                The event related to this call.
            command: :class:`.SlashCommand`
                The slash command to process.

        """
        if not isinstance(inter := event.interaction, hikari.CommandInteraction):
            return
        if isinstance(command, SlashCommand):
            kwargs = await self._prepare_kwargs(inter, inter.options or [])
            await command(self.get_slash_context(event), **kwargs)
        elif isinstance(command, SlashGroup):
            if not (
                to_call := command._subcommands.get(
                    (sub := [opt for opt in inter.options or []][0]).name
                )
            ):
                raise Exception("..")
            kwargs = await self._prepare_kwargs(inter, sub.options or [])
            await to_call(self.get_slash_context(event), **kwargs)

    async def _prepare_kwargs(
        self,
        inter: hikari.CommandInteraction,
        options: t.Sequence[hikari.CommandInteractionOption],
    ) -> t.Mapping[str, t.Any]:

        kwargs: t.Dict[str, t.Any] = {}
        for opt in options or []:
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
                    raise Exception("")
                attachment = res.attachments.get(opt.value)
                kwargs[opt.name] = attachment
            else:
                kwargs[opt.name] = opt.value

        return kwargs

    def _has_guild_binded(self, command: SlashCommand | SlashGroup) -> bool:
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

    async def _update_commands(self, event: hikari.StartedEvent) -> None:
        await self._handle_global_command(self)
        await self._handle_global_groups(self)
        await self._handle_guild_commands(self)
        await self._handle_guild_groups(self)
