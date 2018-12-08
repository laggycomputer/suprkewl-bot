# -*- coding: utf-8 -*-
"""Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import discord
import platform
import random
import asyncio

class events():
    def __init__(self, bot):
        self.bot = bot
    
    async def on_ready(self):

        print(f"Logged in as {self.bot.user.name} (ID {self.bot.user.id} | Connected to {len(self.bot.guilds)} servers | Connected to {len(set(self.bot.get_all_members()))} users")
        print("-" * 8)
        print(f"Current Discord.py Version: {discord.__version__} | Current Python Version: {platform.python_version()}")
        print("-" * 8)
        print(f"Use this link to invite {self.bot.user.name}:")
        print(f"https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=8")
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

                    await self.bot.process_commands(message)

                else:
                    if message.content.startswith("s!"):
                        await message.author.send(":x: I can't send messages there! Perhaps try again elsewhere?")
            else:
                await self.bot.process_commands(message)

def setup(bot):
    bot.add_cog(events(bot))