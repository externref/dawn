import dawn

bot = dawn.Bot("TOKEN")


@bot.register
@dawn.slash_command("ping", "sends a pong message")
async def ping(ctx: dawn.SlashContext) -> None:
    await ctx.create_response("Pong!")


bot.run()
