# -*- coding: utf-8 -*-
"""Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import random
import time

import discord
from discord.ext import commands

class Randomizers():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["burn"])
    async def roast(self, ctx, target: discord.Member):
        """Roast someone. ⌐■_■"""

        roasts = [f"You spend your time on this thingy {target.mention}? I bet you don't even know what it does. By the way, can you even read this?",
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
                  f"I don't forget a single face, but in your case, {target.mention}, I'll make an exception."]

        await ctx.send(random.choice(roasts))

    @commands.command(aliases=["card"], description="Draw from a standard, 52-card deck, no jokers.")
    async def draw(self, ctx):
        """Draw a card"""

        suits = [":spades:", ":diamonds:", ":hearts:", ":clubs:"]
        ranks = ["Ace", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:",
                 ":eight:", ":nine:", ":keycap_ten:", "Jack", "Queen", "King"]

        await ctx.send(f"I drew the {random.choice(ranks)} of {random.choice(suits)}")

    @commands.command(aliases=["flip", "quarter", "dime", "penny", "nickel"])
    async def coin(self, ctx):
        """Flip a coin"""

        msg = await ctx.send("My robot hand flips the coin.")
        await asyncio.sleep(1)

        await msg.edit(content="I slap the coin down on my robot arm.")
        await asyncio.sleep(0.5)

        if random.randint(1,2) == 1:
            await msg.edit(content="It's heads!")
        else:
            await msg.edit(content="It's tails.")

    @commands.command(aliases=["rockpaperscissors"], description="Rock paper scissors. Randomizes a choice for you and the computer. Has a 3 second cooldown on a per-user basis.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def rps(self, ctx):
        """See 's!help rps'."""

        choices = [":fist:", ":newspaper:", ":scissors:"]

        computer = random.choice(choices)
        user = random.choice(choices)
        winner = None
        winmsg = " Congrats! :slight_smile:"
        losemsg = " Better luck next tome... :slight_frown:"

        content = f"{ctx.author.mention} "

        if user == computer:
            content += "We both got :" + computer + ":. Tie!"
        else:
            if user == ":fist:":
                if computer == ":scissors:":
                    content += "Your " + user + " beat my " + computer + "!"
                    winner = "usr"
                else:
                    content += "My " + computer + " beat your " + user + "!"
                    winner = "comp"

            elif user == ":newspaper:":
                if computer == ":fist:":
                    content +=" Your " + user + " beat my " + computer + "!"
                    winner = "usr"
                else:
                    content += "My " + computer + " beat your " + user + "!"
                    winner = "comp"

            elif user == ":scissors:":
                if computer == ":newspaper:":
                    content += "Your " + user + " beat my " + computer + "!"
                    winner = "usr"
                else:
                    content += "My " + computer + " beat your " + user + "!"
                    winner = "comp"

        if winner == "usr":
            content += winmsg
        elif winner == "comp":
            content + losemsg

        async with ctx.channel.typing():
            await asyncio.sleep(2)
            msg = await ctx.send(f"{ctx.author.mention} :fist: Rock...")
            await asyncio.sleep(1)

            await msg.edit(content=f"{ctx.author.mention} :newspaper: Paper...")
            await asyncio.sleep(1)
            await msg.edit(content=f"{ctx.author.mention} :scissors: Scissors...")
            await asyncio.sleep(1)

            await msg.edit(content=f"{ctx.author.mention} :boom: BAM!")
            await asyncio.sleep(0.5)

            await msg.edit(content = content)

    @commands.command(aliases=["laugh"], description="Browse a ridiculously tiny collection of funny images. Has a 2 second per-channel cooldown.")
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def funny(self, ctx):
        """See 's!help funny'"""

        images = ["https://image.ibb.co/f57pL7/Bill.png",
                  "https://image.ibb.co/hHM27n/yey.jpg",
                  "https://image.ibb.co/dWRS7n/bruh1.gif",
                  "https://image.ibb.co/kpUx7n/u_mad_broo.jpg",
                  "https://image.ibb.co/nKTX7n/jumped_Off.jpg",
                  "https://image.ibb.co/i76wYS/uwut.jpg",
                  "https://image.ibb.co/edp0tS/uhhh.jpg",
                  "https://image.ibb.co/gknDF7/no_Briefcase.jpg",
                  "https://image.ibb.co/hFF3hn/any_More_Weekend.jpg",
                  "https://image.ibb.co/hc9Re7/llama.jpg",
                  "https://image.ibb.co/jOuOsS/llamaart.jpg",
                  "https://image.ibb.co/bytavf/justspamf.png"]
        red = random.random() * 255
        green = random.random() * 255
        blue = random.random() * 255

        msg = discord.Embed(name= "This is", title="something funny",
                            description="Don't die of laughter", color=discord.Colour.from_rbg(red, green, blue))

        msg.set_image(url=random.choice(images))

        await ctx.send(embed=msg)

    @commands.command(aliases=["roll"], description="Rolls the dice specified, in AdB format. For example, 's!dice 3d6' would roll 3 six-sided dice. A must be a positive integer up to and including 10, and B has the same contraints, but with a upper limit of 20. This command has a user-based cooldown of 5 seconds.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dice(self, ctx, dice: str):
        """see 's!help dice.'"""

        async with ctx.channel.typing():
            await asyncio.sleep(1)
            msg = await ctx.send("thinking... :thinking:")
            await asyncio.sleep(1)
        try:
            count, limit = map(int, dice.split('d'))
        except Exception:
            await msg.edit(content="Format must be AdB! I was unable to find a seperator between your numbers, or there were no numbers to find. Please check 's!help dice' for more info.")
            return

        if count <= 10 and count > 0 and limit <= 20 and limit > 0:

            for i in range(1, count + 1):
                await msg.edit(content=f":game_die: Rollling die {i}...")
                await asyncio.sleep(1)

            result = ', '.join(str(random.randint(1, limit)) for r in range(count))

            await msg.edit(content=f":game_die: My rolls were: {result}")
        else:
            await msg.edit(content="Your syntax was correct, but one of your arguments was too large to compute, or one of your arguments was negative. Please see 's!help dice' for more info.")

    @commands.command(aliases=["pick", "rand"], description="The tiebreaker of all tiebreakers. Has a 1-second per-channel cooldown, triggered after the command is run twice in the same channel.")
    @commands.cooldown(2, 1, commands.BucketType.channel)
    async def choose(self, ctx, *choices: str):
        """Choose between multiple choices"""

        async with ctx.channel.typing():
            await asyncio.sleep(1)
            msg = await ctx.send("Choosing...")
            await asyncio.sleep(1.5)
            await msg.edit(content="Eeeny, Meeny, Miney, Mo. Catch a tiger by the toe...")

        async with ctx.channel.typing():
            await asyncio.sleep(1)
            message = f"{ctx.author.mention}, I choose '"
            message += random.choice(choices)+"'."
            await msg.edit(content=message)

    class Fighter():
        def __init__(self, user):
            self.user = user
            self.health = 100
            self.turn = False
            self.won = False

    @commands.command(description="Starts a fight between the command invoker and the specified <target>. <target> must be a non-bot and must not be the command invoker. This command has a 10-second cooldown per user.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def fight(self, ctx, target: discord.Member):
        """FIGHT"""

        if target.bot:
            await ctx.send(":x: Oops! You can't fight a robot; it's robot arms will annihilate you! Perhaps you meant a human?")
        else:
            if target == ctx.author:
                await ctx.send(":x: You can't fight yourself!")
            else:
                await ctx.send(":white_check_mark: Starting fight...")

                async with ctx.channel.typing():
                    await asyncio.sleep(1)

                    p1 = self.Fighter(ctx.author)
                    p2 = self.Fighter(target)

                    def findTurn():
                        if p1.turn:
                            return p1
                        elif p2.turn:
                            return p2
                        else:
                            return None
                    def findNotTurn():
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
                        damage = 0
                        currentaction = ""
                        blow = ""

                    currentaction = ""
                    newsetting = ""
                    blow = ""
                    damage = 0

                    fightplaces = ["Laundry Room", "Dining Room", "Kitchen", "Bedroom", "Living Room", "Backyard"]

                    fightactions = {"Laundry Room": ["{0.mention} whips {1.mention} with a freshly washed towel", "{0.mention} shuts {1.mention} in the washer, but {1.mention} narrowly escapes", "{0.mention} throws a tennis ball from inside the clothes dryer at {1.mention}"],
                                    "Dining Room": ["{0.mention} throws a plate at {1.mention}", "{0.mention} stabs {1.mention} with a piece of a broken vase", "{0.mention} pins {1.mention} against the wall with the table"],
                                    "Kitchen": ["{0.mention} cuts {1.mention} with a a knife", "{0.mention} pours some boiling water on {1.mention}","{0.mention} hits {1.mention} with a pot"],
                                    "Bedroom": ["{0.mention} hits {1.mention} with a pillow", "{1.mention} takes a pillow to the head from {0.mention}"],
                                    "Living Room": ["{0.mention} hits {1.mention} with the TV remote", "{0.mention} uses the Wii controller as a club on {1.mention} *wii sports plays*","{1.mention} trips over the Skyrim CD sleeve, 00f"],
                                    "Backyard": ["{0.mention} hits {1.mention} with some tongs", "{0.mention} turns the backyard stove over on {1.mention}"]}

                    universalactions = ["{0.mention} slugs {1.mention} in the face", "{0.mention} uses *sicc* karate skills on {1.mention}", "{0.mention} pushes {1.mention} over"]

                    deathblows = {"Laundry Room": "{0.mention} shuts {1.mention} in the washer and starts it",
                                  "Dining Room": "{0.mention} pins {1.mention} agianst the table",
                                  "Kitchen": "{0.mention} uses top-notch ninja skills on {1.mention}, many of which involve the knives",
                                  "Bedroom": "{0.mention} gets a l33t hit om {1.mention} involving throwing the bedstand",
                                  "Living Room": "{0.mention} narrowly beats {1.mention} in a sword-fight using the Dolby 7:1 surround speakers",
                                  "Backyard": "{0.mention} throws some hot coals from the backyard stove at {1.mention}"}

                    connectedrooms = {"Laundry Room":["Backyard","Kitchen"], "Dining Room":["Kitchen","Backyard"], "Kitchen":["Dining Room","Living Room"],
                                      "Bedroom":["Living Room"], "Living Room":["Kitchen","Bedroom"], "Backyard":["Laundry Room","Laundry Room"]}

                    setting = random.choice(fightplaces)

                    p1.turn = True

                while p1.health > 0 and p2.health > 0:
                    askaction = await ctx.send(f"{findTurn().user.mention}, what do you want to do? `hit`, `run`, or `end`.")

                    def check(m):
                        if m.channel == ctx.channel and m.author == findTurn().user:
                            return m.content.lower().startswith("hit") or m.content.lower().startswith("run") or m.content.lower().startswith("end")
                        else:
                            return False

                    usrinput = await self.bot.wait_for("message", check = check)

                    if usrinput == None:
                        await ctx.send("it timed out noobs")
                        return
                    else:
                        if usrinput.content.lower().startswith("hit"):
                            damage = 0
                            rand = random.randint(1, 15)
                            if rand == 1:
                                blow = deathblows[setting].format(findTurn().user, findNotTurn().user)
                                blow += " (DEATHBLOW)"
                                damage = 100

                            elif rand > 9:
                                blow = random.choice(universalactions).format(findTurn().user, findNotTurn().user)
                                damage = random.randint(1, 50)

                            else:
                                blow = random.choice(fightactions[setting]).format(findTurn().user, findNotTurn().user)
                                damage = random.randint(1, 50)

                            blow += f" ({damage} dmg)"
                            currentaction = blow

                        elif usrinput.content.lower().startswith("run"):
                            newsetting = random.choice(connectedrooms[setting])

                            currentaction = f"{getTurn().user.mention} kicks {getNotTurn().user.mention} in the shins and runs as fast as he/she can out of the {setting} and into the {newsetting}. {getTurn().user.mention} gives chase."

                            setting = newsetting
                            newsetting = ""

                        elif usrinput.content.lower().startswith("end"):
                            await ctx.send(f"{findTurn().user.mention} and {findNotTurn().user.mention} get friendly and the fight's over.")
                            return

                        findNotTurn().health -= damage
                        if findNotTurn().health < 0:
                            findNotTurn().health = 0

                        emb = discord.Embed(name="FIGHT", color=findTurn().user.colour)

                        emb.add_field(name="Current Setting", value=f"`{setting}`")
                        emb.add_field(name="Player 1 health", value=f"**{p1.health}**")
                        emb.add_field(name="Player 2 health", value=f"**{p2.health}**")
                        emb.add_field(name="Current action", value=currentaction)

                        await ctx.send(embed=emb)
                        await askaction.delete()
                        await usrinput.delete()

                        switchturn()

                        await asyncio.sleep(3)

                if p1.health == 0:
                    p2.won = True
                    p1.won = False
                else:
                    p2.won = False
                    p1.won = True
                await ctx.send(f"Looks like {findwin().user.mention} defeated {findloser().user.mention} with {findwin().health} health left!")

def setup(bot):
    bot.add_cog(Randomizers(bot))
