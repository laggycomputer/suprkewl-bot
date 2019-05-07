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

import discord
from discord.ext import commands


class Admin(commands.Cog):

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command(hidden=True, name="del")
    async def deletemsg(self, ctx, id: int):
        try:
            m = await ctx.fetch_message(id)
            sent = None
        except discord.NotFound:
            sent = (await ctx.send(":x: Message not found. It must be in the current channel."))
        except discord.Forbidden:
            sent = (await ctx.send(":x: I do not have permission to `Read Message History` here. I cannot fetch the message."))
        finally:
            if sent is not None:
                await ctx.bot.register_response(sent, ctx.message)

        try:
            await m.delete()
            sent = (await ctx.send(":white_check_mark:"))
        except discord.Forbidden:
            sent = (await ctx.send(":x: I do not have permission to delete that message."))
        finally:
            await ctx.bot.register_response(sent, ctx.message)

    @commands.command(hidden=True)
    async def statustoggle(self, ctx):
        if ctx.bot.change_status:
            resp = "Disabling status change."
        else:
            resp = "Enabling status change."
        ctx.bot.change_status = not ctx.bot.change_status

        sent = (await ctx.send(resp))
        await ctx.bot.register_response(sent, ctx.message)

    @commands.command(hidden=True)
    async def statuschange(self, ctx, *, status):
        await ctx.bot.change_presence(activity=discord.Game(name=status), status=discord.Status.idle)
        sent = (await ctx.send(f":white_check_mark: Changed to `{status}`"))
        await ctx.bot.register_response(sent, ctx.message)


def setup(bot):
    bot.add_cog(Admin())
