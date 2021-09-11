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
import collections
import contextlib
import copy
import enum
import random

import discord

from .economy import do_economy_give, get_money_prefix
from .format_and_convert import Plural

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
                return
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

        await do_economy_give(self.ctx, self.current_player, 130)
        await self.ctx.send(
            f"{self.current_player.mention} has received {await get_money_prefix(self.ctx, self.ctx.guild.id)}130 for "
            f"winning Connect 4.")

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

        if len(message.content) > 5:
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
                    "colors are black, white, red, blue, yellow, and green. *Repeat colors are possible in the " \
                    "code.* You get 24 attempts to guess the code before I reveal it.\nEvery time you guess the " \
                    "four-digit code, I will reply with another four-digit code:\nA :white_check_mark: means your " \
                    "digit is of the correct color, and is in the right place.\nA :thinking: means your digit is of " \
                    "the correct color, but it needs to be in a different spot.\nFinally, :x: means your digit is " \
                    "the wrong color, and you need to try a different color.\n\nThe four-digit code I give you after " \
                    "a guess is in no particular order. This means that if the first digit in my response is " \
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
        msg = None

        try:
            msg = await self.sendrules(self.ctx.author)
        except discord.Forbidden:
            msg = await self.sendrules(self.ctx)
        except discord.NotFound:  # lol why did you delete your account in the middle of a mastermind game
            return

        if msg is not None:
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
            base_payout = 75
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
                "UPDATE SET wins = $2;", self.ctx.author.id, current_wins + 1)

        await self.ctx.send(to_send)

    def is_empty_at(self, index):
        try:
            return self.guesses[index] == [MASTERMIND_NONE] * 4 and self.responses[index] == [MASTERMIND_NONE] * 4
        except IndexError:
            return False


# TODO: cards for DOS and/or UNO ATTACK

@enum.unique
class UnoColor(enum.IntEnum):
    WILD = 0
    BLUE = 1
    GREEN = 2
    RED = 3
    YELLOW = 4


@enum.unique
class UnoSpecialType(enum.IntEnum):
    DRAW_2 = 10
    REVERSE = 11
    SKIP = 12
    WILD = 13
    WILD_4 = 14


