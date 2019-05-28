# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 laggycomputer

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

import asyncio
import contextlib
import io
import math
import os
import random
import re

import discord
from discord.ext import commands
import gtts


class Fighter:
    def __init__(self, user):
        self.user = user
        self.health = 100
        self.turn = False
        self.won = False
        self.blocking = False


class FighterData:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2


class Fun(commands.Cog):

    @commands.command(
        description="A bunch of lenny faces."
    )
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def lenny(self, ctx):
        """( ͡° ͜ʖ ͡°) """

        msg = """**LENNY FACES**
Regular:( ͡° ͜ʖ ͡°)
Eyebrow Lenny: ( ͠° ͜ʖ ͡°)
chienese lenny: （͡°͜ʖ͡°）
TAKE THAT: ( ͡0 ͜ʖ ͡ 0)----@-
The generic tf2 pyro lenny:( ͡w ͜+ ͡m1)
2long4u:( ͡0 ͜ʖ ͡ 0)
Confused:( ͠° ͟ʖ ͡°)
Jew Lenny: (͡ ͡° ͜ つ ͡͡°)
Strong:ᕦ( ͡° ͜ʖ ͡°)ᕤ
The Mino Lenny: ˙͜>˙
Nazi Lenny: ( ͡卐 ͜ʖ ͡卐)
Cat Lenny:( ͡° ᴥ ͡°)
Praise the sun!: [T]/﻿
Dorito Lenny: ( ͡V ͜ʖ ͡V )
Wink:( ͡~ ͜ʖ ͡°)
swiggity swootey:( ͡o ͜ʖ ͡o)
ynneL:( ͜。 ͡ʖ ͜。)﻿
Wink 2: ͡° ͜ʖ ͡ -
I see u:( ͡͡ ° ͜ ʖ ͡ °)﻿
Alien:( ͡ ͡° ͡° ʖ ͡° ͡°)
U WOT M8:(ง ͠° ͟ل͜ ͡°)ง
Lenny Gang: ( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)
dErP:( ͡° ͜ʖ ͡ °)
Kitty?:(ʖ ͜° ͜ʖ)
monster lenny: ( ͜。 ͡ʖ ͡O)
Square:[ ͡° ͜ʖ ͡°]
Raise Your Donger:ヽ༼ຈل͜ຈ༽ﾉ
Imposter:{ ͡• ͜ʖ ͡•}
Voldemort:( ͡° ͜V ͡°)
Happy:( ͡^ ͜ʖ ͡^)
Satisfied:( ‾ʖ̫‾)
Sensei dong:( ͡°╭͜ʖ╮͡° )
Sensei doing Dong dong woo:ᕦ( ͡°╭͜ʖ╮͡° )ᕤ
Donger bill:[̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅]
Spider lenny://( ͡°͡° ͜ʖ ͡°͡°)/\
The noseless lenny:( ͡° ͜ ͡°)
Cool lenny: (⌐■_■)
Cheeky Lenny:: (͡o‿O͡)
Arrow Lenny: ⤜( ͠° ͜ʖ °)⤏
Table Lenny: (╯°□°)╯︵ ┻━┻
cONFUSED lenny乁( ⁰͡ Ĺ̯ ⁰͡ ) ㄏ
nazi lennys: ( ͡° ͜ʖ ͡°)/ ( ͡° ͜ʖ ͡°)/ ( ͡° ͜ʖ ͡°)/ ( ͡° ͜ʖ ͡°)/ 卐卐卐
Oh hay: (◕ ◡ ◕)
Manly Lenny: ᕦ( ͡͡~͜ʖ ͡° )ᕤ
Put ur dongers up or I'll shoot:(ง ͡° ͜ʖ ͡°)=/̵͇̿/'̿'̿̿̿ ̿ ̿̿
Badass Lenny: ̿ ̿'̿'̵͇̿з=(⌐■ʖ■)=ε/̵͇̿/'̿̿ ̿
"""
        sent = await ctx.send(msg)
        await ctx.register_response(sent)

    @commands.command(description="LMAO! Has a 5-second channel cooldown to keep things calm.")
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def lmao(self, ctx):
        """A nice and long lmao"""
        msg = """
L
    M
        A
          O
            o
           o
          o
         。
        。
       ."""

        sent = await ctx.send(msg)
        await ctx.register_response(sent)

    @commands.command(
        description="Make the bot say something. Watch what you say. Has a 5 second user cooldown."
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx, *, message: str):
        """Make the bot say something."""

        sent = await ctx.send(f"{ctx.author.mention} wants me to say '{message}'")
        await ctx.register_response(sent)

    @commands.command(aliases=["burn"])
    async def roast(self, ctx, *, target: discord.Member):
        """Roast someone. ⌐■_■"""

        roasts = [
            f"You spend your time on this thingy {target.mention}? I bet you don't even know what it does. By the way,"
            f" can you even read this?",
            f"{target.mention}, I fart to make you smell better.",
            f"{target.mention}, Your parents hated you so much your bath toys were an iron and a toaster. ~~go commit"
            f" toaster bath~~",
            f"{target.mention}, Why don't you check eBay and see if they have a life for sale?",
            f"{target.mention}, You bring everyone a lot of joy, when you leave the room.",
            f"{target.mention}, you're as bright as a black hole, and twice as dense.",
            f"{target.mention}, what'll you do to get a face after that baboon wants his face back?",
            f"{target.mention}, I don't exactly hate you, but if you were on fire and I had water, I'd drink the"
            f" water.",
            f"{target.mention}, I'll never forget the first time we met, although I'll keep trying.",
            f"{target.mention}, I don't I can think of an insult bad enough for you.",
            f"{target.mention}, There are more calories in your stomach than in the local supermarket!",
            f"{target.mention}, You shouldn't play hide and seek, no one would look for you.",
            f"{target.mention}, If I gave you a penny for your thoughts, I'd get change.",
            f"{target.mention}, So you've changed your mind, does this one work any better?",
            f"{target.mention}, You're so ugly, when your mom dropped you off at school she got a fine for littering.",
            f"{target.mention}, You're so fat the only letters of the alphabet you know are KFC.",
            f"I don't forget a single face, but in your case, {target.mention}, I'll make an exception."
        ]

        sent = await ctx.send(random.choice(roasts))
        await ctx.register_response(sent)

    @commands.command(aliases=["card"], description="Draw from a standard, 52-card deck, no jokers.")
    async def draw(self, ctx):
        """Draw a card"""

        suits = [":spades:", ":diamonds:", ":hearts:", ":clubs:"]

        ranks = [
            "Ace", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:",
            ":eight:", ":nine:", ":keycap_ten:", "Jack", "Queen", "King"
        ]

        sent = await ctx.send(f"I drew the {random.choice(ranks)} of {random.choice(suits)}")
        await ctx.register_response(sent)

    @commands.command(aliases=["flip", "quarter", "dime", "penny", "nickel"])
    async def coin(self, ctx):
        """Flip a coin"""

        msg = await ctx.send("My robot hand flips the coin.")
        await asyncio.sleep(1)

        await msg.edit(content="I slap the coin down on my robot arm.")
        await asyncio.sleep(0.5)

        if random.randint(1, 2) == 1:
            await msg.edit(content="It's heads!")
        else:
            await msg.edit(content="It's tails.")

        await ctx.register_response(msg)

    @commands.command(
        aliases=["rockpaperscissors"],
        description="Rock paper scissors. Randomizes a choice for you and the computer."
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def rps(self, ctx):
        """Rock, Paper, Scissors, Shoot!"""

        choices = [":fist:", ":newspaper:", ":scissors:"]

        computer = random.choice(choices)
        user = random.choice(choices)
        winner = None
        winmsg = " Congrats! :slight_smile:"
        losemsg = " Better luck next time... :slight_frown:"

        content = f"{ctx.author.mention} "

        if user == computer:
            content += f"We both got {computer}. Tie!"
        else:
            if user == ":fist:":
                if computer == ":scissors:":
                    content += f"Your {user} smashed my {computer}!"
                    winner = "usr"
                else:
                    content += f"My {computer} wrapped your {user}!"
                    winner = "comp"

            elif user == ":newspaper:":
                if computer == ":fist:":
                    content += f" Your {user} wrapped my {computer}!"
                    winner = "usr"
                else:
                    content += f"My {computer} cut your {user}!"
                    winner = "comp"

            elif user == ":scissors:":
                if computer == ":newspaper:":
                    content += f"Your {user} cut my {computer}!"
                    winner = "usr"
                else:
                    content += f"My {computer} smashed your {user}!"
                    winner = "comp"

        if winner == "usr":
            content += winmsg
        elif winner == "comp":
            content += losemsg
            await asyncio.sleep(2)
            msg = await ctx.send(f"{ctx.author.mention} :fist: Rock...")
            await ctx.register_response(msg)
            await asyncio.sleep(1)

            await msg.edit(content=f"{ctx.author.mention} :newspaper: Paper...")
            await asyncio.sleep(1)
            await msg.edit(content=f"{ctx.author.mention} :scissors: Scissors...")
            await asyncio.sleep(1)

            await msg.edit(content=f"{ctx.author.mention} :gun: Shoot! :boom:")
            await asyncio.sleep(0.5)

            await msg.edit(content=content)

    @commands.group(
        aliases=["roll"],
        description="Rolls the dice specified, in AdB format. For example, 'dice 3d6' would roll 3 six-sided dice.",
        invoke_without_subcommand=True
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dice(self, ctx, *, dice: str):
        """Now you can roll 1000-sided dice!"""

        if dice == "info":
            await self.dice_info.invoke(ctx)
            return

        async with ctx.channel.typing():
            await asyncio.sleep(1)
        msg = await ctx.send("thinking... :thinking:")
        await asyncio.sleep(1)
        try:
            count, limit = map(int, dice.split("d"))
        except ValueError:
            await msg.edit(
                content=f":x: Your input must be of the form `AdB`! Please check `{ctx.prefix}{ctx.invoked_with}"
                f" info` for more info."
            )
            await ctx.register_response(msg)
            return

        if 1000 >= count > 0 and 1000 >= limit > 0:

            rolls = []
            total = 0

            await msg.edit(content=":game_die: Rollling dice at the speed of sound...")
            await asyncio.sleep(1)
            await msg.edit(content="*A sonic :boom: echoes in the background*")
            await asyncio.sleep(1)

            for i in range(0, count):
                result = random.randint(1, limit)
                rolls.append(str(result))
                total += result

            avg = total / count
            avg = round(avg, 8)

            content = f":game_die: {', '.join(rolls)}. The total was {total}, and the average (mean) was {avg}."

            if len(content) > 2000:
                # Yes, this is blocking, but given current limits responses are almost always ~4000 characters max.
                file_content = "Rolls: {0}Total: {2}{1}Average:{3}".format(
                    "\n".join(rolls), "\n", total, avg)
                fp = io.BytesIO(file_content.encode("utf-8"))
                sent = (await ctx.send(
                    content=":white_check_mark: Your output was longer than 2000 characters and was therefore placed"
                            " in this file:",
                    file=discord.File(fp, "rolls.txt")
                ))
                await ctx.register_response(sent)

            else:
                await msg.edit(content=content)
                await ctx.register_response(msg)
        else:
            await msg.edit(
                content=f"Your syntax was correct, however one of your arguments were invalid. See"
                f" `{ctx.prefix}{ctx.invoked_with} info.`"
            )
            await ctx.register_response(msg)

    @dice.command(description="Show info for dice command.", name="info")
    async def dice_info(self, ctx):
        sent = (await ctx.send(
            "Your argument must be of the form AdB, where A is the number of dice to roll and B is the number of sides"
            " on each die. A and B must be positive integers between 1 and 1000."
        ))
        await ctx.register_response(sent)

    @commands.command(
        aliases=["pick", "rand"],
        description="The tiebreaker of all tiebreakers."
    )
    @commands.cooldown(2, 1, commands.BucketType.channel)
    async def choose(self, ctx, *choices: str):
        """Choose between given choices"""

        message = f"{ctx.author.mention}, I choose '"
        message += random.choice(choices) + "'."

        sent = await ctx.send(message)
        await ctx.register_response(sent)

    @commands.command(
        description="Starts a fight between the command invoker and the specified <target>."
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def fight(self, ctx, target: discord.Member):
        """FIGHT"""

        # Yes, this entire command is an eyesore. I'll get to it. Soon.
        if target.bot:
            sent = await ctx.send(
                ":x: Oops! You can't fight a robot; it's robot arms will annihilate you! Perhaps you meant a human?"
            )
            await ctx.register_response(sent)
            return
        if target == ctx.author:
            sent = await ctx.send(":x: You can't fight yourself!")
            await ctx.register_response(sent)
            return
        if (await ctx.bot.redis.exists(f"{ctx.author.id}:fighting")):
            emb = discord.Embed(
                color=ctx.bot.embed_color,
                description=f"{ctx.author.mention} :x: You can't fight multiple people at once! You're not Bruce Lee."
            )
            fp = discord.File("../assets/brucelee.gif", "image.gif")
            emb.set_image(
                url="attachment://image.gif"
            )
            emb.set_thumbnail(url=ctx.guild.me.avatar_url)
            emb.set_author(
                name=ctx.guild.me.name,
                icon_url=ctx.guild.me.avatar_url
            )
            emb.set_footer(
                text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            sent = await ctx.send(embed=emb, file=fp)
            await ctx.register_response(sent)

            return
        if (await ctx.bot.redis.exists(f"{target.id}:fighting")):
            emb = discord.Embed(
                color=ctx.bot.embed_color,
                description=f"{ctx.author.mention} :x: Don't make {target.mention} fight multiple people at once!"
                f" They're not Bruce Lee."
            )
            fp = discord.File("../assets/brucelee.gif", "image.gif")
            emb.set_image(
                url="attachment://image.gif"
            )
            emb.set_thumbnail(url=ctx.guild.me.avatar_url)
            emb.set_author(
                name=ctx.guild.me.name,
                icon_url=ctx.guild.me.avatar_url
            )
            emb.set_footer(
                text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            sent = await ctx.send(embed=emb, file=fp)
            await ctx.register_response(sent)

            return
        await ctx.bot.redis.execute("SET", f"{ctx.author.id}:fighting", "fighting")
        await ctx.bot.redis.execute("SET", f"{target.id}:fighting", "fighting")

        await ctx.send(":white_check_mark: Starting fight...")

        async with ctx.channel.typing():
            await asyncio.sleep(1)
            current_footer = ctx.bot.embed_footer

            p1 = Fighter(ctx.author)
            p2 = Fighter(target)

            def find_turn():
                if p1.turn:
                    return p1
                elif p2.turn:
                    return p2
                else:
                    return None

            def find_not_turn():
                if p1.turn:
                    return p2
                if p2.turn:
                    return p1
                else:
                    return None

            def findwin():
                if p1.won:
                    return p1
                elif p2.won:
                    return p2
                else:
                    return None

            def findloser():
                if p1.won:
                    return p2
                elif p2.won:
                    return p1
                else:
                    return None

            def switchturn():
                p1.turn = not p1.turn
                p2.turn = not p2.turn
                p1.blocking = False
                p2.blocking = False

            currentaction = ""
            damage = 0
            sent = None

            fightplaces = [
                "Laundry Room", "Dining Room", "Kitchen", "Bedroom", "Living Room", "Backyard"
            ]
            fightactions = {
                "Laundry Room": [
                    "{0.mention} whips {1.mention} with a freshly washed towel",
                    "{0.mention} shuts {1.mention} in the washer, but {1.mention} narrowly escapes",
                    "{0.mention} throws a tennis ball from inside the clothes dryer at {1.mention}"
                ],
                "Dining Room": [
                    "{0.mention} throws a plate at {1.mention}",
                    "{0.mention} stabs {1.mention} with a piece of a broken vase",
                    "{0.mention} pins {1.mention} against the wall with the table"
                ],
                "Kitchen": [
                    "{0.mention} cuts {1.mention} with a a knife",
                    "{0.mention} pours some boiling water on {1.mention}",
                    "{0.mention} hits {1.mention} with a pot"
                ],
                "Bedroom": [
                    "{0.mention} hits {1.mention} with a pillow",
                    "{1.mention} takes a pillow to the head from {0.mention}"
                ],
                "Living Room": [
                    "{0.mention} hits {1.mention} with the TV remote",
                    "{0.mention} uses the Wii controller as a club on {1.mention} *wii sports plays*",
                    "{1.mention} trips over the Skyrim CD sleeve, 00f"
                ],
                "Backyard": [
                    "{0.mention} hits {1.mention} with some tongs",
                    "{0.mention} turns the backyard stove over on {1.mention}"
                ]
            }
            universalactions = [
                "{0.mention} slugs {1.mention} in the face",
                "{0.mention} uses *sicc* karate skills on {1.mention}",
                "{0.mention} pushes {1.mention} over"
            ]
            deathblows = {
                "Laundry Room": "{0.mention} shuts {1.mention} in the washer and starts it",
                "Dining Room": "{0.mention} pins {1.mention} agianst the table",
                "Kitchen": "{0.mention} uses top-notch ninja skills on {1.mention}, many of which involve the knives",
                "Bedroom": "{0.mention} gets a l33t hit om {1.mention} involving throwing the bedstand",
                "Living Room": "{0.mention} narrowly beats {1.mention} in a sword-fight using the Dolby 7:1 surround"
                               " speakers",
                "Backyard": "{0.mention} throws some hot coals from the backyard stove at {1.mention}"
            }

            connectedrooms = {
                "Laundry Room": ["Backyard", "Kitchen"], "Dining Room": ["Kitchen", "Backyard"],
                "Kitchen": ["Dining Room", "Living Room"], "Bedroom": ["Living Room"],
                "Living Room": ["Kitchen", "Bedroom"], "Backyard": ["Laundry Room", "Laundry Room"]
            }

            setting = random.choice(fightplaces)

            p1.turn = True

        while p1.health > 0 and p2.health > 0:
            askaction = await ctx.send(
                f"{find_turn().user.mention}, what do you want to do? `hit`, `run`, `block`, or `end`."
            )

            def check(m):
                if m.channel == ctx.channel and m.author == find_turn().user:
                    return m.content.lower().startswith("hit") or m.content.lower().startswith("run")\
                        or m.content.lower().startswith("block") or m.content.lower().startswith("end")
                else:
                    return False

            usrinput = await ctx.bot.wait_for("message", check=check)

            if usrinput is None:
                await ctx.send("it timed out noobs")
                return
            else:

                if usrinput.content.lower().startswith("block"):
                    currentaction = f"{find_turn().user.mention} is bloccing"
                    find_turn().blocking = True

                elif usrinput.content.lower().startswith("hit"):
                    damage = 0
                    rand = random.randint(1, 15)
                    if rand == 1:
                        blow = deathblows[setting].format(
                            find_turn().user, find_not_turn().user)
                        blow += " (DEATHBLOW)"
                        damage = 100

                    elif rand > 9:
                        blow = random.choice(universalactions).format(
                            find_turn().user, find_not_turn().user)
                        damage = random.randint(1, 50)

                    else:
                        blow = random.choice(fightactions[setting]).format(
                            find_turn().user, find_not_turn().user)
                        damage = random.randint(1, 50)

                    if find_not_turn().blocking:
                        rand = random.randint(0, 5)
                        if rand:
                            damage = math.floor(damage / 2)

                    blow += f" ({damage} dmg)"

                    if find_not_turn().blocking:
                        if rand:
                            blow += f", and {find_not_turn().user.mention} blocked successfully! Half damage."
                        else:
                            blow += f", and {find_not_turn().user.mention} failed to blocc!"

                    currentaction = blow

                elif usrinput.content.lower().startswith("run"):
                    newsetting = random.choice(connectedrooms[setting])

                    currentaction = f"{find_turn().user.mention} kicks {find_not_turn().user.mention} in the" \
                        f" shins and runs as fast as he/she can out of the {setting} and into the" \
                        f" {newsetting}. {find_turn().user.mention} gives chase."

                    setting = newsetting

                elif usrinput.content.lower().startswith("end"):
                    await ctx.send(
                        f"{find_turn().user.mention} and {find_not_turn().user.mention} get friendly and the fight's"
                        f" over."
                    )
                    await ctx.bot.redis.delete(f"{ctx.author.id}:fighting", f"{target.id}:fighting")
                    return

                find_not_turn().health -= damage
                if find_not_turn().health < 0:
                    find_not_turn().health = 0

                emb = discord.Embed(
                    name="FIGHT", color=find_turn().user.colour)

                emb.add_field(name=f"Player 1 ({ctx.author}) health", value=f"**{p1.health}**")
                emb.add_field(name=f"Player 2 ({target}) health", value=f"**{p2.health}**")
                emb.add_field(name="Current Setting", value=f"`{setting}`")
                emb.add_field(name="Current action", value=currentaction)

                emb.set_thumbnail(url=ctx.bot.user.avatar_url)
                emb.set_author(name=ctx.bot.user.name,
                               icon_url=ctx.bot.user.avatar_url)
                emb.set_footer(
                    text=f"{current_footer} Requested by {ctx.author}",
                    icon_url=ctx.author.avatar_url
                )

                if sent is None:
                    sent = await ctx.send(embed=emb)
                    await ctx.register_response(sent)
                else:
                    await sent.edit(embed=emb)

                try:
                    await askaction.delete()
                    await usrinput.delete()
                except discord.Forbidden or discord.NotFound:
                    pass

                switchturn()

        if p1.health == 0:
            p2.won = True
            p1.won = False
        else:
            p2.won = False
            p1.won = True

        win_mention = findwin().user.mention
        lose_mention = findloser().user.mention
        await sent.delete()

        sent = await ctx.send(
            f"Looks like {win_mention} defeated {lose_mention} with {findwin().health} health left!"
        )

        await ctx.bot.redis.delete(f"{ctx.author.id}:fighting", f"{target.id}:fighting")
        await ctx.register_response(sent)

    @commands.group(description="Gets an xkcd comic.", invoke_without_command=True)
    @commands.cooldown(1, 3, commands.BucketType.channel)
    async def xkcd(self, ctx, arg: int = None):
        if arg is None:
            await self.xkcd_latest(ctx)
        else:
            if arg <= 0:
                sent = await ctx.send(":x: Invalid comic number.")
                await ctx.register_response(sent)
                return

            await self.xkcd_get(ctx, arg)

    async def xkcd_get(self, ctx, number):
        async with ctx.bot.http2.get(f"https://xkcd.com/{number}/info.0.json") as resp:
            if resp.status == 404:
                sent = await ctx.send(":x: Comic not found!")
                await ctx.register_response(sent)
                return
            text = await resp.json()

        emb = discord.Embed(
            color=ctx.bot.embed_color,
            description=f"Here you are! xkcd comic #{number}. Credits to [xkcd](https://xkcd.com/{number})."
        )
        emb.set_image(url=text["img"])

        emb.set_author(name=ctx.bot.user.name,
                       icon_url=ctx.bot.user.avatar_url)
        emb.set_footer(
            text=f"{ctx.bot.embed_footer} Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )

        sent = await ctx.send(embed=emb)
        await ctx.register_response(sent)

    @xkcd.command(name="random", aliases=["rand"], description="Get a random xkcd comic.")
    async def xkcd_random(self, ctx):
        if not ctx.command.parent.can_run(ctx):
            return

        async with ctx.bot.http2.get("https://xkcd.com/info.0.json") as resp:
            text = await resp.json()
        latest_comic = text["num"]

        comic_to_get = random.randint(0, int(latest_comic))

        async with ctx.bot.http2.get(f"https://xkcd.com/{comic_to_get}/info.0.json") as resp:
            text = await resp.json()

        emb = discord.Embed(
            color=ctx.bot.embed_color,
            description=f"Here you are! xkcd comic #{comic_to_get}. Credits to [xkcd](https://xkcd.com/{comic_to_get})."
        )
        emb.set_image(url=text["img"])

        emb.set_author(
            name=ctx.bot.user.name,
            icon_url=ctx.bot.user.avatar_url
        )
        emb.set_footer(
            text=f"{ctx.bot.embed_footer} Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )

        sent = await ctx.send(embed=emb)
        await ctx.register_response(sent)

    async def xkcd_latest(self, ctx):
        async with ctx.bot.http2.get("https://xkcd.com/info.0.json") as resp:
            text = await resp.json()

        num = text["num"]

        emb = discord.Embed(
            color=ctx.bot.embed_color,
            description=f"Here you are! xkcd comic #{num}. Credits to [xkcd](https://xkcd.com/{num})."
        )
        emb.set_image(url=text["img"])

        emb.set_author(
            name=ctx.bot.user.name,
            icon_url=ctx.bot.user.avatar_url
        )
        emb.set_footer(
            text=f"{ctx.bot.embed_footer} Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )

        sent = await ctx.send(embed=emb)
        await ctx.register_response(sent)

    @commands.command(
        description="Reacts with a sheep emoji to sheep-related messages. Send 's!stop' to end the sheepiness."
    )
    async def sheep(self, ctx):
        """React to messages with a sheep emoji."""

        if not (await ctx.bot.redis.exists(f"{ctx.channel.id}:sheep")):
            await ctx.bot.redis.execute("SET", f"{ctx.channel.id}:sheep", "baa")
            m = ctx.message

            with contextlib.suppress(discord.HTTPException):
                await m.add_reaction("\U0001F411")

            while True:
                m = await ctx.bot.wait_for("message", check=lambda m: m.channel == ctx.channel, timeout=300)
                if m is None:
                    break
                if m.content.lower().startswith("s!stop") and m.author == ctx.author:
                    break
                if any(i in m.content.lower() for i in ["sheep", "shep", "🐑", "ba", "wool"]):
                    with contextlib.suppress(discord.HTTPException):
                        await m.add_reaction("\U0001F411")

            await ctx.bot.redis.delete(f"{ctx.channel.id}:sheep")

            sent = await ctx.send(":white_check_mark: Done.")
            await ctx.register_response(sent)
        else:
            sent = await ctx.send(
                ":x: Don't run this command twice in the same channel! Use `s!stop` to stop this command."
            )
            await ctx.register_response(sent)

    @commands.command(
        description="Reacts with a duck emoji to duck-related messages. Send 's!stop' to end the quackery."
    )
    async def duck(self, ctx):
        """React to messages with a duck emoji."""

        if not (await ctx.bot.redis.exists(f"{ctx.channel.id}:duck")):
            await ctx.bot.redis.execute("SET", f"{ctx.channel.id}:duck", "kwack")
            m = ctx.message

            await m.add_reaction("\U0001F986")

            pattern = re.compile("(kw|qu)a+c+k?")

            while True:
                m = await ctx.bot.wait_for("message", check=lambda m: m.channel == ctx.channel, timeout=300)
                if m is None:
                    break
                if m.content.lower().startswith("s!stop") and m.author == ctx.author:
                    break
                r = re.search(pattern, m.content.lower())
                if any(i in m.content.lower() for i in ["duck", "duk", "🦆", "ducc"]) or r:
                    await m.add_reaction("\U0001F986")

            await ctx.bot.redis.delete(f"{ctx.channel.id}:duck")

            sent = await ctx.send(":white_check_mark: Done.")
            await ctx.register_response(sent)
        else:
            sent = await ctx.send(
                ":x: Don't run this command twice in the same channel! Use `s!stop` to stop this command."
            )
            await ctx.register_response(sent)

    @commands.command(
        description="Reacts with a dog emoji to dog-related messages. Send 's!stop' to end the borkiness."
    )
    async def dog(self, ctx):
        """React to messages with a dog emoji."""

        if not (await ctx.bot.redis.exists(f"{ctx.channel.id}:dog")):
            await ctx.bot.redis.execute("SET", f"{ctx.channel.id}:dog", "bork")
            m = ctx.message

            with contextlib.suppress(discord.HTTPException):
                await m.add_reaction("\U0001f436")

            patterns = [re.compile("b[oa]+r+[ck]+"), re.compile("w+o+f+"),
                        re.compile("a+r+f+"), re.compile("do+g+e?o?")]

            while True:
                m = await ctx.bot.wait_for("message", check=lambda m: m.channel == ctx.channel, timeout=300)
                if m is None:
                    break
                if m.content.lower().startswith("s!stop") and m.author == ctx.author:
                    break
                r = any(re.search(p, m.content.lower()) is not None for p in patterns)
                if r:
                    with contextlib.suppress(discord.HTTPException):
                        await m.add_reaction("\U0001f436")

            await ctx.bot.redis.delete(f"{ctx.channel.id}:dog")

            sent = await ctx.send(":white_check_mark: Done.")
            await ctx.register_response(sent)
        else:
            sent = await ctx.send(
                ":x: Don't run this command twice in the same channel! Use `s!stop` to stop this command."
            )
            await ctx.register_response(sent)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def tts(self, ctx, *, message):
        """Make me speak a message."""

        async with ctx.typing():
            try:
                tts = gtts.gTTS(text=message)
            except AssertionError:
                sent = await ctx.send(":x: There was nothing speakable in that message.")
                return await ctx.register_response(sent)

            # The actual request happens here:
            def save():
                fname = f"{ctx.message.id}.mp3"
                tts.save(fname)  # This uses requests, and has to wait for all of the sound output to be streamed.
                fp = discord.File(fname, "out.mp3")
                return [fname, fp]

            fname, fp = await ctx.bot.loop.run_in_executor(None, save)

        sent = await ctx.send(":white_check_mark:", file=fp)
        await ctx.register_response(sent)

        os.remove(fname)

    # From spoo.py
    @commands.command()
    async def star(self, ctx, *, msg):
        """Create a star out of a string 1-25 characters long."""

        if len(msg) > 25:
            sent = await ctx.send("Your message must be shorter than 25 characters.")
            return await ctx.register_response(sent)
        elif len(msg) == 0:
            sent = await ctx.send("Your message must have at least 1 character.")
            return await ctx.register_response(sent)

        ret = "```\n"

        mid = len(msg) - 1

        for i in range(len(msg) * 2 - 1):
            if (mid == i):
                ret += msg[::-1] + msg[1:] + "\n"
            else:
                let = abs(mid - i)
                ret += " " * (mid - let)
                ret += msg[let]
                ret += " " * (let - 1)
                ret += msg[let]
                ret += " " * (let - 1)
                ret += msg[let]
                ret += "\n"

        ret += "```"
        sent = await ctx.send(ret)
        await ctx.register_response(sent)


def setup(bot):
    bot.add_cog(Fun())
