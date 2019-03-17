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

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Please note that if you specify a cog name that is also the name of a command, the help for the command will be given.")
    async def help(self, ctx, specific=None):
        """Shows this message."""

        if specific:

            command = self.bot.get_cog(specific)
            command = self.bot.get_command(specific)

            if command is None:
                await ctx.send(":x: Command/cog not found!")
                return
            else:
                if isinstance(command, commands.Cog):
                    cog = command
                    del command

                    emb = discord.Embed(title=f"{ctx.prefix}{cog.name}")

                    for command in cog.walk_commands():
                        alist = []
                        for alias in command.aliases:
                           alist.append(f"`{ctx.prefix}{alias}`")

                        emb.add_field(name=f"`{ctx.prefix}{command.qualified_name}`{', ' if any(command.aliases) else ''}{', '.join(alist)}", description=command.short_doc + "\u200b")
                else:
                    alist = []
                    for alias in command.aliases:
                        alist.append(f"`{alias}`")

                    emb = discord.Embed(title=f"{ctx.prefix}{command.qualified_name}{', ' if any(command.aliases) else ''}{', '.join(alist)}", description=command.short_doc, color=0xf92f2f)
                    emb.add_field(name="Full description", value=command.description + "\u200b")

                    if isinstance(command, commands.GroupMixin):
                        for subcommand in command.commands:
                            alist = []
                            for alias in subcommand.aliases:
                                alist.append(f"`{ctx.prefix}{alias}`")

                            emb.add_field(name=f"`{ctx.prefix}{subcommand.qualified_name}`{', ' if any(subcommand.aliases) else ''}{', '.join(alist)}", value=subcommand.short_doc + "\u200b")
        else:
            emb = discord.Embed(title="Help and Information", color=0xf92f2f)
            for name, command in self.bot.all_commands.items():
                if name in command.aliases or (command.hidden and not await self.bot.is_owner(ctx.author)):
                    continue

                alist = []
                for alias in command.aliases:
                    alist.append(f"`{ctx.prefix}{alias}`")

                emb.add_field(name=f"{name}{', ' if any(command.aliases) else ''}{', '.join(alist)}", value=command.short_doc + "\u200b")

        emb.set_thumbnail(url=self.bot.user.avatar_url)
        emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        emb.set_footer(text=f"{self.bot.description} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=emb)

def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Help(bot))
