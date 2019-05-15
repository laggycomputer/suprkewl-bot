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

import logging

import discord

import bot
import config


logger = logging.getLogger("discord")
logger.setLevel(config.loglevel)
if config.clearLog:
    handler = logging.FileHandler(filename=config.logpath, encoding="utf-8", mode="w")
else:
    handler = logging.FileHandler(filename=config.logpath, encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter("%(asctime)s: %(levelname)s: %(name)s: %(message)s"))
logger.addHandler(handler)

client = bot.suprkewl_bot(
    status=discord.Status.idle,
    command_prefix=bot.get_pre
)

if __name__ == "__main__":
    if config.token == "":
        raise ValueError("Please set your token in the config file.")
    else:
        try:
            client.run(config.token)
        except discord.LoginFailure:
            print("Invalid token passed, exiting.")
else:
    print("Please don't import me!")
