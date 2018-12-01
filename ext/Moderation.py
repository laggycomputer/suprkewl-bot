# -*- coding: utf-8 -*-
"""Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import discord
from discord.ext import commands
import time

class Moderation():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description = "Clear <count> messages from the bottom of the current channel. Remember that bots cannot delete messages older than 2 weeks, and that both the command invoker and the bot must have the 'Manage Messages' permission.")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages = True)
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, count: int):
        """(GUILD ONLY) Clear messages. See 's!help clear' for more."""

        await ctx.message.delete()

        messages = await channel.history(limit = count).flatten()
        await ctx.send(delete_after = 5, content = "Clearing...")
        errorcnt = 0

        for message in messages:
            try:
                await message.delete()
            except Exception:
                errorcnt += 1
        await ctx.send(delete_after = 5, content = "<:suprKewl:508479728613851136> GOTEM! Failed to delete {0} messages. Remember that bots cannot delete messages older than 2 weeks. If you still see some messages that should be deleted, it may be a Discord bug. Reload Discord (Cntrl or Command R) and they should disappear.".format(errorcnt))

    @clear.error
    async def clearerr(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(":x: I don't have the needed permission `Manage Messages`. This won't work... yet!")
        if isinstance(error, commands.MissingPermissions):
            await ctx.message.delete()
            await ctx.send(delete_after = 5, content = ":x: You don't have the proper permissions to delete messages! You need the permission `Manage Messages`.")
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(":x: This command is marked for servers only, and will not work in a DM!")

    @commands.command(description = "Kicks the given <target>. Please ensure both the bot and the command invoker have the permission 'Kick Members' before running this command. Also notifies <target> of kick.")
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members = True)
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, target: discord.Member):
        """(GUILD ONLY) Kick someone. See 's!help kick' for more."""

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
                            await ctx.send(":boom: RIP {}.".format(target.mention))
                            await target.send("You've been kicked from `{0.guild.name}`. :slight_frown:".format(ctx))
                        except Exception:
                            await ctx.send(":x: ?! An error has occured!")
                    else:
                        await ctx.send(":x: The passed member has a higher/equal top role than/to me, meaning I can't kick him/her. Oops! Try again...")

    @kick.error
    async def kickerr(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(":x: Whoa! I don't have the permission `Kick Members`, which I need for this command.")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(":x: Hey! You dont have permissions! In the words of our great Robbie Rotten, **WHAT ARE YOU DOING?!**")
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(":x: This command is marked for servers only, and will not work in a DM!")

    @commands.command(description = "Bans the given <target> with reason <reason>, deleteing all messages sent from that user over the last <deletedays> days (must be an integer betweeen and including 0 and 7). Ensure that both the command invoker and the bot have the permission 'Ban Members'. Also DMs <target> to let them know they've been banned.")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members = True)
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, target:discord.Member, deletedays: int, reason: str):
        """(GUILD ONLY) Ban someone. See 's!help ban' for more info."""

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
                                    await ctx.guild.ban(target, delete_message_days = deletedays, reason = reason)
                                    await ctx.send(":boom: **INSTA BAN!** Swung the ban hammer on {0.mention}.".format(target))
                                    await target.send("Looks like you were banned from `{0.guild}`, {1.mention}. :slight_frown:".format(ctx, target))
                                except Exception:
                                    await ctx.send(":x: Oh noes! It didn't work! I may have ran into ratelimits, or some unknown error may have occured.")
                            else:
                                await ctx.send("Oops! You specified an out-of-range integer for <deletedays>! See `s!help ban` for info on limits.")
                        else:
                            await ctx.send(":x: Oops! That member has a higher or equal top role to me, meaning I can't ban him/her!")

    @ban.error
    async def banerr(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(":x: I don't have the permission to `Ban Members`!")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(":x: Hey! You don't have the right permissions!")
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(":x: This command is marked for servers only, and will not work in a DM!")

    @commands.command(description = "Unbans the given <target>. The target must be banned from the given server, and both the command invoker and the bot must have the permission 'Ban Members'. <target> will be DM'd once they are unbanned.")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members = True)
    @commands.has_permissions(ban_members = True)

    async def unban(self, ctx, target: discord.User):
        """(GUILD ONLY) Unbans someone. See `s!help unban` for more info."""

        targetBanned = False
        async for ban in await ctx.guild.bans():
            if ban[0] == target:
                targetBanned = True
        if targetBanned:
            try:
                await ctx.guild.unban(target)
                await ctx.send("<:suprKewl:508479728613851136> Unbanned!")
                await target.send(":thumbs_up: You've been unbanned from {}! If you still have a valid invite, you can use it to rejoin.".format(messageGuild.name))
            except Exception:
                await msg.edit(content = "{0.mention} :x: Oops! Looks like I couldn't unban {1.name}#{1.discriminator}! Perhaps I crashed into a rate-limit or tripped on another unknown error. Perhaps try again?".format(invoker, target))
        else:
            await msg.edit(content = "{0.mention} :x: Oops! That user ain't banned! Perhaps you meant someone else?".format(invoker))

    @unban.error
    async def unbanerr(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(":x: I don't have permission to `Ban Members`, meaning I also can't unban them!")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(":x: Hey! You don't have permissions!")
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(":x: This command is marked for servers only, and will not work in a DM!")

    @commands.command(description = "Gives the list of banned users for this server. Both the command invoker and the bot must have the permission `Ban Members`.")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members = True)
    @commands.has_permissions(ban_members = True)
    async def banlist(self, ctx):
        """(GUILD ONLY) Gives a list of banned users."""

        emb = discord.Embed()
        emb.set_author(name = 'Me', icon_url = self.bot.user.avatar_url)
        list = []
        banlist = await ctx.guild.bans()
        for ban in banlist:
            list.append(ban[0].name + "#" + ban[0].discriminator)
        commaspace = ", "
        msg = commaspace.join(list)
        emb.add_field(name = "Banned users for {0.name}".format(ctx.guild), value = msg)

        await ctx.send(embed = emb)

    @banlist.error
    async def banlisterr(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(":x: With out the permission to `Ban Members`, I can't get a banlist!")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(":x: Hey! You don't have permissions!")
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(":x: This command is marked for servers only, and will not work in a DM!")

def setup(bot):
    bot.add_cog(Moderation(bot))
