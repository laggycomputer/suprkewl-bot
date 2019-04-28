# -*- coding: utf-8 -*-

"""
The MIT License (MIT)
Copyright (c) 2018-2019 laggycomputer
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import os
import pkg_resources
import platform
import time

import discord
import matplotlib.pyplot as plt
from discord.ext import commands

from .utils import apiToHuman


class Info(commands.Cog):

    @commands.command(description="Gives info on role <permsRole> in server (ping the role).")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def roleinfo(self, ctx, role: discord.Role):
        """Gives info on a passed role."""

        emb = discord.Embed(title=f"Info for '{role}', a role in '{ctx.guild}'", color=role.color)
        emb.set_author(name='Me', icon_url=ctx.bot.user.avatar_url)
        emb.add_field(name="Role Color (Hex)", value=role.color)
        emb.add_field(name="Members with Role", value=str(len(role.members)))
        emb.add_field(name="Role ID", value=role.id)

        emb.set_thumbnail(url=ctx.bot.user.avatar_url)
        emb.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        emb.set_footer(text=f"{ctx.bot.description} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        disp_hoist = "No"
        if role.hoist:
            disp_hoist = "Yes"
        emb.add_field(name="'Display role member seperately from online members'", value=disp_hoist)

        sent = (await ctx.send(embed=emb))
        await ctx.bot.register_response(sent, ctx.message)

    @commands.command(
        description="Gives perms on the given role. The bot must have the 'Manage Roles' permission, and the user must "
                    "have a role called 'suprkewl-viewPerms'. Perms may be overridden."
    )
    @commands.guild_only()
    @commands.has_any_role("suprkewl-viewPerms")
    @commands.bot_has_permissions(manage_roles=True)
    async def roleperms(self, ctx, role: discord.Role):
        """Get permissions for a role"""

        emb = discord.Embed(title=f"Perms for '{role}', a role in '{ctx.guild}'", color=0xf92f2f)
        emb.set_thumbnail(url=ctx.bot.user.avatar_url)
        emb.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        emb.set_footer(text=f"{ctx.bot.description} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        perms = role.permissions

        order = [
            1, 28, 13, 16, 11, 10, 3, 6, 4, 15, 12, 17, 23, 24, 25, 14, 8, 2, 22, 18, 9, 0, 5, 26, 20, 7, 19, 27, 21
        ]
        permtuples = []

        for permTuple in iter(perms):
            readablename = apiToHuman[permTuple[0]]
            permtuples.append((readablename, permTuple[1]))

        for number in order:
            fieldname = permtuples[number][0]

            if permtuples[number][1]:
                fieldval = "Yes"
            else:
                fieldval = "No"
            emb.add_field(name=fieldname, value=fieldval)

        sent = (await ctx.send(embed=emb))
        await ctx.bot.register_response(sent, ctx.message)

    @commands.command(
        aliases=["about"], description="Gets some stats about the bot. Has a 5-second cooldown per channel.."
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def botstats(self, ctx):
        """Give some system info for the bot."""

        emb = discord.Embed(title="Bot info", color=0xf92f2f)
        year, month, dayofmonth, hour, minute, second, dayofweek, _, isdst = time.localtime()
        week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        dayofweek = week[dayofweek]
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "November", "December"
        ]
        month = months[month]
        disptime = f"{dayofweek}, {month} {dayofmonth}, {year}; {hour}:{minute}:{second}, Pacific Standard Time"
        if isdst:
            disptime += " (DST)"

        emb.add_field(name="System Time", value=disptime)
        emb.add_field(name="Processor Type", value=platform.machine().lower())
        emb.add_field(name="OS version (short)", value=platform.system() + " " + platform.release())
        emb.add_field(name="OS version (long)", value=platform.platform(aliased=True))
        emb.add_field(
            name="Python Version", value=f"Python {platform.python_branch()}, build date {platform.python_build()[1]}"
        )
        emb.add_field(name="discord.py version", value=pkg_resources.get_distribution("discord.py").version)
        emb.add_field(name="Jishaku version", value=pkg_resources.get_distribution("jishaku").version)
        emb.add_field(name="Processor name", value=platform.processor())
        emb.add_field(name="Current server count", value=str(len(ctx.bot.guilds)))
        emb.add_field(name="Total Users", value=str(len(ctx.bot.users)))

        emb.add_field(name=f"See `{ctx.prefix}git` for source code.", value="\u200b")

        emb.set_thumbnail(url=ctx.bot.user.avatar_url)
        emb.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        emb.set_footer(text=f"{ctx.bot.description} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        sent = (await ctx.send(embed=emb))
        await ctx.bot.register_response(sent, ctx.message)

    @commands.command()
    async def ping(self, ctx):
        """Check the bot's latency."""

        latency = ctx.bot.latency * 1000
        latency = round(latency, 4)
        emb = discord.Embed(description=f":ping_pong: My current latency is {latency} milliseconds.", color=0xf92f2f)
        emb.set_image(
            url="https://images-ext-2.discordapp.net/external/pKGlPehvn1NTxya18d7ZyggEm4pKFakjbO_sYS-pagM/https/media.giphy.com/media/nE8wBpOIfKJKE/giphy.gif"
        )

        sent = (await ctx.send(embed=emb))
        await ctx.bot.register_response(sent, ctx.message)

    def _piegenerate(self, name1, name2, prc, fname):
        labels = [name1, name2]
        sizes = [prc, 100 - prc]
        colors = ["lightcoral", "lightskyblue"]
        patches, _ = plt.pie(sizes, colors=colors, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.axis('equal')
        plt.tight_layout()
        fname += ".png"
        plt.savefig(fname)

        return fname
    @commands.command(description="Generates a pie chart of those with a role and those without")
    @commands.cooldown(1, 3, commands.BucketType.default)
    async def rolepie(self, ctx, role_id: discord.Role):
        """Generate a piechart of those who have <role>."""

        if ctx.guild.large:
            await ctx.bot.request_offline_members(ctx.guild)

        m = ctx.guild.members
        prc = (sum(m._roles.has(role_id) for m in m) / len(m)) * 100

        names = [f"Members with '{role.name}' role", f"Members without '{role.name}' role"]
        fname = str(ctx.message.id)
        img_out = self._piegenerate(names[0], names[1], prc, fname)

        fp = discord.File(img_out, filename="piechart.png")

        sent = (await ctx.send(":white_check_mark:", file=fp))
        os.delete(img_out)
        await ctx.bot.register_response(sent, ctx.message)

def setup(bot):
    bot.add_cog(Info())
