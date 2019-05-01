# -*- coding: utf-8 -*-

"""
The MIT License (MIT)
Copyright (c) 2018-2019 laggycomputer
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import discord
from discord.ext import commands

from .utils import Embedinator


class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.color = 0xf92f2f

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
        embed = discord.Embed(colour=self.color)
        embed.set_author(
            name=self.context.bot.user.name,
            icon_url=self.context.bot.user.avatar_url
        )
        embed.set_thumbnail(url=self.context.bot.user.avatar_url)
        embed.set_footer(
            text=f"{self.context.bot.description} Requested by {self.context.author}",
            icon_url=self.context.author.avatar_url
        )

        return embed

    def create_embedinator(self, **kwargs):
        destination = self.get_destination()
        embedinator = Embedinator(
            self.context.bot,
            destination,
            self.context.author,
            color=self.color,
            **kwargs
        )

        embedinator.set_author(
            name=self.context.bot.user.name,
            icon_url=self.context.bot.user.avatar_url
        )
        embedinator.set_thumbnail(url=self.context.bot.user.avatar_url)
        embedinator.base_embed.set_footer(
            text=f"{self.context.bot.description} Requested by {self.context.author}",
            icon_url=self.context.author.avatar_url
        )

        return embedinator

    async def send_command_help(self, command):
        embed = self.create_embed()
        embed.title = self.get_command_name(command)
        embed.description = command.short_doc or "No description"
        embed.set_footer(text=f"Category: {command.cog_name}")

        destination = self.get_destination()
        sent = (await destination.send(embed=embed))
        await self.context.bot.register_response(sent, self.context.message)

    async def send_group_help(self, group):
        embedinator = self.create_embedinator(
            title=self.get_command_name(group),
            description=group.short_doc or "No description",
            max_fields=4
        )

        filtered = await self.filter_commands(group.commands)

        if filtered:
            for command in filtered:
                self.add_command_field(embedinator, command)

        sent = (await embedinator.send())
        await self.context.bot.register_response(sent, self.context.message)

        await embedinator.handle()

    async def send_cog_help(self, cog):
        embedinator = self.create_embedinator(
            title=cog.qualified_name,
            description=cog.description or "No description",
            max_fields=4
        )

        filtered = await self.filter_commands(cog.get_commands())

        if filtered:
            for command in filtered:
                self.add_command_field(embedinator, command)

        sent = (await embedinator.send())
        await self.context.bot.register_response(sent, self.context.message)

        await embedinator.handle()

    async def send_bot_help(self, mapping):
        embedinator = self.create_embedinator(
            title="General help",
            description=self.get_opening_note(),
            max_fields=4
        )

        for cog, cog_commands in mapping.items():
            for command in cog_commands:
                self.add_command_field(embedinator, command)

        sent = (await embedinator.send())
        await self.context.bot.register_response(sent, self.context.message)

        await embedinator.handle()

    def add_command_field(self, embedinator, command):
        name = self.get_command_name(command)
        embedinator.add_field(name=name, value=command.short_doc or "\u200b", inline=False)

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
        self.bot.get_command('help').hidden = True

    def cog_unload(self):
        self.bot.help_command = self.original_help_command


def setup(bot):
    bot.add_cog(Help(bot))
