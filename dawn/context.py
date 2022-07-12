import typing as t

import hikari

if t.TYPE_CHECKING:
    from dawn.bot import Bot
    from dawn.slash import SlashCommand

__all__: t.Tuple[str, ...] = ("SlashContext",)


class SlashContext:

    event: hikari.InteractionCreateEvent
    channel_id: hikari.Snowflake
    guild_id: hikari.Snowflake | None
    user_id: hikari.Snowflake
    user: hikari.User
    member: hikari.InteractionMember | None
    bot: "Bot"

    def __init__(self, bot: "Bot", event: hikari.InteractionCreateEvent) -> None:
        if not isinstance(inter := event.interaction, hikari.CommandInteraction):
            raise Exception(
                f"Wrong interaction passed.\nExcepted `hikari.CommandInteraction`, got {inter}"
            )
        self.event = event
        self.bot = bot
        self._setup(inter)

    def _setup(self, inter: hikari.CommandInteraction) -> None:
        self.inter = inter
        self.channel_id = inter.channel_id
        self.guild_id = inter.guild_id
        self.user = inter.user
        self.user_id = inter.user.id
        self.member = inter.member

    @property
    def author(self) -> hikari.User | hikari.InteractionMember:
        return self.member or self.user

    @property
    def channel(self) -> hikari.GuildChannel | None:
        return (
            self.bot.cache.get_guild_channel(self.channel_id)
            if not self.channel_id == self.user_id
            else None
        )

    @property
    def command(self) -> t.Optional["SlashCommand"]:
        return self.bot.get_command(self.inter.command_name)

    async def send_message(
        self, content: hikari.UndefinedOr = hikari.UNDEFINED, **options
    ) -> None:
        await self.inter.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE, content, **options
        )
