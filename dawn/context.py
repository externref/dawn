from __future__ import annotations

import typing as t

import hikari

if t.TYPE_CHECKING:
    from dawn.bot import Bot
    from dawn.slash import SlashCommand

__all__: t.Tuple[str, ...] = ("SlashContext",)


class SlashContext:
    """
    event: hikari.InteractionCreateEvent
    channel_id: hikari.Snowflake
    guild_id: hikari.Snowflake | None
    user_id: hikari.Snowflake
    user: hikari.User
    member: hikari.InteractionMember | None
    bot: "Bot"
    """

    def __init__(self, bot: "Bot", event: hikari.InteractionCreateEvent) -> None:
        if not isinstance(inter := event.interaction, hikari.CommandInteraction):
            raise Exception(
                f"Wrong interaction passed.\nExcepted `hikari.CommandInteraction`, got {inter}"
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
        """`InteractionMember` object of the `User` who invoked the slash command, if applicable."""
        return self._inter.member

    @property
    def user(self) -> hikari.User:
        """`User` who invoked the slash command."""
        return self._inter.user

    @property
    def author(self) -> hikari.User | hikari.InteractionMember | None:
        """An alias to `SlashContext.member or SlashContext.user`."""
        return self._inter.member or self._inter.user

    @property
    def bot(self) -> "Bot":
        """The `.Bot` object."""
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
        """The `GuildChannel` object where the command was invoked."""
        return (
            self.bot.cache.get_guild_channel(self.channel_id)
            if not self.channel_id == self.user_id
            else None
        )

    @property
    def command(self) -> t.Optional["SlashCommand"]:
        """The command this SlashContext belongs to."""
        return self.bot.get_command(self.interaction.command_name)

    async def defer(self) -> None:
        """Defers the response.
        This is useful if the command process is time taking or the response
        has to be created later.

        Returns
        -------

        """
        await self.interaction.create_initial_response(
            hikari.ResponseType.DEFERRED_MESSAGE_CREATE
        )

    async def create_response(
        self, content: hikari.UndefinedOr = hikari.UNDEFINED, **options
    ) -> None:
        await self.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE, content, **options
        )

    async def edit_response(
        self, content: hikari.UndefinedOr = hikari.UNDEFINED, **options
    ) -> None:
        await self.interaction.edit_initial_response(content, **options)


t.Sequence[hikari.ChannelType | int] | None
