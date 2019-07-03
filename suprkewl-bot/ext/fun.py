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

import asyncio
import contextlib
import io
import math
import random
import re

import discord
from discord.ext import commands


# C4 stuff from StarrFox/DiscordChan

c4_diagonal_data = [
    [(3, 0), (2, 1), (1, 2), (0, 3)],
    [(4, 0), (3, 1), (2, 2), (1, 3)],
    [(3, 1), (2, 2), (1, 3), (0, 4)],
    [(5, 0), (4, 1), (3, 2), (2, 3)],
    [(4, 1), (3, 2), (2, 3), (1, 4)],
    [(3, 2), (2, 3), (1, 4), (0, 5)],
    [(5, 1), (4, 2), (3, 3), (2, 4)],
    [(4, 2), (3, 3), (2, 4), (1, 5)],
    [(3, 3), (2, 4), (1, 5), (0, 6)],
    [(5, 2), (4, 3), (3, 4), (2, 5)],
    [(4, 3), (3, 4), (2, 5), (1, 6)],
    [(5, 3), (4, 4), (3, 5), (2, 6)],
    [(3, 6), (2, 5), (1, 4), (0, 3)],
    [(4, 6), (3, 5), (2, 4), (1, 3)],
    [(3, 5), (2, 4), (1, 3), (0, 2)],
    [(5, 6), (4, 5), (3, 4), (2, 3)],
    [(4, 5), (3, 4), (2, 3), (1, 2)],
    [(3, 4), (2, 3), (1, 2), (0, 1)],
    [(5, 5), (4, 4), (3, 3), (2, 2)],
    [(4, 4), (3, 3), (2, 2), (1, 1)],
    [(3, 3), (2, 2), (1, 1), (0, 0)],
    [(5, 4), (4, 3), (3, 2), (2, 1)],
    [(4, 3), (3, 2), (2, 1), (1, 0)],
    [(5, 3), (4, 2), (3, 1), (2, 0)]
]


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