# color, type, number in deck
@enum.unique
class UnoCard(enum.Enum):
    WILD = (UnoColor.WILD, UnoSpecialType.WILD, 4)
    WILD_4 = (UnoColor.WILD, UnoSpecialType.WILD_4, 4)

    BLUE_0 = (UnoColor.BLUE, 0, 1)
    BLUE_1 = (UnoColor.BLUE, 1, 2)
    BLUE_2 = (UnoColor.BLUE, 2, 2)
    BLUE_3 = (UnoColor.BLUE, 3, 2)
    BLUE_4 = (UnoColor.BLUE, 4, 2)
    BLUE_5 = (UnoColor.BLUE, 5, 2)
    BLUE_6 = (UnoColor.BLUE, 6, 2)
    BLUE_7 = (UnoColor.BLUE, 7, 2)
    BLUE_8 = (UnoColor.BLUE, 8, 2)
    BLUE_9 = (UnoColor.BLUE, 9, 2)
    BLUE_DRAW_2 = (UnoColor.BLUE, UnoSpecialType.DRAW_2, 2)
    BLUE_REVERSE = (UnoColor.BLUE, UnoSpecialType.REVERSE, 2)
    BLUE_SKIP = (UnoColor.BLUE, UnoSpecialType.SKIP, 2)

    GREEN_0 = (UnoColor.GREEN, 0, 1)
    GREEN_1 = (UnoColor.GREEN, 1, 2)
    GREEN_2 = (UnoColor.GREEN, 2, 2)
    GREEN_3 = (UnoColor.GREEN, 3, 2)
    GREEN_4 = (UnoColor.GREEN, 4, 2)
    GREEN_5 = (UnoColor.GREEN, 5, 2)
    GREEN_6 = (UnoColor.GREEN, 6, 2)
    GREEN_7 = (UnoColor.GREEN, 7, 2)
    GREEN_8 = (UnoColor.GREEN, 8, 2)
    GREEN_9 = (UnoColor.GREEN, 9, 2)
    GREEN_DRAW_2 = (UnoColor.GREEN, UnoSpecialType.DRAW_2, 2)
    GREEN_REVERSE = (UnoColor.GREEN, UnoSpecialType.REVERSE, 2)
    GREEN_SKIP = (UnoColor.GREEN, UnoSpecialType.SKIP, 2)

    RED_0 = (UnoColor.RED, 0, 1)
    RED_1 = (UnoColor.RED, 1, 2)
    RED_2 = (UnoColor.RED, 2, 2)
    RED_3 = (UnoColor.RED, 3, 2)
    RED_4 = (UnoColor.RED, 4, 2)
    RED_5 = (UnoColor.RED, 5, 2)
    RED_6 = (UnoColor.RED, 6, 2)
    RED_7 = (UnoColor.RED, 7, 2)
    RED_8 = (UnoColor.RED, 8, 2)
    RED_9 = (UnoColor.RED, 9, 2)
    RED_DRAW_2 = (UnoColor.RED, UnoSpecialType.DRAW_2, 2)
    RED_REVERSE = (UnoColor.RED, UnoSpecialType.REVERSE, 2)
    RED_SKIP = (UnoColor.RED, UnoSpecialType.SKIP, 2)

    YELLOW_0 = (UnoColor.YELLOW, 0, 1)
    YELLOW_1 = (UnoColor.YELLOW, 1, 2)
    YELLOW_2 = (UnoColor.YELLOW, 2, 2)
    YELLOW_3 = (UnoColor.YELLOW, 3, 2)
    YELLOW_4 = (UnoColor.YELLOW, 4, 2)
    YELLOW_5 = (UnoColor.YELLOW, 5, 2)
    YELLOW_6 = (UnoColor.YELLOW, 6, 2)
    YELLOW_7 = (UnoColor.YELLOW, 7, 2)
    YELLOW_8 = (UnoColor.YELLOW, 8, 2)
    YELLOW_9 = (UnoColor.YELLOW, 9, 2)
    YELLOW_DRAW_2 = (UnoColor.YELLOW, UnoSpecialType.DRAW_2, 2)
    YELLOW_REVERSE = (UnoColor.YELLOW, UnoSpecialType.REVERSE, 2)
    YELLOW_SKIP = (UnoColor.YELLOW, UnoSpecialType.SKIP, 2)


@enum.unique
class UnoTurnOrder(enum.IntEnum):
    FORWARD = 1
    BACKWARD = -1

    @classmethod
    def reverse_of(cls, direction):
        if direction is cls.FORWARD:
            return cls.BACKWARD
        else:
            return cls.FORWARD


