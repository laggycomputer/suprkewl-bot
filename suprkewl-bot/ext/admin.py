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


def setup(bot):
    bot.add_cog(Admin())
