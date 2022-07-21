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

bot = dawn.Bot("TOKEN")


@bot.slash
@dawn.slash_command("ping", "sends a pong message")
async def ping(ctx: dawn.SlashContext) -> None:
    await ctx.create_response("Pong!")


bot.run()
```

You can find more examples in the [examples](https://github.com/sarthhh/dawn/tree/main/examples) folder.

Documentation: https://hikari-dawn.readthedocs.io/en/latest/
