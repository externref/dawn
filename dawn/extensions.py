import typing as t

if t.TYPE_CHECKING:
    from dawn.bot import Bot
    from dawn.slash import SlashCommand, SlashGroup

from dawn.errors import BotNotInitialised, CommandAlreadyExists

__all__: t.Tuple[str, ...] = ("Extension",)


class Extension:
    __slots__: t.Tuple[str, ...] = (
        "_name",
        "_description",
        "_default_guilds",
        "_loaded",
        "_slash_commands",
        "_slash_groups",
        "_listeners",
        "_bot",
    )

    def __init__(
        self,
        name: str,
        description: str = "No Description",
        *,
        default_guilds: t.List[int] | None = None,
    ) -> None:
        self._name = name
        self._description = description
        self._default_guilds = default_guilds
        self._loaded: bool = False
        self._slash_groups: t.Dict[str, "SlashGroup"] = {}
        self._slash_commands: t.Dict[str, "SlashCommand"] = {}
        self._listeners: t.Dict[t.Any, t.List[t.Callable]] = {}

    @property
    def bot(self) -> "Bot":
        """:class:`Bot` associated with this extension"""
        if self._loaded is False:
            raise BotNotInitialised()
        return self._bot

    @property
    def default_guilds(self) -> t.List[int] | None:
        """The default guilds for this extension"""
        return self._default_guilds

    @property
    def slash_commands(self) -> t.Mapping[str, "SlashCommand"]:
        """Slash commands in this extension"""
        return self._slash_commands

    @property
    def slash_groups(self) -> t.Mapping[str, "SlashGroup"]:
        """Slash groups in this extension"""
        return self._slash_groups

    @property
    def listeners(self) -> t.Mapping[t.Any, t.List[t.Callable]]:
        """Listeners in this extension"""
        return self._listeners

    def create_setup(self, bot: "Bot") -> "Extension":
        """
        Call this method to add the extension to the bot.

        Parameters
        ----------

            bot: :class:`Bot`
                The bot class to add extension to.

        """

        for name, command in self._slash_commands.items():
            command._extension = self
            if command.guild_ids is None and self._default_guilds is not None:
                command._guild_ids = self._default_guilds
            bot.add_slash_command(command)
        for name, group in self._slash_groups.items():
            if group.guild_ids is None and self._default_guilds is not None:
                group._guild_ids = self._default_guilds
            bot.add_slash_group(group)
        for event, listeners in self._listeners.items():
            for listener in listeners:
                bot.event_manager.subscribe(event, listener)
        self._bot = bot
        self._loaded = True

        bot._extensions.update({self._name: self})
        return self

    def register(self, command: "SlashCommand") -> "SlashCommand":
        """
        Use this decorator to add a slash command to the bot
        in an extension.

        Returns
        -------

            :class:`t.Callable[[], "SlashCommand"]`
                A callable slash command.

        """

        def inner() -> "SlashCommand":
            nonlocal command
            if self._slash_commands.get(name := command.name):
                raise CommandAlreadyExists(name)
            self._slash_commands[name] = command
            return command

        return inner()

    def listen_for(self, event: t.Any) -> t.Callable[[t.Callable[..., t.Any]], None]:
        """
        Add a listener from the extension.

        Parameters
        ----------

            event: :class:`~hikari.Event`
                The event to listen for.

        """

        def inner(callback: t.Callable) -> None:
            nonlocal event
            if not (lsnr := self._listeners.get(event)):
                self._listeners[event] = [callback]
            else:
                lsnr.append(callback)

        return inner

    def add_slash_group(self, group: "SlashGroup") -> None:
        """Add a slash command group to bot's bucket.

        Parameters
        ----------

            group: :class:`SlashGroup`
                The group to be added.

        """
        if self._slash_groups.get(name := group.name) or self._slash_commands.get(name):
            raise CommandAlreadyExists(name)
        group._extension = self
        self._slash_groups[name] = group
