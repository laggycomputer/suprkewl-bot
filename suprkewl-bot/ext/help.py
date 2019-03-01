import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, specific=None):
        """Shows this message."""

        if specific:
            command = self.bot.get_command(specific)

            if command is None:
                await ctx.send(":x: Command not found!")
                return
            else:
                emb = discord.Embed(title=f"{ctx.prefix}{command.qualified_name}{', ' if any(command.aliases) else ''}{', '.join(command.aliases)}", description=command.short_doc, color=0xf92f2f)

                if isinstance(command, commands.GroupMixin):
                    for subcommand in command.commands:
                        emb.add_field(name=f"`{ctx.prefix}{subcommand.qualified_name}{', ' if any(subcommand.aliases) else ''}{', '.join(subcommand.aliases)}`", value=subcommand.short_doc + "\u200b")

        else:
            emb = discord.Embed(title="Help and Information", color=0xf92f2f)
            for name, command in self.bot.all_commands.items():
                if name in command.aliases or (command.hidden and not await self.bot.is_owner(ctx.author)):
                    continue
                emb.add_field(name=f"{name}{', ' if any(command.aliases) else ''}{', '.join(command.aliases)}", value=command.short_doc + "\u200b")

        emb.set_thumbnail(url=self.bot.user.avatar_url)
        emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        emb.set_footer(text=f"{self.bot.description} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=emb)

oldhelp = None

def setup(bot):
    oldhelp = bot.remove_command("help")
    bot.add_cog(Help(bot))

def teardown(bot):
    bot.add_command(oldhelp)
