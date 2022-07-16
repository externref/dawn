import dawn
import hikari

ext = dawn.Extension("extension")


@ext.listen_for(hikari.MessageCreateEvent)
async def event_example(
    event: hikari.MessageCreateEvent,
) -> None:  # NOTE: this does not support annotated event
    print("Message created.")  # mention the event class in the decorator.


@ext.register
@dawn.slash_command()
async def ping(ctx: dawn.SlashContext) -> None:
    await ctx.create_response("pong!")


def load(bot: dawn.Bot) -> None:
    ext.create_setup(bot)