class C4():

    def __init__(self, p1, p2, ctx):
        self.player_one = p1
        self.player_two = p2
        self.ctx = ctx
        self.red = "\N{LARGE RED CIRCLE}"
        self.blue = "\N{LARGE BLUE CIRCLE}"
        self.filler = "\N{BLACK LARGE SQUARE}"
        self.emojis = [str(i) + "\u20e3" for i in range(1, 8)]
        self.board = self.create_board()
        self.is_running = True
        self.message = None
        self.current_player = p1
        self.is_first_run = True
        self.last_play = None

    def phrase_board(self):
        return "\n".join(map("".join, self.board)) + "\n" + "".join(self.emojis)

    def create_board(self):
        return [[self.filler] * 7 for _ in range(6)]

    def make_embed(self, *, inverse=False):
        embed = discord.Embed(description=self.phrase_board())
        embed.add_field(
            name="Players:", value=f"{self.red}: {self.player_one.mention}\n{self.blue}: {self.player_two.mention}")
        if not self.is_first_run:
            if not inverse:
                embed.add_field(
                    name="Last move:", value=f"{self.current_player.mention}: {self.last_play + 1}", inline=False)
            else:
                if self.current_player == self.player_two:
                    dex = self.player_one.mention
                else:
                    dex = self.player_two.mention
                embed.add_field(name="Last move:", value=f"{dex}: {self.last_play + 1}", inline=False)
        if self.is_running:
            if self.is_first_run:
                embed.add_field(name="Current turn:", value=self.player_one.mention, inline=False)
            elif self.current_player == self.player_one and not inverse:
                embed.add_field(name="Current turn:", value=self.player_two.mention, inline=False)
            elif self.current_player == self.player_two and not inverse:
                embed.add_field(name="Current turn:", value=self.player_one.mention, inline=False)
            else:
                embed.add_field(name="Current turn:", value=self.current_player.mention, inline=False)
        else:
            embed.add_field(name="Winner:", value=self.current_player.mention, inline=False)
        return embed

    async def add_reactions(self):
        for r in self.emojis:
            await self.message.add_reaction(r)
        await self.message.add_reaction("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}")

    async def find_free(self, num):
        for i in range(6)[::-1]:
            if self.board[i][num] == self.filler:
                return i

    async def phrase_reaction(self, reaction):
        num = self.emojis.index(reaction)
        next = await self.find_free(num)
        if next is None:
            return
        self.board[next][num] = self.red if self.current_player == self.player_one else self.blue
        await self.check_wins()
        self.is_first_run = False
        self.last_play = num
        await self.message.edit(embed=self.make_embed())
        self.current_player = self.player_two if self.current_player == self.player_one else self.player_one

    async def check_wins(self):
        def check_slice(s):
            if s[0] == s[1] == s[2] == s[3] and s[0] != self.filler:
                return True
            else:
                return False
        for row in self.board:
            for i in range(4):
                if check_slice(row[i:i + 4]):
                    self.is_running = False
                    return
        columns = []
        for i in range(7):
            columns.append([self.board[q][i] for q in range(6)])
        for c in columns:
            for i in range(3):
                if check_slice(c[i:i + 4]):
                    self.is_running = False
                    return
        diagonals = []
        for c4_d in c4_diagonal_data:
            diagonals.append([self.board[i[0]][i[1]] for i in c4_d])
        for d in diagonals:
            if check_slice(d):
                self.is_running = False
                return

    async def do_game(self):
        self.message = await self.ctx.send(embed=self.make_embed())
        await self.add_reactions()
        while self.is_running:
            try:
                reaction, user = await self.ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda r, u: (
                        r.message.id == self.message.id
                        and u == self.current_player
                        and str(r) in self.emojis + ["\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}"]
                    ),
                    timeout=300
                )
            except asyncio.TimeoutError:
                await self.message.edit(content="Timed out due to inactivity.", embed=None)
                break
            with contextlib.suppress(discord.HTTPException):
                await reaction.remove(user)

            if str(reaction) == "\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}":
                await self.message.delete()
                self.message = await self.ctx.send(embed=self.make_embed(inverse=True))
                await self.add_reactions()
            else:
                await self.phrase_reaction(str(reaction))

        with contextlib.suppress(discord.HTTPException):
            await self.message.clear_reactions()


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
        await ctx.send(msg)

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

        await ctx.send(msg)

    @commands.command(
        description="Make the bot say something. Watch what you say. Has a 5 second user cooldown."
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx, *, message: str):
        """Make the bot say something."""

        await ctx.send(f"{ctx.author.mention} wants me to say '{message}'")

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

        await ctx.send(random.choice(roasts))

    @commands.command(aliases=["card"], description="Draw from a standard, 52-card deck, no jokers.")
    async def draw(self, ctx):
        """Draw a card"""

        suits = [":spades:", ":diamonds:", ":hearts:", ":clubs:"]

        ranks = [
            "Ace", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:",
            ":eight:", ":nine:", ":keycap_ten:", "Jack", "Queen", "King"
        ]

        await ctx.send(f"I drew the {random.choice(ranks)} of {random.choice(suits)}")

    @commands.command(aliases=["quarter", "dime", "penny", "nickel"])
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
        description="Rolls the dice specified, in AdB format. For example, `dice 3d6` would roll 3 six-sided dice.",
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
            return await msg.edit(
                content=f":x: Your input must be of the form `AdB`! Please check `{ctx.prefix}{ctx.invoked_with}"
                f" info` for more info."
            )

        if 1000 >= count > 0 and 1000 >= limit > 0:
            rolls = []
            total = 0

            await msg.edit(content=":game_die: Rolling dice at the speed of sound...")
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
                file_content = "Rolls: {1}{0}{1}Total: {2}{1}Average: {3}{1}".format(
                    "\n".join(rolls), "\n", total, avg)
                fp = io.BytesIO(file_content.encode("utf-8"))
                await ctx.send(
                    ":white_check_mark: Your output was longer than 2000 characters and was therefore placed in this"
                    " file:",
                    file=discord.File(fp, "rolls.txt")
                )

            else:
                await msg.edit(content=content)
        else:
            await msg.edit(
                content=f"Your syntax was correct, however one of your arguments were invalid. See"
                f" `{ctx.prefix}{ctx.invoked_with} info.`"
            )

    @dice.command(description="Show info for dice command.", name="info")
    async def dice_info(self, ctx):
        await ctx.send(
            "Your argument must be of the form AdB, where A is the number of dice to roll and B is the number of sides"
            " on each die. A and B must be positive integers between 1 and 1000."
        )

    @commands.command(
        aliases=["pick", "rand"],
        description="The tiebreaker of all tiebreakers."
    )
    @commands.cooldown(2, 1, commands.BucketType.channel)
    async def choose(self, ctx, *choices: str):
        """Choose between given choices"""

        message = f"{ctx.author.mention}, I choose '"
        message += random.choice(choices) + "'."

        await ctx.send(message)

    @commands.command(
        description="Starts a fight between the command invoker and the specified <target>."
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def fight(self, ctx, target: discord.Member):
        """FIGHT"""

        # Yes, this entire command is an eyesore. I'll get to it. Soon.
        if target.bot:
            return await ctx.send(
                ":x: Oops! You can't fight a robot; it's robot arms will annihilate you! Perhaps you meant a human?"
            )
        if target == ctx.author:
            return await ctx.send(":x: You can't fight yourself!")

        if (await ctx.bot.redis.exists(f"{ctx.author.id}:fighting")):
            emb = discord.Embed(
                color=ctx.bot.embed_color,
                description=f"{ctx.author.mention} :x: You can't fight multiple people at once! You're not Bruce Lee."
            )
            fp = discord.File("assets/brucelee.gif", "image.gif")
            emb.set_image(
                url="attachment://image.gif"
            )
            emb.set_thumbnail(url=ctx.me.avatar_url)
            emb.set_author(
                name=ctx.me.name,
                icon_url=ctx.me.avatar_url
            )
            emb.set_footer(
                text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            await ctx.send(embed=emb, file=fp)

            return
        if (await ctx.bot.redis.exists(f"{target.id}:fighting")):
            emb = discord.Embed(
                color=ctx.bot.embed_color,
                description=f"{ctx.author.mention} :x: Don't make {target.mention} fight multiple people at once!"
                f" They're not Bruce Lee."
            )
            fp = discord.File("assets/brucelee.gif", "image.gif")
            emb.set_image(
                url="attachment://image.gif"
            )
            emb.set_thumbnail(url=ctx.me.avatar_url)
            emb.set_author(
                name=ctx.me.name,
                icon_url=ctx.me.avatar_url
            )
            emb.set_footer(
                text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=emb, file=fp)

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
                    "{0.mention} body slams {1.mention}, who trips over the Skyrim CD sleeve, 00f"
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

            try:
                usrinput = await ctx.bot.wait_for("message", check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send("it timed out noobs")
                return await ctx.bot.redis.delete(f"{ctx.author.id}:fighting", f"{target.id}:fighting")

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
                return await ctx.bot.redis.delete(f"{ctx.author.id}:fighting", f"{target.id}:fighting")

            find_not_turn().health -= damage
            if find_not_turn().health < 0:
                find_not_turn().health = 0

            emb = discord.Embed(
                name="FIGHT", color=find_turn().user.colour)

            emb.add_field(name=f"Player 1 ({ctx.author}) health", value=f"**{p1.health}**")
            emb.add_field(name=f"Player 2 ({target}) health", value=f"**{p2.health}**")
            emb.add_field(name="Current Setting", value=f"`{setting}`")
            emb.add_field(name="Current action", value=currentaction)

            emb.set_thumbnail(url=ctx.me.avatar_url)
            emb.set_author(name=ctx.me.name,
                           icon_url=ctx.me.avatar_url)
            emb.set_footer(
                text=f"{current_footer} Requested by {ctx.author}",
                icon_url=ctx.author.avatar_url
            )

            if sent is None:
                await ctx.send(embed=emb)
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

        await ctx.send(
            f"Looks like {win_mention} defeated {lose_mention} with {findwin().health} health left!"
        )

        await ctx.bot.redis.delete(f"{ctx.author.id}:fighting", f"{target.id}:fighting")

    @commands.command(
        description="Reacts with a sheep emoji to sheep-related messages. Send `s!stop` to end the sheepiness."
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

            await ctx.send(":white_check_mark: Done.")
        else:
            await ctx.send(":x: Don't run this command twice in the same channel! Use `s!stop` to stop this command.")

    @commands.command(
        description="Reacts with a duck emoji to duck-related messages. Send `s!stop` to end the quackery."
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

            await ctx.send(":white_check_mark: Done.")
        else:
            await ctx.send(":x: Don't run this command twice in the same channel! Use `s!stop` to stop this command.")

    @commands.command(
        description="Reacts with a dog emoji to dog-related messages. Send `s!stop` to end the borkiness."
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

            await ctx.send(":white_check_mark: Done.")
        else:
            await ctx.send(":x: Don't run this command twice in the same channel! Use `s!stop` to stop this command.")

    # From spoo.py
    @commands.command()
    async def star(self, ctx, *, msg):
        """Create a star out of a string 1-25 characters long."""

        if len(msg) > 25:
            return await ctx.send("Your message must be shorter than 25 characters.")
        elif len(msg) == 0:
            return await ctx.send("Your message must have at least 1 character.")

        ret = "```\n"

        mid = len(msg) - 1

        for i in range(len(msg) * 2 - 1):
            if mid == i:
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
        await ctx.send(ret)

    @commands.command(aliases=["mcxp"])
    async def minecraftxp(self, ctx, *, percent: int):  # I don't do Minecraft. Thanks for reading.
        """Draw a Minecraft XP bar."""

        if percent < 0 or percent > 100:
            return await ctx.send(":x: Your argument must be an integer between 0 and 100.")

        data = {"percent": percent}

        async with ctx.bot.http2.get("https://cdn.welcomer.fun/minecraftxp", data=data) as resp:
            raw = await resp.content.read()

        fp = discord.File(io.BytesIO(raw), "xp.png")

        await ctx.send(file=fp)

    @commands.command(aliases=["mca"])
    async def minecraftachievement(self, ctx, *, text):
        """Generate a Minecraft achievement notification with your text."""

        async with ctx.typing():
            async with ctx.bot.http2.get(f"https://api.alexflipnote.dev/achievement?text={text}") as resp:
                raw = await resp.content.read()

        await ctx.send(file=discord.File(io.BytesIO(raw), "achieved.png"))

    @commands.command()
    async def supreme(self, ctx, *, text):
        """Draw a Supreme sticker with your text."""

        async with ctx.typing():
            async with ctx.bot.http2.get(f"https://api.alexflipnote.dev/supreme?text={text}") as resp:
                raw = await resp.content.read()

        await ctx.send(file=discord.File(io.BytesIO(raw), "supreme.png"))

    @commands.command(name="8ball", aliases=["8b"])
    async def _8ball(self, ctx, *, question):
        """The classic Magic 8 ball."""

        await ctx.send(random.choice([
            "It is certain.", "Without a doubt.", "You may rely on it.", "Yes, definitely.", "It is decidedly so.",
            "As I see it, yes.", "Most likely.", "Yes.", "Outlook good.", "Signs point to yes.",
            "Reply hazy try again.", "Better not tell you now.", "Ask again later.", "Cannot predict now.",
            "Concentrate and ask again.", "Don’t count on it.", "Outlook not so good.", "My sources say no.",
            "Very doubtful.", "My reply is no."
        ]))

    @commands.command()
    async def c4(self, ctx, *, member: discord.Member):
        """Play Connect4 with someone."""

        if member == ctx.author:
            return await ctx.send("You cannot play against yourself!")
        if member.bot:
            return await ctx.send("You can't play bots!")

        if (await ctx.bot.redis.exists(f"{ctx.author.id}:c4")):
            emb = discord.Embed(
                color=ctx.bot.embed_color,
                description=f"{ctx.author.mention} :x: You can't play multiple Connect4 games at once!"
            )
            emb.set_thumbnail(url=ctx.me.avatar_url)
            emb.set_author(
                name=ctx.me.name,
                icon_url=ctx.me.avatar_url
            )
            emb.set_footer(
                text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=emb)

        if (await ctx.bot.redis.exists(f"{member.id}:c4")):
            emb = discord.Embed(
                color=ctx.bot.embed_color,
                description=f"{ctx.author.mention} :x: {member.mention} is already in a Connect4 game."
            )

            emb.set_thumbnail(url=ctx.me.avatar_url)
            emb.set_author(
                name=ctx.me.name,
                icon_url=ctx.me.avatar_url
            )
            emb.set_footer(
                text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=emb)

        await ctx.bot.redis.execute("SET", f"{ctx.author.id}:c4", "c4")
        await ctx.bot.redis.execute("SET", f"{member.id}:c4", "c4")

        board = C4(ctx.author, member, ctx)
        await board.do_game()

        await ctx.bot.redis.delete(f"{ctx.author.id}:c4", f"{member.id}:c4")


def setup(bot):
    bot.add_cog(Fun())
