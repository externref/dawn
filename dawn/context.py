from __future__ import annotations

import typing as t

import hikari

if t.TYPE_CHECKING:
    from dawn.bot import Bot
    from dawn.slash import SlashCommand

__all__: t.Tuple[str, ...] = ("SlashContext",)


class SlashContext:
    """
    This object wraps the :class:`hikari.InteractionCreateEvent` class for
    more easy to access the class' methods and attributes.

    Parameters
    ----------

        bot: :class:`.Bot`
            The related bot class.
        event: :class:`hikari.InteractionCreateEvent`
            The event to get context for.

    """

    __slots__: t.Tuple[str, ...] = ("_event", "_bot", "_setup", "_defered", "_inter")

    def __init__(self, bot: "Bot", event: hikari.InteractionCreateEvent) -> None:
        if not isinstance(inter := event.interaction, hikari.CommandInteraction):
            raise Exception(
                f"Wrong interaction passed.\nExcepted :class:`hikari.CommandInteraction`, got {inter}"
            )
        self._event = event
        self._bot = bot
        self._setup(inter)
        self._defered: bool = False

    def _setup(self, inter: hikari.CommandInteraction) -> None:
        self._inter = inter

    @property
    def event(self) -> hikari.InteractionCreateEvent:
        """The event this SlashContext was derived from."""
        return self._event

    @property
    def interaction(self) -> hikari.CommandInteraction:
        """The interaction related to this SlashContext."""
        return self._inter

    @property
    def member(self) -> hikari.InteractionMember | None:
        """:class:`hikari.InteractionMember` object of the :class:`hikari.User`
        who invoked the slash command, if applicable."""
        return self._inter.member

    @property
    def user(self) -> hikari.User:
        """:class:`hikari.User` who invoked the slash command."""
        return self._inter.user

    @property
    def author(self) -> hikari.User | hikari.InteractionMember | None:
        """An alias to `SlashContext.member or SlashContext.user`."""
        return self._inter.member or self._inter.user

    @property
    def bot(self) -> "Bot":
        """The :class:`.Bot` object."""
        return self._bot

    @property
    def channel_id(self) -> hikari.Snowflake:
        """ID of the channel where command was invoked."""
        return self._inter.channel_id

    @property
    def user_id(self) -> hikari.Snowflake:
        """ID of command author."""
        return self._inter.user.id

    @property
    def channel(self) -> hikari.GuildChannel | None:
        """The :class:`hikari.GuildChannel` object where the command was invoked."""
        return (
            self.bot.cache.get_guild_channel(self.channel_id)
            if not self.channel_id == self.user_id
            else None
        )

    @property
    def command(self) -> t.Optional["SlashCommand"]:
        """The :class:`SlashCommand` this SlashContext belongs to."""
        return self.bot.get_slash_command(self.interaction.command_name)

    async def defer(self) -> None:
        """Defers the response.
        This is useful if the command process is time taking or the response
        has to be created later.
        """
        await self.interaction.create_initial_response(
            hikari.ResponseType.DEFERRED_MESSAGE_CREATE
        )

    async def get_last_response(self) -> hikari.Message:
        """Get the last response sent for this interaction."""
        return await self.interaction.fetch_initial_response()

    async def create_response(
        self, content: hikari.UndefinedOr = hikari.UNDEFINED, **options
    ) -> None:
        """Create a response for the :class:`SlashCommand` interaction.

        Paramaters are same as :class:`hikari.CommandInteraction.create_initial_response`
        """
        await self.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE, content, **options
        )

    async def edit_response(
        self, content: hikari.UndefinedOr = hikari.UNDEFINED, **options
    ) -> None:
        """Edit the response sent for the :class:`SlashCommand` interaction.

        Paramaters are same as :class:`hikari.CommandInteraction.create_initial_response`
        """
        await self.interaction.edit_initial_response(content, **options)
