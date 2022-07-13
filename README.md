# dawn
A command handler for hikari that I made for personal use.

## EXAMPLE USAGE  

```python
import dawn

bot = dawn.Bot("TOKEN")


@bot.include
@dawn.slash_command("ping", "Latency of the bot.")
async def ping(context: dawn.SlashContext) -> None:
    await context.send_message(f"Pong! {round(bot.heartbeat_latency*1000,2)}")


bot.run()
```

## TODO

* Command Options
* Slash Subcommands
* everything...