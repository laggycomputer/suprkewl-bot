# -*- coding: utf-8 -*-
"""Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import random

startup_extensions = ["jishaku", "playingloop", "clientevents", "ext.Text", "ext.Randomizers", "ext.Documentation", "ext.Moderation", "ext.Info", "testing"]

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

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            client.load_extension(extension)
            print("Loaded module {}. yay".format(extension))
        except Exception as e:
            exc = f"{e.__name__}: {e}"
            print(f"Failed to load extension {extension}\n{exc}")
client.run("TOKEN")
