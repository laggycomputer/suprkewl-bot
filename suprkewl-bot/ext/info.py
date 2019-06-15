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

import io
import typing
from urllib.parse import quote as urlquote

import discord
from discord.ext import commands

from .utils import permissions_converter, escape_codeblocks, format_json


class Info(commands.Cog):

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.group(
        description="Gives the data under a message, channel, or member in a JSON format, as received from the"
                    " Discord API."
    )
    async def raw(self, ctx):
        """Returns a dict version of some objects."""

        if ctx.invoked_subcommand is None:
            await ctx.send(":x: Please provide a valid subcommand!")

    @raw.command(name="message", aliases=["msg"])
    async def raw_message(self, ctx, *, message: discord.Message):
        """Return a message as a dict."""

        raw = await ctx.bot.http.get_message(message.channel.id, message.id)

        try:
            await ctx.send(f"```json\n{escape_codeblocks(format_json(raw))}```")
        except discord.HTTPException:
            fp = io.BytesIO(format_json(raw))
            fp = discord.File(fp, "raw.txt")

            await ctx.send("Your output was placed in the attached file:", file=fp)

    @raw.command(name="member", aliases=["user"])
    async def raw_member(self, ctx, *, user: discord.User = None):
        """Return a member as a dict."""
        if user is None:
            user = ctx.author

        route = discord.http.Route("GET", f"/users/{user.id}")
        raw = await ctx.bot.http.request(route)

        await ctx.send(f"```json\n{escape_codeblocks(format_json(raw))}```")

    @raw.command(name="channel")
    async def raw_channel(
            self, ctx, *, channel: typing.Union[
                discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel
            ] = None
    ):
        """Return a channel as a dict."""

        if channel is None:
            channel = ctx.channel

        route = discord.http.Route("GET", f"/channels/{channel.id}")
        try:
            raw = await ctx.bot.http.request(route)
        except discord.Forbidden:
            return await ctx.send(":x: I can't see info on that channel!")

        await ctx.send(f"```json\n{escape_codeblocks(format_json(raw))}```")

    @commands.command(description="Gives info on role <permsRole> in server (ping the role).")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def roleinfo(self, ctx, *, role: discord.Role):
        """Gives info on a passed role."""

        emb = discord.Embed(title=f"Info for '{role}', a role in '{ctx.guild}'", color=role.color)
        emb.set_author(name='Me', icon_url=ctx.bot.user.avatar_url)
        emb.add_field(name="Role Color (Hex)", value=role.color)
        emb.add_field(name="Members with Role", value=str(len(role.members)))
        emb.add_field(name="Role ID", value=role.id)

        emb.set_thumbnail(url=ctx.bot.user.avatar_url)
        emb.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        emb.set_footer(text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        disp_hoist = "No"
        if role.hoist:
            disp_hoist = "Yes"
        emb.add_field(name="'Display role member seperately from online members'", value=disp_hoist)

        await ctx.send(embed=emb)

    @commands.command(
        description="Gives perms on the given role. The bot must have the 'Manage Roles' permission, and the user must "
                    "have a role called 'suprkewl-viewPerms'. Perms may be overridden."
    )
    @commands.guild_only()
    @commands.has_any_role("suprkewl-viewPerms")
    @commands.bot_has_permissions(manage_roles=True)
    async def roleperms(self, ctx, *, role: discord.Role):
        """Get permissions for a role"""

        emb = discord.Embed(title=f"Perms for '{role}', a role in '{ctx.guild}'", color=ctx.bot.embed_color)
        emb.set_thumbnail(url=ctx.bot.user.avatar_url)
        emb.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        emb.set_footer(text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        perms = role.permissions

        order = [
            1, 28, 13, 16, 11, 10, 3, 6, 4, 15, 12, 17, 23, 24, 25, 14, 8, 2, 22, 18, 9, 0, 5, 26, 20, 7, 19, 27, 21
        ]
        permtuples = []

        for permTuple in iter(perms):
            readablename = permissions_converter[permTuple[0]]
            permtuples.append((readablename, permTuple[1]))

        for number in order:
            fieldname = permtuples[number][0]

            if permtuples[number][1]:
                fieldval = "Yes"
            else:
                fieldval = "No"
            emb.add_field(name=fieldname, value=fieldval)

        await ctx.send(embed=emb)

    # Thanks to Takaru, PendragonLore/TakaruBot
    @commands.command()
    async def pypi(self, ctx, *, name):
        data = await (await ctx.bot.http2.get(f"https://pypi.org/pypi/{urlquote(name, safe='')}/json")).json()

        embed = discord.Embed(
            title=data["info"]["name"],
            url=data["info"]["package_url"],
            color=discord.Color.dark_blue()
        )
        embed.set_author(name=data["info"]["author"])
        embed.description = data["info"]["summary"] or "No short description."
        embed.add_field(
            name="Classifiers",
            value="\n".join(data["info"]["classifiers"]) or "No classifiers.")
        embed.set_footer(
            text=f"Latest: {data['info']['version']} |"
                 f" Keywords: {data['info']['keywords'] or 'No keywords.'}"
        )
        fp = discord.File("../assets/pypi.png", "image.png")
        embed.set_thumbnail(
            url="attachment://image.png"
        )

        await ctx.send(embed=embed, file=fp)


def setup(bot):
    bot.add_cog(Info())
