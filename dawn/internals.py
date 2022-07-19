from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from dawn.bot import Bot

import hikari

from dawn.errors import BotNotInitialised


class CommandManager:
    @staticmethod
    async def _handle_global_groups(bot: Bot) -> None:
        if not (b_user := bot.get_me()):
            raise BotNotInitialised()
        global_command_builders: t.List[hikari.api.SlashCommandBuilder] = []
        if bot._purge_extra is True:
            for group in [
                c
                for c in bot._slash_groups.values()
                if bot._has_guild_binded(c) is False
            ]:
                command_builder = bot.rest.slash_command_builder(
                    group.name, group.description
                )
                [
                    command_builder.add_option(sub._build_as_option())
                    for sub in group.subcommands
                ]
                global_command_builders.append(command_builder)
            bot._LOGGER.info(
                f"Bulk over-writing {len(global_command_builders)} global groups."
            )
            await bot.rest.set_application_commands(b_user.id, global_command_builders)
            return
        bot._LOGGER.info(f"Processing {len(global_command_builders)} global groups.")
        all_commands = [
            command
            for command in await bot.rest.fetch_application_commands(b_user.id)
            if isinstance(command, hikari.SlashCommand)
            and command.options is not None
            and command.options[0].type == hikari.OptionType.SUB_COMMAND
        ]
        command_names = [c.name for c in all_commands]
        for group in bot._slash_groups.values():
            if not (index := command_names.index(group.name)):
                builder = bot.rest.slash_command_builder(group.name, group.description)
                [
                    builder.add_option(subcmd._build_as_option())
                    for subcmd in group.subcommands
                ]
                await builder.create(bot.rest, b_user.id)
            else:
                g_command = all_commands[index]
                if all(
                    [
                        g_command.name == group.name,
                        g_command.description == group.description,
                        len(g_command.options or []) == len(group.subcommands),
                        all(
                            [
                                subcmd._compare_with(option)
                                for subcmd, option in zip(
                                    group.subcommands, g_command.options or []
                                )
                            ]
                        ),
                    ]
                ):
                    continue
                builder = bot.rest.slash_command_builder(group.name, group.description)
                [
                    builder.add_option(subcmd._build_as_option())
                    for subcmd in group.subcommands
                ]
                await builder.create(bot.rest, b_user.id)

    @staticmethod
    async def _handle_guild_groups(bot: Bot) -> None:
        if not (b_user := bot.get_me()):
            raise BotNotInitialised()
        for group in [
            c for c in bot._slash_groups.values() if bot._has_guild_binded(c) is True
        ]:
            command_builder = bot.rest.slash_command_builder(
                group.name, group.description
            )
            [
                command_builder.add_option(subcmd._build_as_option())
                for subcmd in group.subcommands
            ]
            for guild in (
                group.guild_ids
                or (group.extension.default_guilds if group.extension else [])
                or bot.default_guilds
                or []
            ):
                await command_builder.create(bot.rest, b_user.id, guild=guild)

    @staticmethod
    async def _handle_global_command(bot: Bot) -> None:
        if not (b_user := bot.get_me()):
            raise BotNotInitialised()
        global_command_builders: t.List[hikari.api.SlashCommandBuilder] = []

        if bot._purge_extra is True:
            for command in [
                c
                for c in bot._slash_commands.values()
                if bot._has_guild_binded(c) is False
            ]:
                command_builder = bot.rest.slash_command_builder(
                    command.name, command.description
                )
                [command_builder.add_option(option) for option in command.options]
                global_command_builders.append(command_builder)

            bot._LOGGER.info(
                f"Bulk over-writing {len(global_command_builders)} global commands."
            )
            await bot.rest.set_application_commands(b_user.id, global_command_builders)

            return
        all_commands = [
            command
            for command in await bot.rest.fetch_application_commands(b_user.id)
            if isinstance(command, hikari.SlashCommand)
        ]
        command_names = [c.name for c in all_commands]
        bot._LOGGER.info(f"Processing {len(bot._slash_commands)} global commands.")
        for command in bot._slash_commands.values():
            if not (index := command_names.index(command.name)):
                builder = bot.rest.slash_command_builder(
                    command.name, command.description
                )
                [builder.add_option(option) for option in command.options]
                await builder.create(bot.rest, b_user.id)
            else:
                if command._compare_with(all_commands[index]) is True:
                    continue
                builder = bot.rest.slash_command_builder(
                    command.name, command.description
                )
                [builder.add_option(option) for option in command.options]
                await builder.create(bot.rest, b_user.id)

    @staticmethod
    async def _handle_guild_commands(bot: Bot) -> None:
        if not (b_user := bot.get_me()):
            raise BotNotInitialised()
        for command in [
            c for c in bot._slash_commands.values() if bot._has_guild_binded(c) is True
        ]:
            command_builder = bot.rest.slash_command_builder(
                command.name, command.description
            )
            [command_builder.add_option(option) for option in command.options]
            for guild in (
                command.guild_ids
                or (command.extension.default_guilds if command.extension else [])
                or bot.default_guilds
                or []
            ):
                await command_builder.create(bot.rest, b_user.id, guild=guild)
