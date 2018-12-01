# -*- coding: utf-8 -*-
"""Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import discord
from discord.ext import commands
import redis
import time

class testing():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ["userinfo"], description = "Get the profile of a passed <user>. Please note that <user> DOES NOT DEFAULT TO THE COMMAND INVOKER. Instead, use s!myprofile to get your own profile.")
    async def profile(self, ctx, user: discord.User):
        """See 's!help profile' for some important notes."""

        pool = redis.ConnectionPool(host = 'localhost', port = 6379, db = 0)
        r = redis.Redis(connection_pool = pool)
        defaultbio = "This user has no set bio! If that's you, please set it with `s!setbio`."

        """pipe = r.pipeline()
        pipe.hsetnx("userbios", user.id, defaultbio)
        bio=pipe.hget("userbios", user.id)
        pipe.execute()"""

        msg = discord.Embed(color = user.colour)

        if user.avatar_url == "":
            msg.set_thumbnail(user.default_avatar)
        else:
            msg.set_thumbnail(url = "https://cdn.discordapp.com/avatars/{}/{}.png".format(user.id, user.avatar))
            
        msg.add_field(name = "Username", value = user.name)
        msg.add_field(name = "Discriminator", value = str(user.discriminator))
        msg.add_field(name = "Is a bot", value = str(user.bot))
        msg.add_field(name = "Mention String", value="\\" + user.mention)
        msg.add_field(name = "Discord join date and time", value = str(user.created_at) + " (in UTC timezone)")
        msg.add_field(name = "Server join date", value = str(user.joined_at) + " (first time user joined)")

        await ctx.send(embed = msg)

    @commands.command(description = "A test for cooldown errors. Does nothing otherwise.")
    @commands.cooldown(1, 86410, commands.BucketType.user)
    async def cooldowntest(self, ctx):
        await ctx.send(content = "Cooldowns ok, command triggered")

    @cooldowntest.error
    async def cooldowntest_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            seconds = round(seconds, 2)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)

            if hours > 0:
                await ctx.send("**This command is on cooldown!** {0}hr, {1}m and {2}s remaining. Reinvoking command then.".format(hours, minutes, seconds))
            else:
                await ctx.send("**This command is on cooldown!** {0}m and {1}s remaining. Reinvoking command then.".format(minutes, seconds))
            time.sleep(error.retry_after)
            await ctx.send("{0.mention}! The cooldown has ended, reinvoking command...".format(ctx.author))
            await ctx.reinvoke(restart = True)

    @commands.command()
    async def roleiter(self, ctx, role: discord.Role):
        for i in iter(role.permissions):
            print(i)
            
def setup(bot):
    bot.add_cog(testing(bot))
