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

import discord
from discord.ext import commands
from jishaku.codeblocks import CodeblockConverter


class Admin(commands.Cog):

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command(hidden=True, aliases=["procm", "procmanager", "supervisor", "supervisorctl"])
    async def proc(self, ctx, *, args):
        conv = await CodeblockConverter().convert(ctx, f"/usr/local/bin/supervisorctl {args}")
        await ctx.invoke(ctx.bot.get_command("jsk sh"), argument=conv)

    @commands.command(hidden=True, name="del")
    async def deletemsg(self, ctx, message: int):
        try:
            m = await ctx.fetch_message(message)
            sent = None
        except discord.NotFound:
            sent = (await ctx.send(":x: Message not found. It must be in the current channel."))
            m = None
        except discord.Forbidden:
            sent = (await ctx.send(
                ":x: I do not have permission to `Read Message History` here. I cannot fetch the message."
            ))
            m = None
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
