import dawn
import hikari

bot = dawn.Bot("TOKEN")


@bot.register
@dawn.slash_command(
    "echo", "Repeat your message", options=[dawn.Option("text", "text to repeat")]
)
async def ping(ctx: dawn.SlashContext, text: str) -> None:
    await ctx.create_response(text)


@bot.register
@dawn.slash_command(
    "avatar_test",
    "check avatar of a user",
    options=[
        dawn.Option("user", "user to get avatar of", type=hikari.Member, required=False)
    ],
)
async def av_command(
    context: dawn.SlashContext, user: hikari.Member | None = None
) -> None:
    await context.create_response((user or context.user).avatar_url)


bot.run()
