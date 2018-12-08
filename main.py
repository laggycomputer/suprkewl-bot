# -*- coding: utf-8 -*-
"""Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import random
import platform

startup_extensions = ["jishaku", "ext.Text", "ext.Randomizers", "ext.Documentation", "ext.Moderation", "ext.Info", "testing"]

client = commands.Bot(command_prefix = "s!", description = "SuprKewl Bot, by Too Laggy#3878", pm_help = True)

async def playingstatus():

    await client.wait_until_ready()
    
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

    while not client.is_closed():
        status = f"{random.choice(playing_statuses)} | lurking in {len(client.guilds)} servers and watching over {len(client.users)} users..."

        await client.change_presence(activity = discord.Game(name = status))
        await asyncio.sleep(120)

client.bg_task = client.loop.create_task(playingstatus())

@client.event
async def on_ready():

    print(f"Logged in as {client.user.name} (ID {client.user.id} | Connected to {len(client.guilds)} servers | Connected to {len(set(client.get_all_members()))} users")
    print("-" * 8)
    print(f"Current Discord.py Version: {discord.__version__} | Current Python Version: {platform.python_version()}")
    print("-" * 8)
    print(f"Use this link to invite {client.user.name}:")
    print(f"https://discordapp.com/oauth2/authorize?client_id={client.user.id}&scope=bot&permissions=8")
    print("-" * 8)

@client.event
async def on_message(message):

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

                await client.process_commands(message)

            else:
                if message.content.startswith("s!"):
                    await message.author.send(":x: I can't send messages there! Perhaps try again elsewhere?")
        else:
            await client.process_commands(message)

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            client.load_extension(extension)
            print("Loaded module {}. yay".format(extension))
        except Exception as e:
            exc = f"{e.__name__}: {e}"
            print(f"Failed to load extension {extension}\n{exc}")
client.run("TOKEN")
