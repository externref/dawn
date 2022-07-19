import dawn

bot = dawn.Bot("TOKEN")

group = dawn.SlashGroup("Test", "Group Example Commands")


@group.subcommand()
async def ping(ctx: dawn.SlashContext):
    await ctx.create_response("foo")


@group.subcommand(options=[dawn.Option("text")])
async def echo(ctx: dawn.SlashContext, text: str) -> None:
    await ctx.create_response(text)


bot.add_slash_group(group)

bot.run()
