import dawn
import hikari


bot = dawn.Bot("TOKEN")

group = dawn.SlashGroup("Test", "Group Example Commands")


@group.subcommand()
async def ping(ctx: dawn.SlashContext):
    await ctx.create_response("foo")


@group.subcommand(options=[dawn.Option("text")])
async def echo(ctx: dawn.SlashContext, text: str) -> None:
    await ctx.create_response(text)


# subgroups

sub_group = group.subgroup(name="message")


@sub_group.subcommand(options=[dawn.Option("user", type=hikari.User)])
async def user(ctx: dawn.SlashContext, user: hikari.User) -> None:
    await user.send("Hello!")
    await ctx.create_response("Sent message to user.")


@sub_group.subcommand(
    name="channel",
    options=[
        dawn.Option(
            "channel",
            type=hikari.GuildChannel,
            channel_types=[hikari.ChannelType.GUILD_TEXT],
        )
    ],
)
async def _channel(ctx: dawn.SlashContext, channel: hikari.GuildTextChannel) -> None:
    await channel.send("Hello!")
    await ctx.create_response("Sent message to channel.")


bot.add_slash_group(group)

bot.run()