class UnoBase:
    def __init__(self, ctx):
        self.ctx = ctx

        self.started = False

        self.lobby_message = None
        self.times_joined = {}
        self.players = []
        self.players_ready = []

        self.previous_player = None
        self.starting_players = []
        self.winning_players = []  # index 0 is #1, etc

        self.game_message = None

        self.player_hands = {}
        self.times_skipped = {}

        self.call_emoji = "\U0000203c\U0000fe0f"
        self.last_player_called_on = None

        self.notes = []  # a list of important things like eliminations

        self.turn_order = UnoTurnOrder.FORWARD
        self.play_pointer = 0
        self.should_skip = False

        self.draw_pile = []
        self.discard_pile = []
        self.latest_wild_color = None

        # TODO: move references to UnoCard to a new StockUnoBase containing the rules for UNO but not variations

    async def add_player(self, member):
        if member in self.players:
            await self.ctx.send(f"{member.mention} you are already in this game.", delete_after=10)
            return False

        if self.times_joined.get(member, 0) <= 2:
            self.players.append(member)
            self.times_skipped[member] = 0
            self.player_hands[member] = []
            if await self.ctx.cog.uno_autoready_status(self.ctx, member):
                self.add_ready(member)
            if member not in self.times_joined:
                self.times_joined[member] = 0

            self.times_joined[member] += 1

            self.ctx.bot.dispatch("uno_player_add", self, member)
        else:
            await self.ctx.send(f"{member.mention} you cannot rejoin the game as you have already left it twice.",
                                delete_after=10)
            return False

        return True

    def remove_player(self, member):
        try:
            del self.players[self.players.index(member)]
            self.remove_ready(member)
            self.ctx.bot.dispatch("uno_player_remove", self, member)
            return True
        except ValueError:
            return False

    def add_ready(self, member):
        if not self.started:
            if member not in self.players_ready:
                self.players_ready.append(member)

            self.ctx.bot.dispatch("uno_player_ready_add", self, member)

    def remove_ready(self, member):
        if not self.started:
            while member in self.players_ready:
                del self.players_ready[self.players_ready.index(member)]

            self.ctx.bot.dispatch("uno_player_ready_remove", self, member)

    @property
    def rules(self):
        raise NotImplementedError

    async def update_lobby_message(self):
        if len(self.players) < 1:
            msg_content = "This Uno game has been aborted for some reason."
            embed = None
        else:
            invocation = f"{self.ctx.prefix}{self.ctx.command}"
            msg_content = "Please read the rules below. Joining and leaving more than twice will result in " \
                          "exclusion from the game (though you can join the next one).\n\n"

            if len(self.players) < 2:
                msg_content += "Players have 5 minutes to join the game."
            else:
                msg_content += "If noone joins or leaves in the next two minutes, and noone joins in the minute " \
                               "after, the game starts."

            msg_content += "\n\n\n" + self.rules

            embed = self.ctx.default_embed()
            embed.add_field(name="Players in the lobby", value=" ".join([u.mention for u in self.players]) or "Nobody",
                            inline=False)

            not_ready_mentions = " ".join(u.mention for u in tuple(set(self.players) - set(self.players_ready)))
            embed.add_field(name="Ready players", value=" ".join(u.mention for u in self.players_ready) or "Nobody")
            embed.add_field(name="Not ready players", value=not_ready_mentions or "Nobody")

            embed.description = f"Type `{invocation}` to join the game.\nType `{invocation} leave` to leave the " \
                                f"game.\nYou may also ready up with `{invocation} ready` or unready with " \
                                f"`{invocation} unready`. If all players in a lobby are ready, the game begins with " \
                                f"no warning.\n\nIf you want to automatically ready upon joining, look into " \
                                f"`{invocation} autoready`."

        if self.lobby_message is not None:
            try:
                await self.lobby_message.edit(content=msg_content, embed=embed)
                return
            except discord.HTTPException:
                pass

        try:
            self.lobby_message = await self.ctx.send(msg_content, embed=embed)
        except (discord.HTTPException, discord.Forbidden):
            self.ctx.bot.dispatch("uno_game_destroy", self)

    def uno_event_check(self, game, *args):
        return game is self

    async def await_players(self):
        if self.started:
            return

        while True:
            await self.update_lobby_message()
            if len(self.players) == 0:
                return False  # nobody wants to play :(
            elif len(self.players) < 2:  # one player, we should wait longer
                try:
                    done, pending = await asyncio.wait(
                        [self.ctx.bot.wait_for("uno_player_add", check=self.uno_event_check, timeout=300.0),
                         self.ctx.bot.wait_for("uno_player_remove", check=self.uno_event_check),
                         self.ctx.bot.wait_for("uno_game_destroy", check=self.uno_event_check),
                         self.ctx.bot.wait_for("uno_player_ready_add", check=self.uno_event_check),
                         self.ctx.bot.wait_for("uno_player_ready_remove", check=self.uno_event_check)],
                        return_when=asyncio.FIRST_COMPLETED
                    )

                    try:
                        # If this was a player change, we have two return values. If this was a destroy, we have one.
                        if len(done.pop().result()) < 2:
                            return False
                        for future in pending:
                            future.cancel()
                        continue
                    except discord.HTTPException:
                        return False  # something bad happened
                    except asyncio.TimeoutError:
                        # we have timed out waiting for players to join. abort
                        return False

                except asyncio.TimeoutError:
                    return False
            else:  # there are multiple players seated. wait for join and leave.
                if len(self.players_ready) == len(self.players):
                    # everyone is ready!
                    return True

                done, pending = await asyncio.wait(
                    [self.ctx.bot.wait_for("uno_player_add", check=self.uno_event_check, timeout=180.0),
                     self.ctx.bot.wait_for("uno_player_remove", check=self.uno_event_check, timeout=120.0),
                     self.ctx.bot.wait_for("uno_game_destroy", check=self.uno_event_check),
                     self.ctx.bot.wait_for("uno_player_ready_add", check=self.uno_event_check),
                     self.ctx.bot.wait_for("uno_player_ready_remove", check=self.uno_event_check)],
                    return_when=asyncio.FIRST_COMPLETED
                )

                try:
                    # If this was a player change, we have two return values. If this was a destroy, we have one.
                    if len(done.pop().result()) < 2:
                        return False
                    for future in pending:
                        future.cancel()
                    continue
                except discord.HTTPException:
                    return False  # something bad happened
                except asyncio.TimeoutError:
                    # we have timed out waiting. start!
                    return True

    def render_card(self, card, only_type=False):
        raise NotImplementedError

    def advance_play_pointer(self, direction, mock=False):
        if not self.started:
            return

        new_pointer = self.play_pointer + direction

        if new_pointer < 0:
            new_pointer = len(self.players) - 1
        elif new_pointer >= len(self.players):
            new_pointer = 0

        if not mock:
            self.play_pointer = new_pointer

        return new_pointer

    def create_all_cards(self):
        for card in UnoCard:
            _, _, count = card.value
            self.draw_pile += [card] * count

        random.shuffle(self.draw_pile)

    def initialize_discard_pile(self):
        # TODO: assume there is one draw pile, which is invalid for DOS

        # continue drawing until we find a non-wild. place that on the discard pile, reshuffle the rest into the draw
        # pile
        popped = [self.draw_pile.pop()]
        while popped[-1].value[0] is UnoColor.WILD:
            popped.append(self.draw_pile.pop())
        self.discard_pile.append(popped.pop())

        self.draw_pile += popped
        random.shuffle(self.draw_pile)

    def deal_to_players(self):
        for player in self.players:
            for _ in range(7):
                self.draw_card_for(player)

    def draw_card_for(self, player):
        # this is different in different variants
        raise NotImplementedError

    async def update_game_message(self):
        raise NotImplementedError

    async def play_card_and_process(self, player, card):
        raise NotImplementedError

    def is_playable(self, card, onto):
        raise NotImplementedError

    async def request_play(self):
        raise NotImplementedError

    @property
    def current_player(self):
        return self.players[self.play_pointer]

    @property
    def current_hand(self):
        return self.player_hands[self.current_player]

    def check_call(self, reaction, user, as_check=True):
        """check UNO, DOS, etc. calls"""
        raise NotImplementedError

    def prepare_to_start(self):
        self.create_all_cards()
        self.initialize_discard_pile()
        self.starting_players = copy.copy(self.players)

        self.started = True

        self.deal_to_players()
        # Assume joining order is identical to seating order. Pick a random person to go first.
        self.play_pointer = random.randrange(0, len(self.players))
        self.notes.append(f"{self.current_player.mention} has been selected to play first.")

    async def run(self):
        raise NotImplementedError

    async def do_payout(self, member):
        try:
            ranking = self.winning_players.index(member) + 1
        except IndexError:
            raise IndexError from None

        starting_player_count = len(self.starting_players)

        initial = 75 * (1 / ranking) * (starting_player_count / 3)
        linear_correction = 50 * (starting_player_count - ranking)

        ret = int(round(initial + linear_correction + 50))

        await do_economy_give(self.ctx, member, ret)
        return ret


