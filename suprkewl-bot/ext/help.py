# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 laggycomputer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import discord
from discord.ext import commands

from .utils import Embedinator


class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    def command_not_found(self, string):
        return f"Command or category `{self.context.prefix}{string}` not found. Try again..."

    def subcommand_not_found(self, command, string):
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return f"Command `{self.context.prefix}{command.qualified_name}` has no subcommand named {string}"
        else:
            return f"Command `{self.context.prefix}{command.qualified_name}` has no subcommands."

    @staticmethod
    def get_command_name(command):
        name = command.name
        if any(command.aliases):
            alist = []
            for alias in command.aliases:
                alist.append("`%s`" % alias)
            name = f"{name}, {', '.join(alist)}"

        name = f"{name} {command.signature}"
        return name

    def create_embed(self):
        embed = discord.Embed(colour=self.context.bot.embed_color)
        embed.set_author(
            name=self.context.bot.user.name,
            icon_url=self.context.bot.user.avatar_url
        )
        embed.set_thumbnail(url=self.context.bot.user.avatar_url)
        embed.set_footer(
            text=f"{self.context.bot.embed_footer} Requested by {self.context.author}",
            icon_url=self.context.author.avatar_url
        )

        return embed

    def create_embedinator(self, **kwargs):
        destination = self.get_destination()
        embedinator = Embedinator(
            self.context.bot,
            destination,
            self.context.author,
            color=self.context.bot.embed_color,
            **kwargs
        )

        embedinator.set_author(
            name=self.context.bot.user.name,
            icon_url=self.context.bot.user.avatar_url
        )
        embedinator.set_thumbnail(url=self.context.bot.user.avatar_url)
        embedinator.base_embed.set_footer(
            text=f"{self.context.bot.embed_footer} Requested by {self.context.author}",
            icon_url=self.context.author.avatar_url
        )

        return embedinator

    async def send_command_help(self, command):
        embed = self.create_embed()
        embed.title = self.get_command_name(command)
        embed.description = command.short_doc or "No description"
        embed.add_field(name="Extended info", value=command.description or "No further info", inline=False)
        embed.set_footer(text=f"Category: {command.cog_name}")

        destination = self.get_destination()
        await destination.send(embed=embed)

    async def send_group_help(self, group):
        embedinator = self.create_embedinator(
            title=self.get_command_name(group),
            description=group.short_doc or "No description",
            max_fields=8
        )

        filtered = await self.filter_commands(group.commands)

        if filtered:
            for command in filtered:
                self.add_command_field(embedinator, command)

        await embedinator.send()
        await embedinator.handle()

    async def send_cog_help(self, cog):
        embedinator = self.create_embedinator(
            title=cog.qualified_name,
            description=cog.description or "No description",
            max_fields=8
        )

        filtered = await self.filter_commands(cog.get_commands())

        if filtered:
            for command in filtered:
                self.add_command_field(embedinator, command)

        await embedinator.send()
        await embedinator.handle()

    async def send_bot_help(self, mapping):
        embedinator = self.create_embedinator(
            title="General help",
            description=self.get_opening_note(),
            max_fields=8
        )

        for cog, cog_commands in mapping.items():
            filtered = await self.filter_commands(cog_commands)

            if filtered:
                for command in filtered:
                    self.add_command_field(embedinator, command)

        await embedinator.send()

        await embedinator.handle()

    def add_command_field(self, embedinator, command):
        name = self.get_command_name(command)
        embedinator.add_field(
            name=name, value=command.short_doc or "No short help provided, see main dialog", inline=False)

    def get_opening_note(self):
        command_name = self.context.invoked_with
        return f"Use `{self.context.prefix}{command_name} <command>` or `{self.context.prefix}{command_name}"\
               " <category>` for more info  on a command or category."


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self
        self.bot.get_command("help").hidden = True

    def cog_unload(self):
        self.bot.help_command = self.original_help_command


def setup(bot):
    bot.add_cog(Help(bot))
