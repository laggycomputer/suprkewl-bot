# -*- coding: utf-8 -*-
"""Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import asyncio
import platform
import random
import sys

import discord
from discord.ext import commands
from discord.ext.commands import Bot


class theBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_task = self.loop.create_task(self.playingstatus())

        startup_extensions = ["jishaku", "ext.Text", "ext.Randomizers", "ext.Documentation", "ext.Moderation", "ext.Info", "testing"]

        for extension in startup_extensions:
            try:
                self.load_extension(extension)
                print(f"Loaded module {extension}. yay")
            except Exception as e:
                exc = f"{e.__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exc}")

    async def on_ready(self):

        print(f"Logged in as {self.user.name} (ID {self.user.id} | Connected to {len(self.guilds)} servers | Connected to {len(set(client.get_all_members()))} users")
        print("-" * 8)
        print(f"Current Discord.py Version: {discord.__version__} | Current Python Version: {platform.python_version()}")
        print("-" * 8)
        print(f"Use this link to invite {self.user.name}:")
        print(f"https://discordapp.com/oauth2/authorize?client_id={self.user.id}&scope=bot&permissions=8")
        print("-" * 8)

    async def on_message(self, message):

        print(f"Got message '{message.content}'")
        print(f"From @{message.author}")
        print(f"In server {message.guild}")
        print(f"In channel {message.channel}")

        if message.author.bot:
            return
        else:
            if isinstance(message.channel, discord.abc.GuildChannel):
                if message.channel.permissions_for(message.guild.me).send_messages:

                    if message.content == "<@408869071946514452>":
                        await message.channel.send(":eyes: **WHO DARE PING** btw my prefix is `s!`.")

                    await self.process_commands(message)

                else:
                    if message.content.startswith("s!"):
                        await message.author.send(":x: I can't send messages there! Perhaps try again elsewhere?")
            else:
                await self.process_commands(message)

    async def playingstatus(self):

        await self.wait_until_ready()

        playing_statuses = ["with the community",
                            "with my dad, Too Laggy",
                            "github.com/laggycomputer/suprkewl-bot",
                            "being open source",
                            "I don't game...",
                            "waiting for you to call me! s!help",
                            "being SuprKewl!",
                            "with my Raspberry Pi",
                            "creeping through the shadows",
                            "eating robot food, brb",
                            "being improved!",
                            "ping and run",
                            "helping the community",
                            "living under the MIT license!",
                            "at a robot party, brb in a bit",
                            "meme-scrolling",
                            "and plotting pranks",
                            "with the Discord API"]

        while not self.is_closed():
            status = f"{random.choice(playing_statuses)} | lurking in {len(self.guilds)} servers and watching over {len(self.users)} users..."

            await self.change_presence(activity = discord.Game(name = status))
            await asyncio.sleep(120)
    async def on_command_error(ctx, error):
        if hasattr(ctx.command, "on_error"):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)

        error = getattr(error, "original", error)

		def perms_list(perms):	
			if len(perms) == 0:
				return None
			else:
				if len(perms) == 1:
					return len[0]
				else:
					list = ", ".join(perms[0:-1])
					list += f", and {perms[-1]}"
					return list
		
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):

            emb = discord.Embed
            emb.add_field(name="Disabled Command", value=f":x: `{ctx.prefix}{ctx.command}` has been disabled!")
            emb.set_footer(f"Command invoked by {ctx.author}")

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.NoPrivateMessage):

            emb = discord.Embed
            emb.add_field(name="This command is disabled in DMs", value=f":x: `{ctx.prefix}{ctx.command}` can only be used in servers, not in DMs or DM groups.")
            emb.set_footer(f"Command invoked by {ctx.author}")

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.CommandOnCooldown):

            retry = round(error.retry_after, 2)

            emb = discord.Embed
            emb.add_field(name="Command on Cooldown",
                          value=f"Woah there! You just triggered a cooldown trying to run `{ctx.prefix}{ctx.command}`. I'll start it again after the cooldown of {retry} is over."}
            emb.set_footer(f"Command invoked by {ctx.author}")

            msg=await ctx.send(embed=emb)

            await asyncio.sleep(retry)

            await ctx.send(f"{ctx.author.mention} The cooldown is over! Starting command `{ctx.prefix}{ctx.command}`...")

            await ctx.invoke(ctx.command, ctx.*args, ctx.**kwargs)

            return msg
					
		elif isinstance(error, commands.MissingPermissions):
		
			emb = discord.Embed
			missingPerms = perms_list(error.missing_perms)
			emb.add_field(name="User Missing Permissions", value=f":x: Permission denied to run {ctx.prefix}{ctx.command}. You need to be able to {missingPerms}.")
			emb.set_footer(f"Command invoked by {ctx.author}")
			
			return await ctx.send(embed=emb)
			
		elif isinstance(error, commands.BotMissingPermissions):
			
			emb = discord.Embed
			missingPerms = perms_list(error.missing_perms)
			emb.add_field(name="Bot Missing Permissions", value=f":x: I don't have the proper permissions to run {ctx.prefix}{ctx.command}. I need to be allowed to {missingPerms}.")
			emb.set_footer(f"Command invoked by {ctx.author}")
			
			return await ctx.send(embed=emb)
			
        print(f"Ignoring exception in command {ctx.prefix}{ctx.command}:", file=sys.stderr)

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

client = theBot(
                command_prefix="s!",
                description="SuprKewl Bot, by Too Laggy#3878",
                pm_help=True)

client.run("TOKEN")
