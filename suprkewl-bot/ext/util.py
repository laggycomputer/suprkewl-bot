import base64
import binascii
from datetime import datetime
import io
import json
import os
import re

import discord
from discord.ext import commands
import gtts

import config


async def download_file(ctx, data):
    cs = ctx.bot.http2
    async with cs.post(f"http://{config.rtex_server}/api/v2", data={
        "code": data,
        "format": "png"
    }) as resp:
        data = await resp.json()
    return data

token_re = re.compile(r"[a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_\-]{27}|mfa\.[a-zA-Z0-9_\-]{84}")


class Utilities(commands.Cog):
    @commands.command(
        description="Renders LaTeX code."
    )
    async def latex(self, ctx, *, code):
        """Render LaTeX code."""

        async with ctx.typing():
            with open("ext/template.tex", "r") as fp:
                template = fp.read()
            template = re.sub(r"%.*\n", "", template)

            with open("ext/replacements.json", "r") as fp:
                replacements = json.loads(fp.read())

            for key, value in replacements.items():
                code = code.replace(key, value)

            ret = await download_file(ctx, template.replace("#CONTENT", code))
            log = ret.pop("log")

        if ret["status"] == "error":
            data = {
                "api_dev_key": config.pastebin_token, "api_option": "paste",
                "api_paste_code": log, "api_paste_expire_date": "1W",
                "api_paste_name": f"Rendering Log (ID: {ctx.message.id})"
            }
            async with ctx.bot.http2.post("https://pastebin.com/api/api_post.php", data=data) as resp:
                if (await resp.text()).startswith("Bad API request, "):
                    sent = await ctx.send("Something wrong happened while rendering. Perhaps your input was invalid?")
                    return await ctx.register_response(sent)
                else:
                    pasted_url = await resp.text()
            sent = await ctx.send(
                f"Something wrong happened while rendering. The render log is available at {pasted_url}.")
            return await ctx.register_response(sent)

        async with ctx.typing():

            fname = ret["filename"]

            async with ctx.bot.http2.get(f"http://{config.rtex_server}/api/v2/" + fname) as resp:
                fp = io.BytesIO(await resp.content.read())

        await ctx.send(
            ":white_check_mark: Like it or not, this image is better viewed on light theme.",
            file=discord.File(fp, "latex.png")
        )

    @commands.command(aliases=["tokenparse", "ptoken"])
    @commands.cooldown(1, 2.5, commands.BucketType.member)
    async def parsetoken(self, ctx, *, token):
        """Parse a Discord auth token."""

        if not token_re.match(token):
            sent = await ctx.send("Not a valid token.")
            return await ctx.register_response(sent)

        t = token.split(".")
        if len(t) != 3:
            sent = await ctx.send("Not a valid token.")
            return await ctx.register_response(sent)

        try:
            id_ = base64.standard_b64decode(t[0]).decode("utf-8")
            try:
                user = await ctx.bot.fetch_user(int(id_))
            except discord.HTTPException:
                user = None
        except binascii.Error:
            sent = await ctx.send("Failed to decode user ID.")
            return await ctx.register_response(sent)

        try:
            token_epoch = 1293840000
            decoded = int.from_bytes(base64.standard_b64decode(t[1] + "=="), "big")
            timestamp = datetime.utcfromtimestamp(decoded)
            if timestamp.year < 2015:
                timestamp = datetime.utcfromtimestamp(decoded + token_epoch)
            date = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except binascii.Error:
            sent = await ctx.send("Failed to decode timestamp.")
            return await ctx.register_response(sent)

        invite = discord.utils.oauth_url(ctx.bot.user.id, discord.Permissions.none())

        fmt = f"**Valid token: **\n\n**User ID is**: {id_} ({user or '*Not fetchable*.'}).\n" \
              f"**Created at**: {date}\n**Cryptographic component**: {t[2]}\n**Invite**: {invite}"

        sent = await ctx.send(fmt)
        await ctx.register_response(sent)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def tts(self, ctx, *, message):
        """Make me speak a message."""

        async with ctx.typing():
            try:
                tts = gtts.gTTS(text=message)
            except AssertionError:
                sent = await ctx.send(":x: There was nothing speakable in that message.")
                return await ctx.register_response(sent)

            # The actual request happens here:
            def save():
                fname = f"{ctx.message.id}.mp3"
                tts.save(fname)  # This uses requests, and has to wait for all of the sound output to be streamed.
                fp = discord.File(fname, "out.mp3")
                return [fname, fp]

            fname, fp = await ctx.bot.loop.run_in_executor(None, save)

        sent = await ctx.send(":white_check_mark:", file=fp)
        await ctx.register_response(sent)

        os.remove(fname)

    @commands.command()
    @commands.guild_only()
    async def banner(self, ctx):
        """Gets the guild banner."""

        if ctx.guild.banner is None:
            sent = await ctx.send("This guild has no banner!")
        else:
            sent = await ctx.send(ctx.guild.banner_url_as(format="png"))
        await ctx.register_response(sent)


def setup(bot):
    bot.add_cog(Utilities())
