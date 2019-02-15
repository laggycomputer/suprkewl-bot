# -*- coding: utf-8 -*-
"""Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import discord
from discord.ext import commands

class Moderation():
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["purge"], invoke_without_command=True, description="Clear <count> messages from the bottom of the current channel, excluding the message used to run the command. Remember that bots cannot delete messages older than 2 weeks, and that both the command invoker and the bot must have the 'Manage Messages' permission.")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, count: int):
        """(GUILD ONLY) Delete messages. See full command help for more."""

        await ctx.message.delete()

        messages = await ctx.history(limit=count).flatten()

        await ctx.send(delete_after=5, content="Clearing...")
        deleted = 0
        errorcnt = 0

        for message in messages:
            try:
                await message.delete()
                deleted += 1
            except Exception:
                errorcnt += 1

        await ctx.send(delete_after=10, content=f"<:suprKewl:508479728613851136> Done! Deleted {deleted} messages, failed to delete {errorcnt} messages. Remember that bots cannot delete messages older than 2 weeks. If you still see some messages that should be deleted, it may be a Discord bug. Reload Discord (Cntrl or Command R) and they should disappear.")

    @clear.command(description="Delete messages within the past <count> messages, but only if they are from <user>. See the help dialog on the main clear command for rate-limit info and more.")
    async def user(self, ctx, user: discord.Member, count: int):

        if not await ctx.command.parent.can_run(ctx):
            return

        await ctx.message.delete()

        messages = await ctx.history(limit=count).flatten()

        await ctx.send(delete_after=5, content="Clearing...")
        total = 0
        errorcnt = 0

        for message in messages:
            if message.author == user:
                try:
                    await message.delete()
                except Exception:
                    errorcnt += 1
                total += 1

        await ctx.send(delete_after=10, content=f"<:suprKewl:508479728613851136> Done! Tried to delete {total} messages, failed to delete {errorcnt} messages. Remember that bots cannot delete messages older than 2 weeks. If you still see some messages that should be deleted, it may be a Discord bug. Reload Discord (Cntrl or Command R) and they should disappear.")

    @clear.command(description="Delete all messages within the given limit that were sent by members with the given role (ping it). See the main clear command help for info on rate-limits and more.")
    async def role(self, ctx, role: discord.Role, count: int):

        if not await ctx.command.parent.can_run(ctx):
            return

        await ctx.message.delete()

        messages = await ctx.history(limit=count).flatten()

        await ctx.send(delete_after=5, content="Clearing...")
        total = 0
        errorcnt = 0

        for message in messages:
            if message.author in role.members:
                try:
                    await message.delete()
                except Exception:
                    errorent += 1
                total +=1

        await ctx.send(delete_after=10, content=f"<:suprKewl:508479728613851136> Done! Tried to delete {total} messages, failed to delete {errorcnt} messages. Remember that bots cannot delete messages older than 2 weeks. If you still see some messages that should be deleted, it may be a Discord bug. Reload Discord (Cntrl or Command R) and they should disappear.")

    @commands.command(description="Kicks the given <target>. Please ensure both the bot and the command invoker have the permission 'Kick Members' before running this command. Also notifies <target> of kick.")
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, target: discord.Member):
        """(GUILD ONLY) Kick someone. See full help command."""

        if target == ctx.guild.owner:
            await ctx.send(":x: I can't kick the server owner!")
        else:
            if target == meInServer:
                await ctx.send(":x: I can't kick myself!")
            else:
                if ctx.author == target:
                    await ctx.send(":x: I'm not kicking you! If you hate this place that much, just leave!")
                else:
                    if meInServer.top_role < invoker.top_role:
                        try:
                            await target.kick()
                            await ctx.send(f":boom: RIP {target.mention}.")
                            await target.send(f"You've been kicked from `{ctx.guild}`. :slight_frown:")
                        except Exception:
                            await ctx.send(":x: ?! An error has occured!")
                    else:
                        await ctx.send(":x: The passed member has a higher/equal top role than/to me, meaning I can't kick him/her. Oops! Try again...")

    @commands.command(description="Bans the given <target> with reason <reason>, deleteing all messages sent from that user over the last <deletedays> days (must be an integer betweeen and including 0 and 7). Ensure that both the command invoker and the bot have the permission 'Ban Members'. Also DMs <target> to let them know they've been banned.")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, target: discord.Member, deletedays: int, reason: str):
        """(GUILD ONLY) Ban someone. See main help dialog."""

        if isinstance(ctx.channel, discord.abc.GuildChannel):
            if target == ctx.guild.owner:
                await ctx.send(":x: The server owner can't be banned!")
            else:
                if target == meInServer:
                    await ctx.send(":x: Oopsie! Can't ban myself...")
                else:
                    if target == ctx.author:
                        await ctx.send(":x: I'm not banning you! Just leave if you hate this place so much!")
                    else:
                        if meInServer.top_role > target.top_role:
                            if deletedays <= 7 and deletedays >= 0:
                                try:
                                    await ctx.guild.ban(target, delete_message_days=deletedays, reason=reason)
                                    await ctx.send(f":boom: **INSTA BAN!** Swung the ban hammer on {target.mention}.")
                                    await target.send(f"Looks like you were banned from `{ctx.guild}`, {target.mention}. :slight_frown:")
                                except Exception:
                                    await ctx.send(":x: Oh noes! It didn't work! I may have ran into ratelimits, or some unknown error may have occured.")
                            else:
                                await ctx.send(f"Oops! You specified an out-of-range integer for <deletedays>! See `{ctx.prefix}help ban` for info on limits.")
                        else:
                            await ctx.send(":x: Oops! That member has a higher or equal top role to me, meaning I can't ban him/her!")

    @commands.command(description="Unbans the given <target>. The target must be banned from the given server, and both the command invoker and the bot must have the permission 'Ban Members'. <target> will be DM'd once they are unbanned.")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)

    async def unban(self, ctx, target: discord.User):
        """(GUILD ONLY) Unbans someone. Please refer to the main help dialog."""

        targetBanned = False
        async for ban in await ctx.guild.bans():
            if ban[0] == target:
                targetBanned = True
        if targetBanned:
            try:
                await ctx.guild.unban(target)
                await ctx.send("<:suprKewl:508479728613851136> Unbanned!")
                await target.send(f":thumbs_up: You've been unbanned from {ctx.guild}! If you still have a valid invite, you can use it to rejoin.")
            except Exception:
                await msg.edit(content = f"{ctx.author.mention} :x: Oops! Looks like I couldn't unban {target.name}#{target.discriminator}! Perhaps I crashed into a rate-limit or tripped on another unknown error. Perhaps try again?")
        else:
            await msg.edit(content = f"{ctx.author.mention} :x: Oops! That user ain't banned! Perhaps you meant someone else?")

    @commands.command(description="Gives the list of banned users for this server. Both the command invoker and the bot must have the permission `Ban Members`.")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def banlist(self, ctx):
        """(GUILD ONLY) Gives a list of banned users."""

        emb = discord.Embed()
        emb.set_author(name='Me', icon_url=self.bot.user.avatar_url)
        list = []
        banlist = await ctx.guild.bans()
        for ban in banlist:
            list.append(ban[0].name + "#" + ban[0].discriminator)
        commaspace = ", "
        msg = commaspace.join(list)
        emb.add_field(name=f"Banned users for {ctx.guild}", value=msg)

        await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(Moderation(bot))
