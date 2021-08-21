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
import enum
import random

import discord

from .economy import do_economy_give, get_money_prefix

# C4 stuff from StarrFox/DiscordChan

C4_DIAGONALS = [
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


class C4:
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
        self.moves = []

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
        embed.add_field(name="Current move list", value=self.current_moves)
        return embed

    async def add_reactions(self):
        for r in self.emojis:
            await self.message.add_reaction(r)
        await self.message.add_reaction("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}")
        await self.message.add_reaction("\N{BLACK SQUARE FOR STOP}")

    async def find_free(self, num):
        for i in range(6)[::-1]:
            if self.board[i][num] == self.filler:
                return i

    async def parse_reaction(self, reaction):
        num = self.emojis.index(reaction)
        next_ = await self.find_free(num)
        if next_ is None:
            return
        self.board[next_][num] = self.red if self.current_player == self.player_one else self.blue
        await self.check_wins()
        self.is_first_run = False
        self.last_play = num
        self.moves.append(num + 1)
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
        for c4_d in C4_DIAGONALS:
            diagonals.append([self.board[i[0]][i[1]] for i in c4_d])
        for d in diagonals:
            if check_slice(d):
                self.is_running = False
                return

    def check_reaction(self, reaction, user):
        valid_emojis = self.emojis + ["\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}"]
        same_message = reaction.message.id == self.message.id
        curent_player_action = user == self.current_player and str(reaction) in valid_emojis
        player_reacted_with_stop = (user.id in (self.player_one.id, self.player_two.id)
                                    and str(reaction) == "\N{BLACK SQUARE FOR STOP}")

        return same_message and (curent_player_action or player_reacted_with_stop)

    async def do_game(self):
        self.message = await self.ctx.send(embed=self.make_embed())
        await self.add_reactions()
        while self.is_running:
            try:
                reaction, user = await self.ctx.bot.wait_for(
                    "reaction_add",
                    check=self.check_reaction,
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
            elif str(reaction) == "\N{BLACK SQUARE FOR STOP}":
                with contextlib.suppress(discord.HTTPException):
                    await self.message.clear_reactions()
                await self.message.edit(content=f"This game was stopped by {user.mention}.")
                return
            else:
                await self.parse_reaction(str(reaction))

        with contextlib.suppress(discord.HTTPException):
            await self.message.clear_reactions()

    @property
    def current_moves(self):
        ret = self.moves or "[no moves made]"

        if type(ret) != str:
            ret = "".join(map(str, ret))

        return ret


MASTERMIND_NONE = "\U00002754"


class MastermindColors(enum.Enum):
    BLACK = "\U00002b1b"
    WHITE = "\U00002b1c"
    RED = "\U0001f7e5"
    PURPLE = "\U0001f7ea"
    YELLOW = "\U0001f7e8"
    GREEN = "\U0001f7e9"


class MastermindEscapes(enum.Enum):
    BLACK = "\\:black_large_square:"
    WHITE = "\\:white_large_square:"
    RED = "\\:red_square:"
    PURPLE = "\\:purple_square:"
    YELLOW = "\\:yellow_square:"
    GREEN = "\\:green_square:"


class MastermindFeedback(enum.Enum):
    BLACK = ":white_check_mark:"
    WHITE = ":thinking:"
    BLANK = ":x:"


class Mastermind:
    def __init__(self, ctx):
        self.ctx = ctx
        self.code = [random.choice(list(MastermindColors)) for _ in range(4)]
        self.embed_footer = ""
        self.latest_messages = (None, None)
        self.guesses = [[MASTERMIND_NONE] * 4] * 24  # 24x4 of soon-to-be user guesses
        self.responses = [[MASTERMIND_NONE] * 4] * 24  # 24x4 of soon-to-be feedback codes
        self.latest_guess = [MASTERMIND_NONE] * 4
        self.round = 1
        self.last_messages = (None, None)

        self.possible_emotes = ["\U00002b1b", "\U00002b1c", "\U0001f7e5", "\U0001f7ea", "\U0001f7e8", "\U0001f7e9"]
        self.possible_letters = list("bwrpyg")

    async def send_embed(self):
        emb = self.ctx.default_embed()
        self.embed_footer = emb.footer.text
        emb.set_footer(text=self.embed_footer)  # Prevent footer from changing

        emb.title = "Mastermind"
        desc = []
        for index, guesses_and_responses in enumerate((zip(self.guesses, self.responses))):
            if self.is_empty_at(index) and self.is_empty_at(index - 1) and index != 0:
                continue

            guesses, responses = guesses_and_responses
            desc.append(
                f"`{(index + 1):02}`. {''.join(guesses)} \U000027a1 {''.join(responses)}"
            )
        description = "Your guess \U000027a1 My response:\n" + "\n".join(desc)

        # The following code is just the paginate_with_embeds function, but I want extra fields...
        by_line = description.split("\n")

        if len(by_line) > 12:
            part1 = "\n".join(by_line[:len(by_line) // 2])
            part2 = "\n".join(by_line[len(by_line) // 2:])

            emb1 = discord.Embed(description=part1, color=self.ctx.bot.embed_color)
            emb2 = discord.Embed(description=part2, color=self.ctx.bot.embed_color)
            emb3 = discord.Embed(color=self.ctx.bot.embed_color)

            emb1.set_author(name=self.ctx.me.name, icon_url=self.ctx.me.avatar_url)
            emb3.set_footer(
                text=f"{self.ctx.bot.embed_footer} Requested by {self.ctx.author}", icon_url=self.ctx.author.avatar_url)

            emb3.add_field(
                name="Formatting instructions",
                value="See the introduction message for formatting information.",
                inline=False
            )
            emb3.add_field(
                name="Had enough?",
                value="React with :stop_button: below to stop the game.",
                inline=False
            )

            m1 = await self.ctx.send(embed=emb1)
            m2 = await self.ctx.send(embed=emb2)
            m3 = await self.ctx.send(embed=emb3)
            await m3.add_reaction("\U000023F9")
            return m1, m2, m3
        else:
            part1 = "\n".join(by_line)
            emb1 = discord.Embed(description=part1, color=self.ctx.bot.embed_color)
            emb2 = discord.Embed(color=self.ctx.bot.embed_color)
            emb1.set_author(name=self.ctx.me.name, icon_url=self.ctx.me.avatar_url)
            emb2.set_footer(
                text=f"{self.ctx.bot.embed_footer} Requested by {self.ctx.author}", icon_url=self.ctx.author.avatar_url)

            emb2.add_field(
                name="Formatting instructions",
                value="See the introduction message for formatting information.",
                inline=False
            )
            emb2.add_field(
                name="Had enough?",
                value="React with :stop_button: below to stop the game.",
                inline=False
            )

            m1 = await self.ctx.send(embed=emb1)
            m2 = await self.ctx.send(embed=emb2)
            await m2.add_reaction("\U000023F9")

            return m1, m2

    def parse_message(self, content):
        content = content.strip()
        ret = []
        for char in content.strip():
            if char in self.possible_emotes:
                ret.append(char)
            elif char.lower() in self.possible_letters:
                ret.append(self.possible_emotes[self.possible_letters.index(char.lower())])

        if len(ret) != 4:
            return []

        return ret

    def validate_message(self, message):
        if message.author != self.ctx.author or message.channel != self.ctx.channel:
            return False

        parsed = self.parse_message(message.content)

        return parsed and parsed not in self.guesses

    def validate_reaction(self, reaction, user):
        if user != self.ctx.author or reaction.message.id != self.latest_messages[-1].id:
            return False

        return reaction.emoji == "\U000023F9"

    async def sendrules(self, to, ignore_optedout=False):
        resp = await self.ctx.bot.db_pool.fetchrow(
            "SELECT wins, intro_opt_out FROM mastermind WHERE user_id = $1;", self.ctx.author.id)

        if resp:
            wins, is_opted_out = resp[0], resp[1]
        else:
            wins = 0
            is_opted_out = 0

        if is_opted_out and not ignore_optedout:
            # The user is opted out and we are allowed to ignore it. Leave.
            return

        else:
            rules = "**Mastermind rules:**\n\nI have a code of four colors that you need to guess. The possible " \
                    "colors are black, white, red, blue, yellow, and green. *Repeat colors are possible in the code.*" \
                    "You get 24 attempts to guess the code before I reveal it.\nEvery time you guess the four-digit " \
                    "code, I will reply with another four-digit code:\nA :white_check_mark: means your digit is of " \
                    "the correct color, and is in the right place.\nA :thinking: means your digit is of the correct " \
                    "color, but it needs to be in a different spot.\nFinally, :x: means your digit is the wrong " \
                    "color, and you need to try a different color.\n\nThe four-digit code I give you after a guess " \
                    "is in no particular order. This means that if the first digit in my response is " \
                    ":white_check_mark:, that does not *necessarily* mean that the first digit of your guess was " \
                    "correct.\n\nOn every round, type a guess using the following emojis:\n"

            rules += "\n".join(
                [f"{c.value}: {e.value}" for c, e in zip(list(MastermindColors), list(MastermindEscapes))])
            rules += "\nYou can also use the first letter of a color instead of the emoji.\n**WRITE YOUR ENTIRE CODE " \
                     "IN ONE MESSAGE. BE CAREFUL - THERE IS NO WAY TO CHANGE YOUR GUESS!**\nRepeat guesses are " \
                     "useless, so I will ignore you if you try to guess something you've already tried.\n\nBefore " \
                     "you play, a few hints:\nRemember to use your feedback to your advantage. If you get, for " \
                     "example, :white_check_mark::white_check_mark::thinking::thinking:, you know that the colors in " \
                     "your latest guess should not be changed, and that you should keep reordering them until you " \
                     "win.\nA good starting strategy is to guess as many different colors as possible, then use the " \
                     "feedback to figure out which colors belong and which don't.\nYou have 24 tries at cracking the " \
                     "code.""\n**Please react with a :white_check_mark: below to start the game.**\nGood luck " \
                     "beating the Mastermind!"

            if wins >= 5:
                rules += f"\n\nP.S.: Since you have won more than 5 games, you can opt out of the introduction " \
                         f"message (or back in) using `{self.ctx.prefix}{self.ctx.invoked_with} toggleintro`."

            return await to.send(rules)

    async def start(self):
        try:
            msg = await self.sendrules(self.ctx.author)
        except discord.Forbidden:
            msg = await self.sendrules(self.ctx)
        except discord.NotFound:  # lol why did you delete your account in the middle of a mastermind game
            return

        await msg.add_reaction("\U00002705")
        try:
            await self.ctx.bot.wait_for(
                "reaction_add",
                check=lambda r, u: u == self.ctx.author and r.emoji == "\U00002705" and r.message.id == msg.id,
                timeout=60.0
            )
        except asyncio.TimeoutError:
            return

        return True

    async def run(self):
        while True:
            if self.round >= 25:
                break

            self.last_messages = self.latest_messages
            for message in self.last_messages:
                if message is not None:
                    try:
                        await message.delete()
                    except discord.NotFound:
                        pass

            self.latest_messages = await self.send_embed()

            if self.latest_guess == [c.value for c in self.code]:
                break

            done, pending = await asyncio.wait(
                [self.ctx.bot.wait_for("message", check=self.validate_message, timeout=120.0),
                 self.ctx.bot.wait_for("reaction_add", check=self.validate_reaction, timeout=120.0)],
                return_when=asyncio.FIRST_COMPLETED
            )

            try:
                finished_task = done.pop().result()
            except discord.HTTPException:
                return  # An error means something is wrong enough to end the game.
            except asyncio.TimeoutError:
                break

            for future in pending:
                future.cancel()  # In the last words of John Wilkes Booth: useless, useless.

            if isinstance(finished_task, tuple):  # This would denote that the return is from a reaction_add event
                break
            else:
                u_input = self.parse_message(finished_task.content.strip())

                guesses = [list(MastermindColors)[self.possible_emotes.index(e)] for e in u_input]

                black_count = 0
                white_count = 0
                blank_count = 0

                for color in MastermindColors:
                    color_count_in_code = self.code.count(color)
                    color_count_in_guess = guesses.count(color)

                    while color_count_in_code and color_count_in_guess:
                        white_count += 1
                        color_count_in_code -= 1
                        color_count_in_guess -= 1

                for index in range(0, 4):
                    if guesses[index] == self.code[index]:
                        white_count -= 1
                        black_count += 1

                blank_count += 4 - (white_count + black_count)

                self.guesses[self.round - 1] = [g.value for g in guesses]
                self.latest_guess = [g.value for g in guesses]
                self.responses[self.round - 1] = (
                        [MastermindFeedback.BLACK.value] * black_count
                        + [MastermindFeedback.WHITE.value] * white_count
                        + [MastermindFeedback.BLANK.value] * blank_count
                )

            self.round += 1

        to_send = f"Game over! The code was {''.join([c.value for c in self.code])}."
        if self.latest_guess == [c.value for c in self.code]:
            beaten_at = self.round - 1
            guesses_count_bonus = int((max(-1 / 8 * (beaten_at ** 2) + 30, 0)) // 1)
            base_payout = 100
            payout = base_payout + guesses_count_bonus
            await do_economy_give(self.ctx, self.ctx.author, payout)

            currency_prefix = await get_money_prefix(self.ctx)
            if guesses_count_bonus:
                to_send += f"\nYou also earned {currency_prefix}{payout}:\n{currency_prefix}{base_payout} for " \
                           f"beating the game and {currency_prefix}{guesses_count_bonus} for winning in {beaten_at} " \
                           f"rounds."
            else:
                to_send += f"\nYou also earned {currency_prefix}{payout}."

            current_wins = (await self.ctx.bot.db_pool.fetchval("SELECT wins FROM mastermind WHERE user_id = $1;",
                                                                self.ctx.author.id)) or 0

            await self.ctx.bot.db_pool.execute(
                "INSERT INTO mastermind (user_id, wins, intro_opt_out) VALUES ($1, $2, 0) ON CONFLICT (user_id) DO "
                "UPDATE SET wins = $2;", self.ctx.author.id, current_wins)

        await self.ctx.send(to_send)

    def is_empty_at(self, index):
        try:
            return self.guesses[index] == [MASTERMIND_NONE] * 4 and self.responses[index] == [MASTERMIND_NONE] * 4
        except IndexError:
            return False


def roll_XdY(x, y, *, return_rolls=False):
    if not isinstance(x, int) or not isinstance(y, int):
        raise TypeError
    ret = 0
    if return_rolls:
        rolls = []
        for _ in range(x):
            roll = random.randint(1, y + 1)
            rolls.append(roll)
            ret += roll
        return ret, rolls
    else:
        for _ in range(x):
            ret += random.randint(1, y + 1)
        return ret
