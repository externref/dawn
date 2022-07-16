import typing as t

import hikari

if t.TYPE_CHECKING:
    from dawn.bot import Bot
    from dawn.slash import SlashCommand

from dawn.errors import BotNotInitialised, CommandAlreadyExists


class Extension:
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_guilds: t.Sequence[int] | None = None,
    ) -> None:
        self._name = name
        self._description = description
        self._default_guilds = default_guilds
        self._loaded: bool = False
        self._slash_commands: t.Dict[str, "SlashCommand"] = {}
        self._listeners: t.Dict[t.Any, t.List[t.Callable]] = {}

    @property
    def bot(self) -> "Bot":
        if self._loaded is False:
            raise BotNotInitialised()
        return self._bot

    @property
    def slash_commands(self) -> t.Mapping[str, "SlashCommand"]:
        return self._slash_commands

    @property
    def listeners(self) -> t.Mapping[t.Any, t.List[t.Callable]]:
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
            command.extension = self
            if command.guild_ids is None and self._default_guilds is not None:
                command._guild_ids = self._default_guilds
            bot.add_slash_command(command)
        for event, listeners in self._listeners.items():
            for listener in listeners:
                bot.event_manager.subscribe(event, listener)
        self._loaded = True
        self._bot = bot
        return self

    def register(self, command: "SlashCommand") -> "SlashCommand":
        """
        Use this decorator to add a slash command to the bot
        in an extension.

        Returns
        -------

            :class:`t.Callable[[], "SlashCommand"]`
                A callable slash command.

        Example
        -------
        """

        def inner() -> "SlashCommand":
            nonlocal command
            if self._slash_commands.get(name := command.name):
                raise CommandAlreadyExists(name)
            self._slash_commands[name] = command
            return command

        return inner()

    def listen_for(
        self, event: hikari.Event
    ) -> t.Callable[[t.Callable[..., t.Any]], None]:
        """
        Add a listener from the extension.

        Parameters
        ----------

            event: :class:`hikari.Event`
                The event to listen for.

        """

        def inner(callback: t.Callable) -> None:
            nonlocal event
            if not (lsnr := self._listeners.get(event)):
                self._listeners[event] = [callback]
            else:
                lsnr.append(callback)

        return inner
