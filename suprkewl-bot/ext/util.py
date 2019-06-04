import io
import json
import re

import discord
from discord.ext import commands

import config


async def download_file(ctx, data):
    cs = ctx.bot.http2
    async with cs.post("http://rtex.probablyaweb.site/api/v2", data={
        "code": data,
        "format": "png"
    }) as resp:
        data = await resp.json()
    return data


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

            async with ctx.bot.http2.get("http://rtex.probablyaweb.site/api/v2/" + fname) as resp:
                fp = io.BytesIO(await resp.content.read())

        await ctx.send(
            ":white_check_mark: Like it or not, this image is better viewed on light theme.",
            file=discord.File(fp, "latex.png")
        )


def setup(bot):
    bot.add_cog(Utilities())
