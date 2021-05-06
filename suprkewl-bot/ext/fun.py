# -*- coding: utf-8 -*-

"""
Copyright (C) 2021 Dante "laggycomputer" Dam

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
import os
import random
import re
import typing

import aiohttp
import discord
from discord.ext import commands

import config
from .utils import C4, Fighter, ImageEmbedinator, IsCustomBlacklisted, Mastermind, purge_from_list, Plural, roll_XdY
from .utils import use_potential_nickname


def custom_inspire_blacklist(ctx):
    if ctx.guild and ctx.guild.id == 707226419993772112:
        raise IsCustomBlacklisted
    return True


class Fun(commands.Cog):
    def __init__(self):
        self.latest_inspires = dict()
        self.uids_fighting = []
        self.channelids_sheeping = []
        self.channelids_ducking = []
        self.channelids_dogging = []
        self.uids_c4ing = []
        self.channelids_masterminding = []
        self.uids_masterminding = []

    @commands.command(
        description="A bunch of lenny faces."
    )
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def lenny(self, ctx):
        """( ͡° ͜ʖ ͡°) """

        msg = """**LENNY FACES**
Regular: ( ͡° ͜ʖ ͡°)
Eyebrow Lenny: ( ͠° ͜ʖ ͡°)
chienese lenny: （͡°͜ʖ͡°）
TAKE THAT: ( ͡0 ͜ʖ ͡ 0)----@-
The generic tf2 pyro lenny: ( ͡w ͜+ ͡m1)
2long4u: ( ͡0 ͜ʖ ͡ 0)
Confused: ( ͠° ͟ʖ ͡°)
Strong: ᕦ( ͡° ͜ʖ ͡°)ᕤ
The Mino Lenny: ˙͜>˙
Cat Lenny: ( ͡° ᴥ ͡°)
Praise the sun!: [T]/
Dorito Lenny: ( ͡V ͜ʖ ͡V )
Wink: ( ͡~ ͜ʖ ͡°)
swiggity swootey: ( ͡o ͜ʖ ͡o)
ynneL: ( ͜。 ͡ʖ ͜。)
Wink 2: ͡° ͜ʖ ͡ -
I see u: ( ͡͡ ° ͜ ʖ ͡ °)
Alien: ( ͡ ͡° ͡° ʖ ͡° ͡°)
U WOT M8:( ง ͠° ͟ل͜ ͡°)ง
Lenny Gang: ( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)
dErP: ( ͡° ͜ʖ ͡ °)
Kitty?: (ʖ ͜° ͜ʖ)
monster lenny: ( ͜。 ͡ʖ ͡O)
Square: [ ͡° ͜ʖ ͡°]
Raise Your Donger: ヽ༼ຈل͜ຈ༽ﾉ
Imposter: { ͡• ͜ʖ ͡•}
Voldemort: ( ͡° ͜V ͡°)
Happy: ( ͡^ ͜ʖ ͡^)
Satisfied: ( ‾ʖ̫‾)
Spider lenny: //( ͡°͡° ͜ʖ ͡°͡°)/\
The noseless lenny: ( ͡° ͜ ͡°)
Cool lenny: (⌐■_■)
Cheeky Lenny:: (͡o‿O͡)
Arrow Lenny: ⤜( ͠° ͜ʖ °)⤏
Table Lenny: (╯°□°)╯︵ ┻━┻
cONFUSED lenny: 乁( ⁰͡ Ĺ̯ ⁰͡ ) ㄏ
Oh hay: (◕ ◡ ◕)
Manly Lenny: ᕦ( ͡͡~͜ʖ ͡° )ᕤ
Put ur dongers up or I'll shoot: (ง ͡° ͜ʖ ͡°)=/̵͇̿/'̿'̿̿̿ ̿ ̿̿
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
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def roast(self, ctx, *, target: typing.Union[discord.Member, discord.User]):
        """Roast someone. ⌐■_■"""

        roasts = [
            "You spend your time on this thingy {}? I bet you don't even know what it does. By the"
            " way,"
            " can you even read this?",
            "{}, I fart to make you smell better.",
            "{}, why don't you check eBay and see if they have a life for sale?",
            "{}, you bring everyone a lot of joy, when you leave the room.",
            "{}, you're as bright as a black hole, and twice as dense.",
            "{}, what'll you do to get a face after that baboon wants his face back?",
            "{}, I don't exactly hate you, but if you were on fire and I had water, I'd drink the"
            " water.",
            "They say people look like their pets. I'm assuming you have an elephant?",
            "{}, I'll never forget the first time we met, although I'll keep trying.",
            "{}, I don't think I can think of an insult bad enough for you.",
            "{}, there are more calories in your stomach than in the local supermarket!",
            "{}, you shouldn't play hide and seek, no one would look for you.",
            "{}, if I gave you a penny for your thoughts, I'd get change.",
            "{}, so you've changed your mind, does this one work any better?",
            "{}, you're so ugly, when your mom dropped you off at school she got a fine for littering.",
            "{}, you're so fat the only letters of the alphabet you know are KFC.",
            "I don't forget a single face, but in your case, {}, I'll make an exception.",
            "Yo {}, looks like you traded in your neck for an extra chin...",
            "Oh no, look at you, {}! Was anybody else hurt in that accident?",
            "I would roast {}, but I'm told burning trash is bad for the environment.",
            "Hey {}, I thought of you today. It reminded me to take out the trash.",
            "{}, you're like a cloud. When you disappear, it's a beautiful day.",
            "{}, I would make a joke about your life, but I see life has beaten me to it."
        ]

        await ctx.send(random.choice(roasts).replace("{}", target.display_name))

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
        invoke_without_command=True
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dice(self, ctx, *, dice):
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

            total, rolls = roll_XdY(count, limit, return_rolls=True)
            count = len(rolls)
            rolls = map(str, rolls)

            avg = total / count
            avg = round(avg, 8)

            content = f":game_die: {', '.join(rolls)}. The total was {total}, and the average (mean) was {avg}."

            if len(content) > 2000:
                # Yes, this is blocking, but given current limits responses are almost always ~4000 characters max.
                file_content = "Rolls: {1}{0}{1}Total: {2}{1}Average: {3}{1}".format(
                    "\n".join(rolls), "\n", total, avg)
                try:
                    await msg.edit(content=await ctx.bot.post_to_hastebin(file_content))
                except (aiohttp.ContentTypeError, AssertionError):
                    fp = io.BytesIO(file_content.encode("utf-8"))
                    await ctx.send(
                        ":white_check_mark: Your output was longer than 2000 characters and was therefore placed in"
                        " this file:",
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
    async def fight(self, ctx, *, target: typing.Union[discord.Member, discord.User]):
        """FIGHT"""

        # Yes, this entire command is an eyesore. I'll get to it. Soon.
        if target.bot:
            return await ctx.send(
                ":x: Oops! You can't fight a robot; it's robot arms will annihilate you! Perhaps you meant a human?"
            )
        if target == ctx.author:
            return await ctx.send(":x: You can't fight yourself!")

        if ctx.author.id in self.uids_fighting:
            emb = ctx.default_embed()
            emb.description = f"{ctx.author.mention} :x: You can't fight multiple people at once! You're not Bruce" \
                              f" Lee."
            fp = discord.File(os.path.join("assets", "brucelee.gif"), "image.gif")

            await ctx.send(embed=emb, file=fp)

            return
        if target.id in self.uids_fighting:
            emb = ctx.default_embed()
            emb.description = f"{ctx.author.mention} :x: Don't make {target.mention} fight multiple people at once!" \
                              f" They're not Bruce Lee."
            fp = discord.File(os.path.join("assets", "brucelee.gif"), "image.gif")
            emb.set_image(
                url="attachment://image.gif"
            )

            return await ctx.send(embed=emb, file=fp)

        self.uids_fighting.append(ctx.author.id)
        self.uids_fighting.append(target.id)

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
                    return m.content.lower().startswith("hit") or m.content.lower().startswith("run") \
                           or m.content.lower().startswith("block") or m.content.lower().startswith("end")
                else:
                    return False

            try:
                usrinput = await ctx.bot.wait_for("message", check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send("it timed out noobs")
                return purge_from_list(self.uids_fighting, ctx.author.id, target.id)

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
                return purge_from_list(self.uids_fighting, ctx.author.id, target.id)

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

        purge_from_list(self.uids_fighting, ctx.author.id, target.id)

    @commands.command(
        description="Reacts with a sheep emoji to sheep-related messages. Send `sk!stop` to end the sheepiness."
    )
    async def sheep(self, ctx):
        """React to messages with a sheep emoji."""

        if ctx.channel.id not in self.channelids_sheeping:
            self.channelids_sheeping.append(ctx.channel.id)
            m = ctx.message

            with contextlib.suppress(discord.HTTPException):
                await m.add_reaction("\U0001F411")

            while True:
                m = await ctx.bot.wait_for("message", check=lambda m: m.channel == ctx.channel, timeout=300)
                if m is None:
                    break
                if any(i in m.content.lower() for i in ["sheep", "shep", "🐑", "ba", "wool"]):
                    with contextlib.suppress(discord.HTTPException):
                        await m.add_reaction("\U0001F411")

            purge_from_list(self.channelids_sheeping, ctx.channel.id)
        else:
            await ctx.send(":white_check_mark: Done.")
            purge_from_list(self.channelids_sheeping, ctx.channel.id)

    @commands.command(
        description="Reacts with a duck emoji to duck-related messages. Send `sk!stop` to end the quackery."
    )
    async def duck(self, ctx):
        """React to messages with a duck emoji."""

        if ctx.channel.id not in self.channelids_ducking:
            self.channelids_ducking.append(ctx.channel.id)
            m = ctx.message

            await m.add_reaction("\U0001F986")

            pattern = re.compile("(kw|qu)a+c+k?")

            while True:
                m = await ctx.bot.wait_for("message", check=lambda m: m.channel == ctx.channel, timeout=300)
                if m is None:
                    break
                r = re.search(pattern, m.content.lower())
                if any(i in m.content.lower() for i in ["duck", "duk", "🦆", "ducc"]) or r:
                    await m.add_reaction("\U0001F986")

            purge_from_list(self.channelids_ducking, ctx.channel.id)
        else:
            await ctx.send(":white_check_mark: Done.")
            purge_from_list(self.channelids_ducking, ctx.channel.id)

    @commands.command(
        description="Reacts with a dog emoji to dog-related messages. Send `sk!stop` to end the borkiness."
    )
    async def dog(self, ctx):
        """React to messages with a dog emoji."""

        if ctx.channel.id not in self.channelids_dogging:
            self.channelids_dogging.append(ctx.channel.id)
            m = ctx.message

            with contextlib.suppress(discord.HTTPException):
                await m.add_reaction("\U0001f436")

            patterns = [re.compile("b[oa]+r+[ck]+"), re.compile("w+o+f+"),
                        re.compile("a+r+f+"), re.compile("do+g+e?o?")]

            while True:
                m = await ctx.bot.wait_for("message", check=lambda m: m.channel == ctx.channel, timeout=300)
                if m is None:
                    break
                r = any(re.search(p, m.content.lower()) is not None for p in patterns)
                if r:
                    with contextlib.suppress(discord.HTTPException):
                        await m.add_reaction("\U0001f436")

            purge_from_list(self.channelids_dogging, ctx.channel.id)
        else:
            await ctx.send(":white_check_mark: Done.")
            purge_from_list(self.channelids_dogging, ctx.channel.id)

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

        async with ctx.bot.session.get(f"https://cdn.welcomer.fun/minecraftxp?percent={percent}") as resp:
            raw = await resp.content.read()

        fp = discord.File(io.BytesIO(raw), "xp.png")

        await ctx.send(file=fp)

    @commands.command(aliases=["mca"])
    async def minecraftachievement(self, ctx, *, text):
        """Generate a Minecraft achievement toast with your text."""

        async with ctx.typing():
            headers = dict(Authorization=config.flipnote_key)
            async with ctx.bot.session.get(f"https://api.alexflipnote.dev/achievement?text={text}", headers=headers
                                           ) as resp:
                raw = await resp.content.read()

        await ctx.send(file=discord.File(io.BytesIO(raw), "achieved.png"))

    @commands.command(aliases=["mcc"])
    async def minecraftchallenge(self, ctx, *, text):
        """Generate a Minecraft challenge toast with your text."""

        async with ctx.typing():
            headers = dict(Authorization=config.flipnote_key)
            async with ctx.bot.session.get(f"https://api.alexflipnote.dev/challenge?text={text}", headers=headers
                                           ) as resp:
                raw = await resp.content.read()

        await ctx.send(file=discord.File(io.BytesIO(raw), "challengecompleted.png"))

    @commands.command()
    async def supreme(self, ctx, *, text="Supreme"):
        """Draw a Supreme sticker with your text."""

        async with ctx.typing():
            headers = dict(Authorization=config.flipnote_key)
            async with ctx.bot.session.get(f"https://api.alexflipnote.dev/supreme?text={text}", headers=headers
                                           ) as resp:
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

    @commands.command(aliases=["connect4"],
                      description="On your turn, react with a number to place a counter on that row, or react with"
                                  " :arrow_double_down: to switch sides. You may react with :stop_button: to stop the"
                                  " game at any time.")
    async def c4(self, ctx, *, member: typing.Union[discord.Member, discord.User]):
        """Play Connect4 with someone."""

        if member == ctx.author:
            return await ctx.send("You cannot play against yourself!")
        if member.bot:
            return await ctx.send("You can't play bots!")

        if ctx.author.id in self.uids_c4ing:
            emb = ctx.default_embed()
            emb.description = f"{ctx.author.mention} :x: You can't play multiple Connect4 games at once!"

            return await ctx.send(embed=emb)

        if member.id in self.uids_c4ing:
            emb = ctx.default_embed()
            emb.description = f"{ctx.author.mention} :x: {member.mention} is already in a Connect4 game."

            return await ctx.send(embed=emb)

        self.uids_c4ing.append(ctx.author.id)
        self.uids_c4ing.append(member.id)

        board = C4(ctx.author, member, ctx)
        await board.do_game()

        purge_from_list(self.uids_c4ing, ctx.author.id, member.id)

    @commands.group(aliases=["mm"], invoke_without_command=True)
    @commands.bot_has_permissions(add_reactions=True)
    async def mastermind(self, ctx):
        """[VERY SPAMMY] Play Mastermind, with the bot making the code. See the rules subcommand for info."""

        if ctx.channel.id in self.channelids_masterminding:
            await ctx.message.add_reaction("\U0000203c")
            try:
                return await ctx.author.send(
                    ":x: There is already another game in that channel. You can also play Mastermind in this DM, "
                    "if you'd like..."
                )
            except discord.Forbidden:
                return await ctx.send(
                    ":x: There is already another game in this channel. You can also play Mastermind in a DM, if "
                    "you'd like..."
                )

        if ctx.author.id in self.uids_masterminding:
            return await ctx.send(":x: You cannot play two Mastermind games at once.")

        self.channelids_masterminding.append(ctx.channel.id)
        self.uids_masterminding.append(ctx.author.id)

        game = Mastermind(ctx)
        await game.run()

        purge_from_list(self.channelids_masterminding, ctx.channel.id)
        purge_from_list(self.uids_masterminding, ctx.author.id)

    @mastermind.command(name="rules", aliases=["r"])
    async def mastermind_rules(self, ctx):
        """Displays the rules for Mastermind. Useful when kept in your back pocket."""

        rules = "**Mastermind rules:**\n\nI have a code of four colors that you need to guess. The possible colors " \
                "are black, white, red, blue, yellow, and green. *Repeat colors are possible in the code.*" \
                "You get 24 attempts to guess the code before I reveal it.\nEvery time you guess the four-digit " \
                "code, I will reply with another four-digit code:\nA :white_check_mark: means your digit is of the " \
                "correct color, and is in the right place.\nA :thinking: means your digit is of the correct color, " \
                "but it needs to be in a different spot.\nFinally, :x: means your digit is the wrong color, and you " \
                "need to try a different color.\n\nThe four-digit code I give you after a guess is in no particular " \
                "order. This means that if the first digit in my response is :white_check_mark:, that does not " \
                "*necessarily* mean that the first digit of your guess was correct.\n\nBefore you play, a few " \
                "hints:\nRemember to use your feedback to your advantage. If you get, for example, " \
                ":white_check_mark::white_check_mark::thinking::thinking:, you know that the colors in your latest " \
                "guess should not be changed, and that you should keep reordering them until you win.\nA good " \
                "starting strategy is to guess as many different colors as possible, then use the feedback to figure " \
                "out which colors belong and which don't.\n\nYou have 24 tries at cracking the code. Good luck " \
                "beating the Mastermind!"

        await ctx.send(rules)

    @mastermind.command(name="toggleintro", aliases=["ti"])
    async def mastermind_toggleintro(self, ctx, *, setting: bool = None):
        """Toggle the introductory message. You must have 5 games won to access this function."""

        record = await ctx.bot.db_pool.fetchrow("SELECT wins, intro_opt_out FROM mastermind WHERE user_id = $1;",
                                                ctx.author.id)
        if record:
            wins, is_opted_out = record["wins"], record["intro_opt_out"]
        else:
            wins = 0
            is_opted_out = 0

        if wins < 5:
            return await ctx.send("You cannot access this feature, you must have won at least 5 games.")
        else:
            if setting is None:
                await ctx.send(f"You have the introductory message {'enabled' if not is_opted_out else 'disabled'}.")
            else:
                await ctx.bot.db_pool.execute("UPDATE mastermind SET intro_opt_out = $1 WHERE user_id = $2;",
                                              int(setting), ctx.author.id)
                await ctx.send(":white_check_mark: Done.")

    @mastermind.command(name="wins")
    async def mastermind_wins(self, ctx, *, user: typing.Union[discord.Member, discord.User] = None):
        """Check how many times someone has won Mastermind."""

        user = user or ctx.author

        if user.bot:
            return await ctx.send("Bots don't play Mastermind...")

        stored_wins = await ctx.bot.db_pool.fetchval("SELECT wins FROM mastermind WHERE user_id = $1;", user.id)
        wins = stored_wins if stored_wins is not None else 0

        await ctx.send(f"{use_potential_nickname(user)} has {format(Plural(wins), 'win')}.")

    @mastermind.command(name="leaderboard", aliases=["top", "leaderboards", "lb"])
    async def mastermind_leaderboard(self, ctx):
        """Show the lifetime Mastermind wins leaderboard"""

        if not await ctx.bot.db_pool.fetchval("SELECT EXISTS(SELECT 1 FROM mastermind) AS exists;"):
            return await ctx.send("Nobody seems to have Mastermind records...")

        records = await ctx.bot.db_pool.fetch("SELECT user_id, wins FROM mastermind ORDER BY wins DESC LIMIT 10;")
        emb = ctx.default_embed()
        emb.description = f"Showing (up to) top 10 players. Find you or another user's ranking with " \
                          f"`{ctx.prefix}mastermind ranking <user>`."
        for index, record in enumerate(records):
            fetch = None
            if ctx.guild:
                try:
                    fetch = await ctx.guild.fetch_member(record["user_id"])
                except discord.NotFound:
                    pass
            if not ctx.guild or fetch is None:
                try:
                    fetch = use_potential_nickname(await ctx.bot.fetch_user(record["wins"]))
                except discord.NotFound:
                    fetch = "<invalid user>"
            emb.add_field(
                name=f"`{index + 1}:` {fetch}",
                value=f"{format(Plural(record[1]), 'win')}",
                inline=False
            )
        await ctx.send(embed=emb)

    @mastermind.command(name="ranking")
    async def mastermind_ranking(self, ctx, *, user: typing.Union[discord.User, discord.Member, int]):
        """Check the ranking of a user on the wins leaderboard."""

        user = user or ctx.author
        uid = user.id if not isinstance(user, int) else user

        stored_wins = await ctx.bot.db_pool.fetchval("SELECT wins FROM mastermind WHERE user_id = $1;", uid)
        wins = stored_wins if stored_wins is not None else 0

        if wins == 0:
            await ctx.send("This user does not have any wins.")
        else:
            record_count = await ctx.bot.db_pool.fetchval("SELECT COUNT(user_id) FROM mastermind WHERE wins > 0;")
            async with ctx.bot.db_pool.acquire() as conn:
                async with conn.transaction():
                    async for record in conn.cursor("SELECT wins, RANK() OVER (ORDER BY wins DESC) r FROM mastermind;"):
                        db_wins, rank = record[0], record[1]
                        if db_wins == wins:
                            ranking = rank
                            break

            await ctx.send(f"{use_potential_nickname(user)} is #{ranking:,} out of "
                           f"{format(Plural(record_count), 'total user')} on record.")

    @commands.command(aliases=["scan"])
    @commands.guild_only()
    @commands.cooldown(3, 5, commands.BucketType.user)
    async def search(self, ctx, reading, *, user: typing.Union[discord.Member, discord.TextChannel] = None):
        """Use cutting-edge AI to search for qualities of a channel or user."""

        user = user or ctx.channel
        if isinstance(user, discord.abc.User):
            user = user.display_name
        else:
            user = "#" + user.name

        level = random.randint(1, 1000) / 10
        ticks = int(level // 5)
        not_ticks = 20 - ticks
        ticks = "\U00002588" * ticks
        not_ticks = "-" * not_ticks
        emb = ctx.default_embed()
        emb.description = f"**{reading} levels for {user}:**"
        emb.add_field(name="\u200b", value=f"```|{ticks}{not_ticks}|  {level}%  ```")
        emb.add_field(name="\u200b", value="\u200b")

        msg = await ctx.send(f"Calculating {reading} levels for {user}...")
        await asyncio.sleep(2)
        await msg.edit(content=None, embed=emb)

    @commands.group(aliases=["inspiro"])
    @commands.cooldown(3, 5, commands.BucketType.user)
    @commands.check(custom_inspire_blacklist)
    async def inspire(self, ctx):
        """Fetch an AI generated quote for inspiration. (can include expletives occasionally)"""

        if ctx.invoked_subcommand is None:
            async with ctx.bot.session.get("https://inspirobot.me/api?generate=true") as resp:
                out = await resp.content.read()
            out = out.decode("utf-8")

            emb = ctx.colored_embed
            emb.set_image(url=out)
            await ctx.send(embed=emb)

            self.latest_inspires[ctx.author.id] = out

    @staticmethod
    def _inspire_msg_check(ctx, msg):
        if msg.content:
            reg = re.match(r"https://generated\.inspirobot\.me/a/[a-zA-Z0-9]{10}.jpg", msg.content)
            if reg is not None and reg.group(0) == msg.content:
                return True, msg.content
            return

        if len(msg.embeds) < 1:
            return
        emb = msg.embeds[0]
        if emb.image == discord.Embed.Empty:
            return

        reg = re.match(r"https://generated\.inspirobot\.me/a/[a-zA-Z0-9]{10}.jpg", emb.image.url)
        if reg is None or reg.group(0) != emb.image.url:
            return

        return True, emb.image.url

    @inspire.command(name="favorite", aliases=["f", "fave"],
                     description="To favorite an image, link a message containing an Inspirobot image or include a "
                                 "link to an Insprobot image. If you do neither, the most recent image you requested "
                                 "will be favorited.")
    async def inspire_favorite(self, ctx, *, msg: typing.Union[discord.Message, str] = None):
        """Add an Inspirobot image to your personal library."""

        if msg is None:
            url = self.latest_inspires.get(ctx.author.id, None)
            if url is None:
                return await ctx.send("You do not have a latest image on record. Please pass a message link or ID to "
                                      "favorite it.")
        else:
            if isinstance(msg, str):
                reg = re.match(r"https://generated\.inspirobot\.me/a/[a-zA-Z0-9]{10}.jpg", msg)
                if reg is None or reg.group(0) != msg:
                    return await ctx.send("This string is not an inspiring message.")
                url = msg
            else:
                check = self._inspire_msg_check(ctx, msg)
                if not check:
                    return await ctx.send("This message does not contain an inspiring quote.")
                url = check[1]

        query = await ctx.bot.db_pool.fetchrow("SELECT * FROM inspire_favorites WHERE user_id = $1 AND image = $2;",
                                               ctx.author.id,
                                               url.lstrip("https://generated.inspirobot.me/a/").rstrip(".jpg"))

        if query:
            await ctx.send("This image is already in your personal library.")
        else:
            await ctx.bot.db_pool.execute("INSERT INTO inspire_favorites (user_id, image) VALUES ($1, $2);",
                                          ctx.author.id,
                                          url.lstrip("https://generated.inspirobot.me/a/").rstrip(".jpg"))
            await ctx.send(":white_check_mark: Added.")

    @inspire.command(name="unfavorite", aliases=["uf", "unfave"],
                     description="To unfavorite an image, link a message containing an Inspirobot image or include a "
                                 "link to an Insprobot image. If you do neither, the most recent image you requested "
                                 "will be unfavorited.")
    async def inspire_unfavorite(self, ctx, *, msg: typing.Union[discord.Message, str] = None):
        """Remove an Inspirobot image from your personal library."""

        if msg is None:
            url = self.latest_inspires.get(ctx.author.id, None)
            if url is None:
                return await ctx.send("You do not have a latest image on record. Please pass a message link or ID to "
                                      "unfavorite it.")
        else:
            if isinstance(msg, str):
                reg = re.match(r"https://generated\.inspirobot\.me/a/[a-zA-Z0-9]{10}.jpg", msg)
                if reg is None or reg.group(0) != msg:
                    return await ctx.send("This string is not an inspiring message.")
                url = msg
            else:
                check = self._inspire_msg_check(ctx, msg)
                if not check:
                    return await ctx.send("This message does not contain an inspiring quote.")
                url = check[1]

        query = await ctx.bot.db_pool.fetchrow("SELECT * FROM inspire_favorites WHERE user_id = $1 AND image = $2;",
                                               ctx.author.id,
                                               url.lstrip("https://generated.inspirobot.me/a/").rstrip(".jpg"))

        if not query:
            await ctx.send("This image is not in your personal library.")
        else:
            await ctx.bot.db_pool.execute("DELETE FROM inspire_favorites WHERE user_id = $1 AND image = $2;",
                                          ctx.author.id,
                                          url.lstrip("https://generated.inspirobot.me/a/").rstrip(".jpg"))
            await ctx.send(":white_check_mark: Deleted requested image from your library.")

    @inspire.command(name="view", aliases=["list", "show"])
    async def inspire_view(self, ctx):
        """View your favorited Inspirobot content."""

        exists = await ctx.bot.db_pool.fetchval("SELECT EXISTS(SELECT 1 FROM inspire_favorites WHERE user_id = $1);",
                                                ctx.author.id)
        if not exists:
            return await ctx.send(f"No favorites found. Add some with `{ctx.prefix}inspire favorite`.")

        emb = ImageEmbedinator(ctx.bot, ctx, color=ctx.bot.embed_color, member=ctx.author)
        emb.base_embed.set_footer(
            text=f"{ctx.bot.embed_footer} Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )

        async with ctx.bot.db_pool.acquire() as conn:
            async with conn.transaction():
                async for record in conn.cursor("SELECT image FROM inspire_favorites WHERE user_id = $1;",
                                                ctx.author.id):
                    emb.add_image(f"https://generated.inspirobot.me/a/{record[0]}.jpg")

        await emb.send()
        await emb.handle()

    @inspire.command(name="clear", aliases=["cls"])
    async def inspire_clear(self, ctx):
        """Clear your favorite images list."""

        query = await ctx.bot.db_pool.fetchrow("SELECT * FROM inspire_favorites WHERE user_id = $1;", ctx.author.id)
        if not query:
            return await ctx.send("Can't wipe an empty favorites list.")

        msg = await ctx.send(
            f"{ctx.author.mention}, please react below to confirm you are wiping your Inspiro favorites list "
            f"**permanently**."
        )
        try:
            await msg.add_reaction("\U00002705")
        except discord.Forbidden:
            pass

        def check(payload):
            return payload.user_id == ctx.author.id and payload.message_id == msg.id \
                   and payload.channel_id == ctx.channel.id and str(payload.emoji) == "\U00002705"

        try:
            await ctx.bot.wait_for("raw_reaction_add", check=check, timeout=30.0)
            await ctx.bot.db_pool.execute("DELETE FROM inspire_favorites WHERE user_id = $1;", ctx.author.id)
            await ctx.send(f":ok_hand: Wiped {len(query)} entries from your favorites list.")
        except asyncio.TimeoutError:
            return


def setup(bot):
    bot.add_cog(Fun())
