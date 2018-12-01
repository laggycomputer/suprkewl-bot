# -*- coding: utf-8 -*-
licenseinfo = """Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform
import random
import datetime
import time

startup_extensions = ["Text", "Randomizers", "Documentation", "Moderation", "Info", "testing"]

client = commands.Bot(command_prefix = commands.when_mentioned_or('s!'), description = "SuprKewl Bot, by Too Laggy#3878", pm_help = True)

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
                   "and plotting pranks"]

@client.event
async def on_ready():
    print(licenseinfo)
    status = random.choice(playing_statuses)+" | "
    status += "lurking in {} servers".format(str(len(client.guilds)))
    status += " and watching over {} users.".format(str(len(client.users)))
    await client.change_presence(activity = discord.Game(name = status))

    print('Logged in as ' + client.user.name + ' (ID:' + str(client.user.id) + ') | Connected to '+str(len(client.guilds))+' servers | Connected to ' + str(len(set(client.get_all_members()))) + ' users')
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('------')

@client.event
async def on_message(message):
    if random.randint(1,10) == 1:
        status = "{0} | lurking in {1} servers and watching over {2} users👀...".format(random.choice(playing_statuses), str(len(client.guilds)), str(len(client.users)))
        await client.change_presence(activity = discord.Game(name = status))

    print("Got message '" + message.content + "'")
    print("From " + str(message.author))
    print("In server " + str(message.guild))
    print("In channel " + str(message.channel))

    if message.author.bot:
        return
    else:
        if isinstance(message.channel, discord.abc.GuildChannel):
            if message.channel.permissions_for(message.guild.me).send_messages:
                if message.content == "<@408869071946514452>":
                    await message.channel.send(":eyes: **WHO DARE PING**")
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
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

client.run('token')
