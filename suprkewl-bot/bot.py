# -*- coding: utf-8 -*-

"""
Copyright (C) 2019  laggycomputer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import platform
import random
import traceback

import aiohttp
import discord
from discord.ext import commands
from ext.utils import apiToHuman, linecount, plural

import config
import redis


class theBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.embed_color = 0xf92f2f

        self.redis = None
        self.http2 = None

        self.bg_task = self.loop.create_task(self.playingstatus())
        self.change_status = True

        startup_extensions = [
            "ext.about",
            "ext.admin",
            "ext.crypto",
            "ext.fun",
            "ext.help",
            "ext.info",
            "ext.mod",
            "ext.text",
            "jishaku"
        ]

        for extension in startup_extensions:
            try:
                self.load_extension(extension)
                print(f"Loaded cog {extension}.")
            except Exception as e:
                exc = f"{e.__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exc}")

    async def on_ready(self):
        if not self.redis:
            self.redis = redis.Redis()
            await self.redis.connect()
        if not self.http2:
            self.http2 = aiohttp.ClientSession()

        print(
            f"Logged in as {self.user.name} (UID {self.user.id}) | Connected to {len(self.guilds)} servers and their "
            f"combined {len(set(self.get_all_members()))} members"
        )
        print("-" * 8)
        print(
            f"Current discord.py version: {discord.__version__} | Current Python version: {platform.python_version()}"
        )
        print("-" * 8)
        print(f"Use this link to invite this bot:")
        print(f"https://discordapp.com/oauth2/authorize?client_id={self.user.id}&scope=bot&permissions=8")
        print("-" * 8)

    async def on_message(self, message):
        if not self.is_ready():
            return
        try:
            print(f"Got message '{message.content}'")
            print(f"From @{message.author}")
            print(f"From @{message.author}")
            print(f"In server {message.guild}")
            print(f"In channel {message.channel}")

        except UnicodeDecodeError:
            print("Message properties not printable")

        if len(message.embeds) > 0:
            embeds = ""
            for emb in message.embeds:
                embeds += str(emb.to_dict())
            print(f"With embed(s):\n{embeds}")

        if message.author.bot:
            return
        else:
            await self.track_message(f"tracked_message {message.id}")

            if isinstance(message.channel, discord.abc.GuildChannel):
                if message.channel.permissions_for(message.guild.me).send_messages:
                    if message.content.startswith(message.guild.me.mention):
                        ping_images = [
                            "../assets/angery,gif",
                            "../assets/eyes.png",
                        ]
                        desc = plural(await get_pre(self, message))
                        emb = discord.Embed(
                            color=self.embed_color,
                            description=f":eyes: Who pinged? My prefix(es) is/are `{desc}`. If you are in a DM with me, I do not require a prefix."
                        )
                        fname = random.choice(ping_images)
                        ext = fname.split(".")[-1]
                        fname_finished = f"image.{ext}"
                        fp = discord.File(fname, fname_finished)
                        emb.set_image(url="attachment://" + fname_finished)

                        await message.channel.send(embed=emb, file=fp)

                    owner = (await self.application_info()).owner
                    m1 = f"<@!{owner.id}>"
                    m2 = f"<@{owner.id}>"
                    if (message.content.startswith(m1) or message.content.startswith(m2)) and message.author != owner:
                        await message.channel.send("<:angryping:564532599918297117>")

                    await self.process_commands(message)

                else:
                    if message.content.startswith(config.prefix):
                        await message.author.send(":x: I can't send messages there! Perhaps try again elsewhere?")
            else:
                await self.process_commands(message)

    async def on_raw_message_edit(self, payload):
        if not self.is_ready():
            return

        if "content" not in payload.data:
            return

        channel = self.get_channel(int(payload.data["channel_id"]))

        if channel is None:
            return

        message = channel._state._get_message(payload.message_id)
        if message is None:
            try:
                message = await channel.fetch_message(payload.message_id)
            except discord.HTTPException:
                return

        if await self.redis.exists(f"tracked_message {payload.message_id}"):
            await self.clear_messages(f"tracked_message {payload.message_id}")
        await self.process_commands(message)

    async def on_raw_message_delete(self, payload):
        if not self.is_ready():
            return

        if await self.redis.exists(payload.message_id):
            await self.clear_messages(payload.message_id)
            await self.redis.delete(payload.message_id)

    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, "on_error"):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)

        error = getattr(error, "original", error)

        def perms_list(perms):

            if len(perms) == 0:
                return None
            else:
                if len(perms) == 1:
                    return apiToHuman[perms[0]]
                else:
                    fmt = ""
                    for i in range(0, len(perms)):
                        fmt += apiToHuman[i]
                        fmt += ", "
                        fmt += f"and {perms[-1]}"

                    return fmt

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):

            emb = discord.Embed(color=self.embed_color)
            emb.add_field(name="Disabled Command", value=f":x: `{ctx.prefix}{ctx.command}` has been disabled!")
            emb.set_thumbnail(url=self.user.avatar_url)
            emb.set_author(name=self.user.name, icon_url=self.user.avatar_url)
            emb.set_footer(text=f"{self.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.NoPrivateMessage):

            emb = discord.Embed(color=self.embed_color)
            emb.add_field(
                name="This command is disabled in DMs",
                value=f":x: `{ctx.prefix}{ctx.command}` can only be used in servers, not in DMs or DM groups."
            )
            emb.set_thumbnail(url=self.user.avatar_url)
            emb.set_author(name=self.user.name, icon_url=self.user.avatar_url)
            emb.set_footer(text=f"{self.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.CommandOnCooldown):

            retry = round(error.retry_after, 2)

            human_readable_cooldown = {
                commands.BucketType.default: "bot-wide",
                commands.BucketType.user: "per-user",
                commands.BucketType.guild: "server-wide",
                commands.BucketType.channel: "per-channel",
                commands.BucketType.member: "per-server, per-user",
                commands.BucketType.category: "per-category"
            }

            cooldown_type = human_readable_cooldown[error.cooldown.type]

            emb = discord.Embed(color=self.embed_color)
            emb.add_field(
                name="Command on Cooldown",
                value=f"Woah there! You just triggered a {cooldown_type} cooldown trying to run "
                f"`{ctx.prefix}{ctx.command}`. Wait {retry} seconds."
            )
            emb.set_thumbnail(url=self.user.avatar_url)
            emb.set_author(name=self.user.name, icon_url=self.user.avatar_url)
            emb.set_footer(text=f"{self.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.MissingPermissions):

            emb = discord.Embed(color=self.embed_color)
            missing_perms = perms_list(error.missing_perms)
            emb.add_field(
                name="User Missing Permissions",
                value=f":x: Permission denied to run `{ctx.prefix}{ctx.command}`."
                f" You need to be able to {missing_perms}."
            )
            emb.set_thumbnail(url=self.user.avatar_url)
            emb.set_author(name=self.user.name, icon_url=self.user.avatar_url)
            emb.set_footer(text=f"{self.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.BotMissingPermissions):

            emb = discord.Embed(color=self.embed_color)
            missing_perms = perms_list(error.missing_perms)
            emb.add_field(
                name="Bot Missing Permissions",
                value=f":x: I don't have the proper permissions to run `{ctx.prefix}{ctx.command}`."
                f" I need to be allowed to {missing_perms}."
            )
            emb.set_thumbnail(url=self.user.avatar_url)
            emb.set_author(name=self.user.name, icon_url=self.user.avatar_url)
            emb.set_footer(text=f"{self.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=emb)

        print(f"Ignoring exception in command {ctx.prefix}{ctx.command}:")

        traceback.print_exception(type(error), error, error.__traceback__)


    async def track_message(self, message):
        if await self.redis.exists(message):
            return

        await self.redis.rpush(message, 0)
        await self.redis.expire(message, 3600)

    async def clear_messages(self, tracked_message):
        for message_data in await self.redis.lrange(tracked_message, 1, -1):
            channel_id, message_id = message_data.split(":")
            try:
                await self.http.delete_message(
                    int(channel_id), int(message_id))
            except discord.NotFound:
                pass

        await self.redis.execute("LTRIM", tracked_message, 0, 0)

    async def register_response(self, response, request):
        if await self.redis.exists(f"tracked_message {request.id}"):
            await self.redis.rpush(
                f"tracked_message {request.id}",
                f"{response.channel.id}:{response.id}"
            )

    async def playingstatus(self):

        await self.wait_until_ready()

        playing_statuses = [
            " ",
            "and plotting pranks",
            "at a robot party, brb in a bit",
            "being improved!",
            "being open source",
            "being SuprKewl!",
            "chess with Kasparov",
            "creeping through the shadows",
            "eating robot food, brb",
            "github.com/laggycomputer/suprkewl-bot",
            "helping the community",
            "I don't game...",
            "idling",
            "living under the GPL3!",
            "mafia",
            "meme-scrolling",
            "ping and run",
            "tag with other robots",
            "the attention game",
            "waiting for you to call me!",
            "werewolf",
            "with my dad, Too Laggy",
            "with my Raspberry Pi",
            "with the community",
            "with the Discord API"
        ]

        while self.is_ready() and self.change_status:
            status = random.choice(playing_statuses)
            status += f" | lurking in {len(self.guilds)} servers and watching over {len(self.users)} users..."

            await self.change_presence(activity=discord.Game(name=status), status=discord.Status.idle)
            await asyncio.sleep(120)


    async def logout(self):
        if not self.http2.closed:
            await self.http2.close()
            await asyncio.sleep(0)

        await super().logout()


    @property
    def embed_footer(self):
        return random.choice((
            "Did you know? If you are in a DM with me, you don't need to use a prefix.",
            "Don't run the code and no errors will appear.",
            "I am Nobody, nobody is perfect, therefore I am perfect. - Dandi Daley Mackall",
            "If you work 8 hours a day as a regular worker, you may one day be promoted to boss and work 12 hours a"
            " day.",
            "Instant gratification takes too long - Carrie Fisher",
            "It's called a miracle because it doesn't happen.",
            "May all your bacon burn.",
            "The word utopia is derived from the Latin 'Utopia', meaning 'nothing, impossible'.",
            "To succeed in life, you need three things; a wishbone, a backbone and a funny bone. - Reba McEntire",
            linecount()
        ))



async def get_pre(bot, message):
    pre = [config.prefix]
    is_owner = (await bot.is_owner(message.author))
    if isinstance(message.channel, discord.DMChannel) or is_owner:
        pre.append("")

    return pre
