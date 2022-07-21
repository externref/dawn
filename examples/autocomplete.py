import hikari

import dawn

bot = dawn.Bot("TOKEN")


@bot.slash
@dawn.slash_command(options=[dawn.Option("color", autocomplete=True)])
async def colors(ctx: dawn.SlashContext, color: str) -> None:
    await ctx.create_response(f"{ctx.author} chose {color}")


@colors.autocomplete("color")
async def ac_color(
    inter: hikari.AutocompleteInteraction, option: hikari.AutocompleteInteractionOption
) -> list[hikari.CommandChoice | str]:
    return ["red", hikari.CommandChoice(name="blue", value="blue")]


group = dawn.SlashGroup(name="Test")

bot.add_slash_group(group)


@group.subcommand(options=[dawn.Option("number", type=int, autocomplete=True)])
async def command(ctx: dawn.SlashContext, number: int) -> None:
    await ctx.create_response(number)


@command.autocomplete("number")
async def ac_number(
    inter: hikari.AutocompleteInteraction, opt=hikari.AutocompleteInteractionOption
) -> list[int | hikari.CommandChoice]:
    return [1, 2, 3, 4, hikari.CommandChoice(name="five", value=5)]


bot.run()