class UnoDefault(UnoBase):
    @property
    def rules(self):
        return "Rules are here: https://service.mattel.com/instruction_sheets/42001pr.pdf\n**The following " \
               "modifications have been made to the winning conditions:**\n\nThe first player to run out " \
               "of cards is first place. Play continues with the person who would have played next, skipping the " \
               "player(s) who are already out of the game. The next player to run out is second place, and so on, " \
               "until only one player remains. The last place player receives no money, and payouts increase with " \
               "ranking.\n\nThis change is often made at tables to shorten the game, as under the original rules " \
               "(which are still playable via <NOT IMPLEMENTED>) the game repeats itself up to several times to " \
               "produce a winner."

    def render_card(self, card, only_type=False):
        color, type, _ = card.value

        resolved_type = ""

        if type < 10:  # i.e. not special
            resolved_type += str(type)
        else:
            if type is UnoSpecialType.DRAW_2:
                resolved_type = "+2"
            elif type is UnoSpecialType.REVERSE:
                resolved_type = "Reverse"
            elif type is UnoSpecialType.SKIP:
                resolved_type = "Skip"
            elif type is UnoSpecialType.WILD_4:  # wild means add nothing
                resolved_type = "+4"
            elif type is UnoSpecialType.WILD:
                resolved_type = "Regular wild" if only_type else ""

        if only_type:
            return resolved_type

        ret = ""

        ret += {UnoColor.WILD: "Wild", UnoColor.BLUE: "Blue",
                UnoColor.GREEN: "Green", UnoColor.RED: "Red", UnoColor.YELLOW: "Yellow"}[color.value]

        ret += (" " + resolved_type) if resolved_type else ""
        return ret

    def draw_card_for(self, player):
        if not self.draw_pile:
            reshufflable_cards = self.discard_pile[:-1]  # everything but the top card
            random.shuffle(reshufflable_cards)
            self.draw_pile = reshufflable_cards

            self.notes.append("The draw pile was exhausted and the discard pile was shuffled to become the new draw"
                              "pile.")

        drawn = self.draw_pile.pop()
        self.player_hands[player].append(drawn)
        return drawn

    async def update_game_message(self):
        msg_content = "On your turn, you will be privately messaged regarding your move.\n**You have two minutes to " \
                      "play a card. Failure to do so twice in a row will disqualify you from the game with no chance " \
                      "for earnings.**"

        emb = self.ctx.default_embed(no_footer=True)
        emb.add_field(name="Currently playing", value=self.current_player.mention)
        emb.add_field(name="Next up", value=self.players[self.advance_play_pointer(self.turn_order, mock=True)].mention)
        emb.add_field(name="Top of discard pile",
                      value=", ".join("**" + self.render_card(c) + "**" for c in reversed(self.discard_pile[-3:])))
        emb.add_field(name="Players", value=" ".join(u.mention for u in self.players))

        if len(self.players) > 2:  # If there are 2 players left, everyone knows the turn order.
            emb.add_field(
                name="Next player", value=self.players[self.advance_play_pointer(self.turn_order, mock=True)].mention)

        if self.winning_players:
            emb.add_field(name="Rankings (#1 1st)", value=" ".join(u.mention for u in self.winning_players))

        if self.notes:
            emb.add_field(inline=False,
                          name="Game state notes", value="\n".join("**" + c + "**" for c in reversed(self.notes[-3:])))

        small_hands = {}
        for u, hand in self.player_hands.items():
            if len(hand) < 5:
                small_hands[u] = len(hand)

        if small_hands:
            emb.description = f"The following players have low card counts (under 5). Lines in bold denote players " \
                              f"who, __on their turn__, if they have 1 card, can call UNO. If this player fails to " \
                              f"call UNO, they can be \"caught\" by someone else calling UNO first and forced to " \
                              f"draw 4 cards. **Call UNO by reacting with {self.call_emoji}** below:\n\n"
            to_append = []

            for user, count in small_hands.items():
                if count > 1:
                    to_append.append(f"{user.mention}: {count}")
                else:
                    to_append.append(f"**__{user.mention}: {count}__**")
            emb.description += "\n".join(to_append)

        if self.game_message is not None:
            with contextlib.suppress(discord.DiscordException):
                await self.game_message.delete()
        self.game_message = await self.ctx.send(msg_content, embed=emb)
        await self.game_message.add_reaction(self.call_emoji)

    async def play_card_and_process(self, player, card):
        if card.value[0] is UnoColor.WILD:
            self.latest_wild_color = None
            sent = await player.send("You have played a wild card, meaning you can choose its color. What color would "
                                     "you like?")
            reactions = {
                "\U0001f7e6": UnoColor.BLUE,
                "\U0001f7e9": UnoColor.GREEN,
                "\U0001f7e5": UnoColor.RED,
                "\U0001f7e8": UnoColor.YELLOW
            }
            for e in reactions.keys():
                await sent.add_reaction(e)

            def check_event(reaction, user):
                if user != player:
                    return False

                if str(reaction.emoji) not in reactions.keys():
                    return False

                return True

            reaction_out, _ = await self.ctx.bot.wait_for("reaction_add", check=check_event)
            self.latest_wild_color = reactions[str(reaction_out)]
            self.notes.append(f"Wild card played by {player.mention} is {reaction_out}.")
        else:
            self.latest_wild_color = None

        if card.value[1] is UnoSpecialType.SKIP:
            victim = self.players[self.advance_play_pointer(self.turn_order, mock=True)]
            self.should_skip = True
            self.notes.append(f"Skipped {victim.mention} because of {player.mention}'s skip card.")
        elif card.value[1] is UnoSpecialType.DRAW_2:
            victim = self.players[self.advance_play_pointer(self.turn_order, mock=True)]
            for _ in range(2):
                self.draw_card_for(victim)
            self.notes.append(f"{victim.mention} drew two cards because of {player.mention}'s draw 2 card.")
        elif card.value[1] is UnoSpecialType.WILD_4:
            victim = self.players[self.advance_play_pointer(self.turn_order, mock=True)]
            for _ in range(4):
                self.draw_card_for(victim)
            self.notes.append(f"{victim.mention} drew four cards because of {player.mention}'s draw 4 card.")
        elif card.value[1] is UnoSpecialType.REVERSE:
            if len(self.players) > 2:
                self.turn_order = UnoTurnOrder.reverse_of(self.turn_order)

                self.notes.append(f"Turn order has changed due to {player.mention}'s reverse card.")
            else:
                self.should_skip = True
                self.notes.append(f"{player.mention}'s reverse acts as a skip card as there are 2 players left.")

        try:
            del self.player_hands[player][self.player_hands[player].index(card)]
            self.discard_pile.append(card)
            return True
        except IndexError:
            return False

    def is_playable(self, card, onto):
        if card.value[0] is UnoColor.WILD:
            return True  # you can play a wild on anything

        color = self.latest_wild_color or onto.value[0]

        if card.value[0] == color:
            return True

        elif onto.value[1] == card.value[1]:
            return True

        return False

    async def request_play(self):
        hand = self.current_hand
        fmt_card_list = []
        total_cards = 0
        color_to_cards = collections.defaultdict(list)
        playable_cards = []

        for color_name, color in UnoColor.__members__.items():
            type_counts = collections.Counter(c for c in hand if c.value[0] is color)
            for card, count in type_counts.items():
                color_to_cards[color] += [card] * count

            total_cards += len(color_to_cards[color])
            color_to_cards[color].sort(key=lambda c: c.value)
            # recreate the list as a sorted version of the following:
            # for every card, render it. if it is playable on top of the discard pile, bold and underline.
            rendered_cards = []
            for c in sorted(color_to_cards[color], key=lambda c: c.value[1]):
                if self.is_playable(c, self.discard_pile[-1]):
                    rendered_cards.append(f"**__{self.render_card(c, only_type=True)}__**")
                    playable_cards.append(c)
                else:
                    rendered_cards.append(self.render_card(c, only_type=True))

            if rendered_cards:
                fmt_card_list.append(color_name.title() + ":\n" + ", ".join(rendered_cards))

        fmt_card_list = "\n\n".join(fmt_card_list)

        emb = self.ctx.default_embed(no_footer=True)
        emb.description = f"The above is your hand of {format(Plural(total_cards), 'card')}. **You have two minutes " \
                          f"to complete your move. If you run out of time on two turns in a row, you will be " \
                          f"disqualified.**"
        if playable_cards:
            emb.description += " Highlighted cards are playable.\n\nYou may either type a number to play - for " \
                               "example, type 1 to play your first playable card, and so on - or type `draw` to draw " \
                               "a card. If you draw a card which is playable, you may also play it (but you may not " \
                               "play any other card from your hand). Drawing by choice is also known as reneging."

            def process_action(msg, behave_as_check=True):
                content = msg.content.strip().lower()

                if msg.channel != self.current_player.dm_channel:
                    return False if behave_as_check else (None, None)

                if content == "draw":
                    return True if behave_as_check else (self.draw_card_for(self.current_player), True)

                try:
                    ind = int(content)
                except ValueError:
                    return False if behave_as_check else (None, None)

                if not (1 <= ind <= len(playable_cards)):
                    return False if behave_as_check else (None, None)
                return True if behave_as_check else (playable_cards[ind - 1], False)

            await self.current_player.send(fmt_card_list, embed=emb)

            # no timeout because that's handled elsewhere
            reply = await self.ctx.bot.wait_for("message", check=process_action)
            out_card, was_drawn = process_action(reply, behave_as_check=False)
            if out_card is None:
                await self.ctx.send("this is not supposed to happen")
                while True:
                    # lol
                    pass
            # note: execution always comes here normally so no else or anything

            if was_drawn:
                if self.is_playable(out_card, self.discard_pile[-1]):
                    await self.current_player.send(
                        f"You draw this card, which is also playable:\n> {self.render_card(out_card)}\nWould you like "
                        f"to play it (yes) or keep it until next turn (no)? If you answer with something other than "
                        f"yes or no, you will play the card.")

                    def confirmation_check(m):
                        if m.channel != self.current_player.dm_channel:
                            return False

                        return True

                    reply = await self.ctx.bot.wait_for("message", check=confirmation_check)
                    if reply.content.strip().startswith("n"):
                        await self.current_player.send(
                            "You are keeping this card. Return to the server containing the game to watch the game "
                            "play out.")
                        self.notes.append(f"{self.current_player.mention} drew a card and kept it.")
                        return
                    else:
                        # note: this appears incorrect as we should be playing from a separate card object containing
                        # the newly drawn card, however that card was placed in the hand so this is correct
                        await self.current_player.send(
                            "You played this card. Return to the server containing the game to watch the game play "
                            "out.")
                        await self.play_card_and_process(self.current_player, out_card)
                        return
                else:
                    await self.current_player.send(
                        f"You drew this card:\n> {self.render_card(out_card)}\nIt is not playable. Return to the "
                        f"server containing the game to watch the game play out.")
                    self.notes.append(f"{self.current_player.mention} drew a card and kept it.")
                    return
            else:
                await self.play_card_and_process(self.current_player, out_card)
                await self.current_player.send(
                    f"You played this card from your hand:\n> {self.render_card(out_card)}\nReturn to the server "
                    f"containing the game to watch the game play out.")
                return

        else:
            drawn = self.draw_card_for(self.current_player)
            content = f"\n\nYou have no playable cards, so you drew the following card from the deck:\n> " \
                      f"{self.render_card(drawn)}\n"
            if self.is_playable(drawn, self.discard_pile[-1]):
                await self.current_player.send(fmt_card_list, embed=emb)
                content += "This card is playable, so you are forced to play it.\nReturn to the server " \
                           "containing the game to watch the game play out."
                await self.current_player.send(content)
                await self.play_card_and_process(self.current_player, drawn)
            else:
                await self.current_player.send(fmt_card_list, embed=emb)
                content += "This card is not playable, so you will keep it.\nReturn to the server " \
                           "containing the game to watch the game play out."
                await self.current_player.send(content)
                self.notes.append(f"{self.current_player.mention} drew a card and kept it.")

            return

    def check_call(self, reaction, user, as_check=True):
        if as_check:
            if reaction.message != self.game_message:
                return False

            if user not in self.players:
                return False

            if str(reaction.emoji) != self.call_emoji:
                return False

        if self.previous_player is not None:
            prev_hand_was_uno = len(self.player_hands[self.previous_player]) == 1
        else:
            prev_hand_was_uno = False

        if as_check:
            if not (len(self.current_hand) == 1 or prev_hand_was_uno):
                return False

            return self.last_player_called_on is None
        else:
            if prev_hand_was_uno:
                self.last_player_called_on = self.previous_player
                return self.previous_player
            elif len(self.current_hand) == 1:
                self.last_player_called_on = self.current_player
                return self.current_player
            else:
                raise ValueError  # we should never be here but let's raise this in case we somehow end up here

    async def run(self):
        self.prepare_to_start()

        while len(self.players) > 1:
            await self.update_game_message()

            try:
                done, pending = await asyncio.wait([
                    asyncio.wait_for(self.request_play(), timeout=120.0),
                    self.ctx.bot.wait_for("reaction_add", check=self.check_call)
                ], return_when=asyncio.FIRST_COMPLETED)
                finished_task = done.pop().result()
                returned_from_reaction = isinstance(finished_task, tuple)

                if not returned_from_reaction:  # only kill the reaction wait_for, not requesting a move
                    for future in pending:
                        future.cancel()

                    self.last_player_called_on = None
                else:
                    called_against = self.check_call(*finished_task, as_check=False)
                    who_called = finished_task[1]
                    if who_called == called_against:
                        #  someone called uno on themselves, this is fine
                        self.notes.append(f"{who_called.mention} called UNO on themselves and avoided drawing cards.")
                        pass
                    else:
                        for _ in range(4):
                            self.draw_card_for(called_against)
                        self.notes.append(f"{called_against.mention} failed to call UNO and was caught by "
                                          f"{who_called.mention} and is forced to draw 4 cards.")

                self.times_skipped[self.current_player] = 0

                if len(self.current_hand) < 1:
                    self.winning_players.append(self.current_player)
                    rnk = len(self.winning_players)
                    self.notes.append(
                        f"{self.current_player.mention} has reached 0 cards, becoming #{rnk}.")

                    self.previous_player = None
                    del self.players[self.play_pointer]
                    continue  # don't increment play pointer here either
            except discord.HTTPException:
                return
            except asyncio.TimeoutError:
                # L
                with contextlib.suppress(discord.DiscordException):
                    await self.current_player.send("**Time has expired. It is no longer your turn.**")

                self.times_skipped[self.current_player] += 1
                if self.times_skipped[self.current_player] > 1:
                    self.notes.append(f"Eliminated {self.current_player.mention} for idling.")

                    self.previous_player = None
                    del self.players[self.play_pointer]
                    continue  # don't advance the play pointer as this would skip the next person
                else:
                    self.notes.append(f"{self.current_player.mention} has failed to move in time.")

            self.previous_player = self.current_player
            self.advance_play_pointer(self.turn_order)
            if self.should_skip:
                self.should_skip = False
                self.advance_play_pointer(self.turn_order)

            if self.previous_player == self.current_player:
                await asyncio.sleep(2)  # make the game easier to follow

        if not len(self.winning_players):
            await self.ctx.send(
                "There is only one player left and everyone else has been disqualified. Unfortunately, to prevent "
                "illegitimate currency gains, nothing will be awarded.")
        else:
            self.winning_players.append(self.players[0])
            if self.game_message:
                with contextlib.suppress(discord.DiscordException):
                    await self.game_message.delete()

            disqualified_players = [u for u in tuple(set(self.starting_players) - set(self.winning_players))]
            c_pre = await get_money_prefix(self.ctx, self.ctx.guild.id)
            rankings = []
            for index, user in enumerate(self.winning_players):
                rankings.append(f"`{index + 1}.` - {user.mention} ({user}): +{c_pre}{await self.do_payout(user)}")

            rankings_list = "This Uno game has concluded. Here are the standings and earnings:\n"
            rankings_list += "\n".join(rankings)
            if disqualified_players:
                rankings_list += "\n\nThe following players were disqualified and receive nothing:\n" \
                                 + " ".join(f"{u.mention} ({u})" for u in disqualified_players)

            await self.ctx.send(rankings_list)

            winner = self.winning_players[0]
            current_wins = (await self.ctx.bot.db_pool.fetchval(
                "SELECT uno_default_wins FROM uno WHERE user_id = $1", winner.id)) or 0
            await self.ctx.bot.db_pool.execute(
                "INSERT INTO uno (user_id, uno_default_wins) VALUES ($1, $2) "
                "ON CONFLICT (user_id) DO UPDATE SET uno_default_wins = $2;",
                winner.id, current_wins + 1)


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
