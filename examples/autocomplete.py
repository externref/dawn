import dawn 
import hikari  

bot = dawn.Bot("TOKEN")

@bot.slash
@dawn.slash_command(options=[dawn.Option("color", autocomplete=True)])
async def colors(ctx: dawn.Context, color: str) -> None:
    await ctx.create_response(f"{ctx.author} chose {color}")

@colors.autocomplete("color")
async def ac_color(inter: hikari.AutocompleteInteraction, option: hikari.AutocompleteInteractionOption) -> hikari.CommandChoice:
    return [
        
    ]
