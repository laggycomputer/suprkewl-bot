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

import asyncio
import io
import json
import math
import random

import aiohttp
import discord
from discord.ext import commands


class _fighter:
    def __init__(self, user):
        self.user = user
        self.health = 100
        self.turn = False
        self.won = False
        self.blocking = False
class _fdata:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

class Random(commands.Cog):

    @commands.command(aliases=["burn"])
    async def roast(self, ctx, target: discord.Member):
        """Roast someone. ⌐■_■"""

        roasts = [
            f"You spend your time on this thingy {target.mention}? I bet you don't even know what it does. By the way, can you even read this?",
            f"{target.mention}, I fart to make you smell better.",
            f"{target.mention}, Your parents hated you so much your bath toys were an iron and a toaster. ~~go commit toaster bath~~",
            f"{target.mention}, Why don't you check eBay and see if they have a life for sale?",
            f"{target.mention}, You bring everyone a lot of joy, when you leave the room.",
            f"{target.mention}, you're as bright as a black hole, and twice as dense.",
            f"{target.mention}, what'll you do to get a face after that baboon wants his face back?",
            f"{target.mention}, I don't exactly hate you, but if you were on fire and I had water, I'd drink the water.",
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
        await ctx.bot.register_response(sent, ctx.message)

    @commands.command(aliases=["card"], description="Draw from a standard, 52-card deck, no jokers.")
    async def draw(self, ctx):
        """Draw a card"""

        suits = [":spades:", ":diamonds:", ":hearts:", ":clubs:"]

        ranks = [
            "Ace", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:",
            ":eight:", ":nine:", ":keycap_ten:", "Jack", "Queen", "King"
        ]

        sent = await ctx.send(f"I drew the {random.choice(ranks)} of {random.choice(suits)}")
        await ctx.bot.register_response(sent, ctx.message)

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

        await ctx.bot.register_response(msg, ctx.message)

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

        async with ctx.channel.typing():
            await asyncio.sleep(2)
            msg = await ctx.send(f"{ctx.author.mention} :fist: Rock...")
            await ctx.bot.register_response(msg, ctx.message)
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
    async def dice(self, ctx, dice: str):
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
                content=f":x: Your input must be of the form `AdB`! Please check `{ctx.prefix}{ctx.invoked_with} info` for more info."
            )
            await ctx.bot.register_response(msg, ctx.message)
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

            content = f":game_die: {rolls}. The total was {total}, and the average (mean) was {avg}."

            if len(content) > 2000:
                # Yes, this is blocking, but given current limits responses are almost always ~4000 characters max.
                file_content = "Rolls: {0}Total: {2}{1}Average:{3}".format("\n".join(rolls), "\n", total, avg)
                fp = io.BytesIO(file_content.encode("utf-8"))
                sent = (await ctx.send(
                    content=":white_check_mark: Your output was longer than 2000 characters and was therefore placed in this file:",
                    file=discord.File(fp, "rolls.txt")
                ))
                await ctx.bot.register_response(sent, ctx.message)

            else:
                await msg.edit(
                    content=content
                )
                await ctx.bot.register_response(msg, ctx.message)
        else:
            await msg.edit(
                content=f"Your syntax was correct, however one of your arguments were invalid. See `{ctx.prefix}{ctx.invoked_with} info.`"
            )
            await ctx.bot.register_response(msg, ctx.message)

    @dice.command(description="Show info for dice command.", name="info")
    async def dice_info(self, ctx):
        sent = (await ctx.send(
            "Your argument must be of the form AdB, where A is the number of dice to roll and B is the number of sides on each die. A and B must be postive integers between 1 and 1000."
        ))
        await ctx.bot.register_response(sent, ctx.message)

    @commands.command(
        aliases=["pick", "rand"],
        description="The tiebreaker of all tiebreakers."
    )
    @commands.cooldown(2, 1, commands.BucketType.channel)
    async def choose(self, ctx, *choices: str):
        """Choose between given choices"""

        async with ctx.channel.typing():
            await asyncio.sleep(1)
            msg = await ctx.send("Choosing...")
            await ctx.bot.register_response(msg, ctx.message)
            await asyncio.sleep(1.5)
            await msg.edit(content="Eeeny, Meeny, Miney, Mo. Catch a tiger by the toe...")

        async with ctx.channel.typing():
            await asyncio.sleep(1)
            message = f"{ctx.author.mention}, I choose '"
            message += random.choice(choices) + "'."
            await msg.edit(content=message)

    @commands.command(
        description="Starts a fight between the command invoker and the specified <target>."
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def fight(self, ctx, target: discord.Member):
        """FIGHT"""

        # Yes, this entire command is an eyesore. I'll get to it. Soon.
        if target.bot:
            sent = (await ctx.send(
                ":x: Oops! You can't fight a robot; it's robot arms will annihilate you! Perhaps you meant a human?"
            ))
            await ctx.bot.register_response(sent, ctx.message)
            return
        if target == ctx.author:
            sent = (await ctx.send(":x: You can't fight yourself!"))
            await ctx.bot.register_response(sent, ctx.message)
            return
        if (await ctx.bot.redis.exists(f"{ctx.author.id}:fighting")):
            emb = discord.Embed(
                color=0xf92f2f,
                description=f"{ctx.author.mention} :x: You can't fight multiple people at once! You're not Bruce Lee."
            )
            emb.set_image(
                url="https://media1.tenor.com/images/8c69a1095f5d7745fabbdedf569644e7/tenor.gif?itemid=13291191"
            )
            emb.set_thumbnail(url=ctx.guild.me.avatar_url)
            emb.set_author(name=ctx.guild.me.name, icon_url=ctx.guild.me.avatar_url)
            emb.set_footer(text=f"{ctx.bot.description} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            sent = (await ctx.send(embed=emb))
            await ctx.bot.register_response(sent, ctx.message)

            return
        if (await ctx.bot.redis.exists(f"{target.id}:fighting")):
            emb = discord.Embed(
                color=0xf92f2f,
                description=f"{ctx.author.mention} :x: Don't make {target.mention} fight multiple people at once! They're' not Bruce Lee."
            )
            emb.set_image(
                url="https://media1.tenor.com/images/8c69a1095f5d7745fabbdedf569644e7/tenor.gif?itemid=13291191"
            )
            emb.set_thumbnail(url=ctx.guild.me.avatar_url)
            emb.set_author(name=ctx.guild.me.name, icon_url=ctx.guild.me.avatar_url)
            emb.set_footer(text=f"{ctx.bot.description} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            sent = (await ctx.send(embed=emb))
            await ctx.bot.register_response(sent, ctx.message)

            return
        await ctx.bot.redis.execute("SET", f"{ctx.author.id}:fighting", "fighting")
        await ctx.bot.redis.execute("SET", f"{target.id}:fighting", "fighting")

        await ctx.send(":white_check_mark: Starting fight...")

        async with ctx.channel.typing():
            await asyncio.sleep(1)

            p1 = _fighter(ctx.author)
            p2 = _fighter(target)

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
                damage = 0
                currentaction = ""
                blow = ""

            currentaction = ""
            newsetting = ""
            blow = ""
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
                "Living Room": "{0.mention} narrowly beats {1.mention} in a sword-fight using the Dolby 7:1 surround speakers",
                "Backyard": "{0.mention} throws some hot coals from the backyard stove at {1.mention}"
            }

            connectedrooms = {
                "Laundry Room":["Backyard","Kitchen"], "Dining Room":["Kitchen","Backyard"], "Kitchen":["Dining Room","Living Room"],
                "Bedroom":["Living Room"], "Living Room":["Kitchen","Bedroom"], "Backyard":["Laundry Room","Laundry Room"]
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

            if usrinput == None:
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
                        blow = deathblows[setting].format(find_turn().user, find_not_turn().user)
                        blow += " (DEATHBLOW)"
                        damage = 100

                    elif rand > 9:
                        blow = random.choice(universalactions).format(find_turn().user, find_not_turn().user)
                        damage = random.randint(1, 50)

                    else:
                        blow = random.choice(fightactions[setting]).format(find_turn().user, find_not_turn().user)
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

                    currentaction = f"{find_turn().user.mention} kicks {find_not_turn().user.mention} in the shins and runs as fast as he/she can out of the {setting} and into the {newsetting}. {find_turn().user.mention} gives chase."

                    setting = newsetting
                    newsetting = ""

                elif usrinput.content.lower().startswith("end"):
                    await ctx.send(
                        f"{find_turn().user.mention} and {find_not_turn().user.mention} get friendly and the fight's over."
                    )
                    await ctx.bot.redis.delete(f"{ctx.author.id}:fighting", f"{target.id}:fighting")
                    return

                find_not_turn().health -= damage
                if find_not_turn().health < 0:
                    find_not_turn().health = 0

                emb = discord.Embed(name="FIGHT", color=find_turn().user.colour)

                emb.add_field(name="Current Setting", value=f"`{setting}`")
                emb.add_field(name="Player 1 health", value=f"**{p1.health}**")
                emb.add_field(name="Player 2 health", value=f"**{p2.health}**")
                emb.add_field(name="Current action", value=currentaction)

                emb.set_thumbnail(url=ctx.bot.user.avatar_url)
                emb.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
                emb.set_footer(
                    text=f"{ctx.bot.description} Requested by {ctx.author}",
                    icon_url=ctx.author.avatar_url
                )

                if sent is None:
                    sent = (await ctx.send(embed=emb))
                    await ctx.bot.register_response(sent, ctx.message)
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
        await ctx.send(
            f"Looks like {win_mention} defeated {lose_mention} with {findwin().health} health left!"
        )

        await ctx.bot.redis.delete(f"{ctx.author.id}:fighting", f"{target.id}:fighting")

    @commands.group(description="Gets an xkcd comic.", invoke_without_command=True)
    @commands.cooldown(1, 3, commands.BucketType.channel)
    async def xkcd(self, ctx, arg: int=None):
        if arg is None:
            await self.xkcd_latest(ctx)
        else:
            if arg <= 0:
                sent = (await ctx.send(":x: Invalid comic number."))
                await ctx.bot.register_response(sent, ctx.message)
                return
            
            await self.xkcd_get(ctx, arg)

    async def xkcd_get(self, ctx, number):
        async with ctx.bot.http2.get(f"https://xkcd.com/{number}/info.0.json") as resp:
            if resp.status == 404:
                sent = (await ctx.send(":x: Comic not found!"))
                await ctx.bot.register_response(sent, ctx.message)
                return
            text = await resp.json()

        emb = discord.Embed(
            color=0xf92f2f,
            description=f"Here you are! xkcd comic #{number}. Credits to [xkcd](https://xkcd.com/{number})."
        )
        emb.set_image(url=text["img"])

        emb.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        emb.set_footer(
            text=f"{ctx.bot.description} Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )

        sent = (await ctx.send(embed=emb))
        await ctx.bot.register_response(sent, ctx.message)

    @xkcd.command(name="random", aliases=["rand"], description="Get a random xkcd comic.")
    async def xkcd_random(self, ctx):
        if not ctx.command.parent.can_run(ctx):
            return

        async with ctx.bot.http2.get("https://xkcd.com/info.0.json") as resp:
            text = await resp.text()
        text = json.loads(text)
        latest_comic = text["num"]

        comic_to_get = random.randint(0, int(latest_comic))

        async with ctx.bot.http2.get(f"https://xkcd.com/{comic_to_get}/info.0.json") as resp:
            text = await resp.text()
        text = json.loads(text)

        emb = discord.Embed(
            color=0xf92f2f,
            description=f"Here you are! xkcd comic #{comic_to_get}. Credits to [xkcd](https://xkcd.com/{comic_to_get})."
        )
        emb.set_image(url=text["img"])

        emb.set_author(
            name=ctx.bot.user.name,
            icon_url=ctx.bot.user.avatar_url
        )
        emb.set_footer(
            text=f"{ctx.bot.description} Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )

        sent = (await ctx.send(embed=emb))
        await ctx.bot.register_response(sent, ctx.message)

    async def xkcd_latest(self, ctx):
        async with ctx.bot.http2.get("https://xkcd.com/info.0.json") as resp:
            text = await resp.json()

        num = text["num"]

        emb = discord.Embed(
            color=0xf92f2f,
            description=f"Here you are! xkcd comic #{num}. Credits to [xkcd](https://xkcd.com/{num})."
        )
        emb.set_image(url=text["img"])

        emb.set_author(
            name=ctx.bot.user.name,
            icon_url=ctx.bot.user.avatar_url
        )
        emb.set_footer(
            text=f"{ctx.bot.description} Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )

        sent = (await ctx.send(embed=emb))
        await ctx.bot.register_response(sent, ctx.message)

def setup(bot):
    bot.add_cog(Random(bot))
