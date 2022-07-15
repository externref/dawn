![](https://img.shields.io/github/license/sarthhh/dawn?style=flat-square)
![](https://img.shields.io/pypi/pyversions/hikari?style=flat-square)
![](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)
![](http://www.mypy-lang.org/static/mypy_badge.svg)
![](https://img.shields.io/github/stars/sarthhh/dawn?style=flat-square)
![](https://img.shields.io/github/last-commit/sarthhh/dawn?style=flat-square)

# dawn
A command handler for hikari.

## EXAMPLE USAGE  

```python
import dawn
import hikari

bot = dawn.Bot("TOKEN")


@bot.register
@dawn.slash_command("ping", "Latency of the bot.")
async def ping(context: dawn.SlashContext) -> None:
    await context.create_response(f"Pong! {round(bot.heartbeat_latency*1000,2)}")


# with options


@bot.register
@dawn.slash_command(
    "avatar",
    "Check user's avatar.",
    options=[dawn.Option("user", "Target user.", type=hikari.User)],
)
async def avatar(context: dawn.SlashContext, user: hikari.User) -> None:
    """
    Sending a message and editing the response.
    """
    await context.create_response("Getting user avatar.")
    await context.edit_response(str(user.display_avatar_url))


# guild specific commands


@bot.register
@dawn.slash_command(
    "echo",
    "Repeats your text.",
    options=[dawn.Option("text", "Text to repeat.")],
    guild_ids=(1234567890,),
)
async def echo(context: dawn.SlashContext, text: str) -> None:
    await context.create_response(text)


bot.run()
```