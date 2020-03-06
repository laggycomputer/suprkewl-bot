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

import asyncio
import platform
import random
import textwrap
import traceback

import aiohttp
import aiosqlite
import discord
from discord.ext import commands
from ext.utils import permissions_converter, linecount, Context

import config
import redis


class suprkewl_bot(commands.Bot):

    def __init__(self, extra_owners=[], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.extra_owners = extra_owners

        self.embed_color = 0xf92f2f

        self.commands_used = 0
        self.messages_seen = 0

        self.redis = None
        self.http2 = None
        self.db = None

        self.ps_task = self.loop.create_task(self.playingstatus())
        self.dbl_task = self.loop.create_task(self.dbl_guild_update())
        self.change_status = True
        self.owner_no_prefix = False

        startup_extensions = [
            "ext.about",
            "ext.admin",
            "ext.crypto",
            "ext.fun",
            "ext.help",
            "ext.img",
            "ext.info",
            "ext.markov",
            "ext.mod",
            "ext.settings",
            "ext.stats",
            "ext.text",
            "ext.util",
            "jishaku"
        ]

        loaded = []
        for extension in startup_extensions:
            try:
                self.load_extension(extension)
                loaded.append(extension)
            except Exception as e:
                exc = f"{e.__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exc}")

        print("Loaded extensions: " + "\n" + "\n".join(textwrap.wrap(", ".join(loaded))))

    async def on_ready(self):
        if not self.redis:
            self.redis = redis.Redis()
            await self.redis.connect()
        if not self.http2:
            self.http2 = aiohttp.ClientSession()
        if not self.db:
            self.db = await aiosqlite.connect(config.db_path)

        print(f"Logged in as {self.user.name} (UID {self.user.id})")
        print("-" * 8)
        print(f"discord.py {discord.__version__} | Python {platform.python_version()}")
        print("-" * 8)
        print("Use this link to invite this bot:")
        invite = discord.utils.oauth_url(self.user.id)
        print(invite)
        print("-" * 8)

    async def on_message(self, message):
        if not self.is_ready():
            return

        self.messages_seen += 1

        if message.author.bot:
            return
        else:
            await self.track_message(f"tracked_message {message.id}")

            if isinstance(message.channel, discord.abc.GuildChannel):
                if message.channel.permissions_for(message.guild.me).send_messages:
                    if message.guild.me in message.mentions:
                        ping_images = [
                            "assets/angery,gif",
                            "assets/eyes.png",
                        ]

                        resp = await (
                            await self.db.execute(f"SELECT prefix FROM guilds WHERE id={message.guild.id};")
                        ).fetchall()

                        if resp:
                            emb = discord.Embed(
                                color=self.embed_color,
                                description=f":eyes: Who pinged? My prefix is `s!` and the custom server prefix is "
                                            f"`{resp[0][0]}`. If you are in a DM with me, or you are my owner, I do "
                                            f"not require a prefix."
                            )
                        else:
                            emb = discord.Embed(
                                color=self.embed_color,
                                description=f":eyes: Who pinged? My prefix is `s!`. If you are in a DM with"
                                            f" me, or you are my owner, I do not require a prefix."
                            )
                        fname = random.choice(ping_images)
                        ext = fname.split(".")[-1]
                        fname_finished = f"image.{ext}"
                        fp = discord.File(fname, fname_finished)
                        emb.set_image(url="attachment://" + fname_finished)

                        await message.channel.send(embed=emb, file=fp)

                    for m in message.mentions:
                        if await self.is_owner(m) and not await self.is_owner(message.author):
                            try:
                                await message.channel.send("<:angryping:564532599918297117>")
                            except discord.HTTPException:
                                pass

                    await self.process_commands(message)

                else:
                    if message.content.startswith("s!"):
                        try:
                            await message.author.send(":x: I can't send messages there! Perhaps try again elsewhere?")
                        except discord.Forbidden:
                            pass
            else:
                await self.process_commands(message)

    async def on_command_completion(self, ctx):
        self.commands_used += 1

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

        ignored = (commands.CommandNotFound,)
        quote_errors = (
            commands.UnexpectedQuoteError, commands.InvalidEndOfQuotedStringError, commands.ExpectedClosingQuoteError
        )
        bad_arg_errors = (commands.BadArgument, commands.BadUnionArgument)

        error = getattr(error, "original", error)

        def perms_list(perms):

            if len(perms) == 0:
                return None
            else:
                if len(perms) == 1:
                    return permissions_converter[perms[0]]
                else:
                    fmt = ""
                    for i in range(0, len(perms)):
                        fmt += permissions_converter[i]
                        fmt += ", "
                        fmt += f"and {perms[-1]}"

                    return fmt

        if isinstance(error, ignored):
            return

        elif isinstance(error, quote_errors):
            await ctx.send(
                "Your argument(s) had too many or too few quotes. Remember to match all opening quotes with closing"
                " quotes.")

        elif isinstance(error, bad_arg_errors):
            await ctx.send(":x: Your argument(s) could not be converted. If you are looking for a channel or message,"
                           "please ensure that I have permission to see that channel or message.")

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"`{error.param.name}` is a missing required argument.")
            await ctx.send_help(ctx.command)

        elif isinstance(error, commands.DisabledCommand):
            emb = ctx.default_embed
            emb.add_field(name="Disabled Command", value=f":x: `{ctx.prefix}{ctx.command}` has been disabled!")

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.NoPrivateMessage):
            emb = ctx.default_embed
            emb.add_field(
                name="This command is disabled in DMs",
                value=f":x: `{ctx.prefix}{ctx.command}` can only be used in servers, not in DMs or DM groups."
            )

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

            emb = ctx.default_embed
            emb.add_field(
                name="Command on Cooldown",
                value=f"Woah there! You just triggered a {cooldown_type} cooldown trying to run "
                f"`{ctx.prefix}{ctx.command}`. Wait {retry} seconds."
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.MissingPermissions):
            emb = ctx.default_embed
            missing_perms = perms_list(error.missing_perms)
            emb.add_field(
                name="User Missing Permissions",
                value=f":x: Permission denied to run `{ctx.prefix}{ctx.command}`."
                f" You need to be able to {missing_perms}."
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.BotMissingPermissions):
            emb = ctx.default_embed
            missing_perms = perms_list(error.missing_perms)
            emb.add_field(
                name="Bot Missing Permissions",
                value=f":x: I don't have the proper permissions to run `{ctx.prefix}{ctx.command}`."
                f" I need to be allowed to {missing_perms}."
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.NotOwner):
            emb = ctx.default_embed
            emb.add_field(
                name="Permission denied",
                value=f":x: You must be a bot owner to run `{ctx.prefix}{ctx.command}`."
            )

            return await ctx.send(embed=emb)

        print(f"Ignoring exception in command {ctx.prefix}{ctx.command}:")

        traceback.print_exception(type(error), error, error.__traceback__)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)
        await self.invoke(ctx)

    async def is_owner(self, user):
        return await super().is_owner(user) or user.id in self.extra_owners

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
            "with the Discord API",
            "with your emotions"
        ]

        while self.is_ready() and self.change_status:
            status = random.choice(playing_statuses)
            status += f" | lurking in {len(self.guilds)} servers and watching over {len(self.users)} users..."

            await self.change_presence(activity=discord.Game(name=status), status=discord.Status.idle)
            await asyncio.sleep(120)

    async def dbl_guild_update(self):
        await self.wait_until_ready()

        while not self.is_closed():
            await self.http2.post(
                f"https://discordbots.org/api/bots/{self.user.id}/stats",
                json=dict(server_count=len(self.guilds)),
                headers={"Content-Type": "application/json", "Authorization": config.dbl_token}
            )
            await asyncio.sleep(1800)

    async def logout(self):
        if not self.http2.closed:
            await self.http2.close()
            await asyncio.sleep(0)
        self.redis.disconnect()  # yes this not a coro
        await self.db.close()
        await super().logout()

    async def post_to_hastebin(self, data):
        data = data.encode("utf-8")
        async with self.http2.post("https://hastebin.com/documents", data=data) as resp:
            out = await resp.json()

        assert "key" in out

        return "https://hastebin.com/" + out["key"]

    @property
    def embed_footer(self):
        return random.choice((
            "Did you know? If you are in a DM with me, you don't need to use a prefix.",
            "Don't run the code and no errors will appear.",
            "I am Nobody, nobody is perfect, therefore I am perfect. - Dandi Daley Mackall",
            "I dream of a better world where chickens can cross the road without having their motives called into"
            " serious question by members of another species.",
            "If plan A fails, don't worry; there are still 25 more letters in the alphabet.",
            "If two wrongs don't make a right, try three.",
            "If you work 8 hours a day as a regular worker, you may one day be promoted to boss and work 12 hours a"
            " day.",
            "Instant gratification takes too long - Carrie Fisher",
            "Interestingly enough, Moses owned the first cloud-synced tablet.",
            "It's called a miracle because it doesn't happen.",
            "Just read that 4,153,237 people got married last year, not to cause any trouble but shouldn't that be an"
            " even number?",
            "Man cannot live by bread alone; he must have peanut butter.",
            "May all your bacon burn.",
            "Regex by trial and error: Combining dots slashes and dots until a thing happens.",
            "The center of a donut is 100% fat free.",
            "The word utopia is derived from the Latin 'Utopia', meaning 'nothing, impossible'.",
            "There are two kinds of people at a party; the ones that want to stay and those who want to leave. The"
            " problem is they are usually married to each other.",
            "To succeed in life, you need three things; a wishbone, a backbone and a funny bone. - Reba McEntire",
            linecount(),
            "You can edit a command invocation to change my response."
        ))


async def get_pre(bot, message):
    pre = ["s!"]
    is_owner = await bot.is_owner(message.author)
    if isinstance(message.channel, discord.DMChannel) or (is_owner and not bot.owner_no_prefix):
        pre.append("")

    return pre
