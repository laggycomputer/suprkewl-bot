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

client = bot.theBot(
    status=discord.Status.idle,
    command_prefix=bot.get_pre,
    description="Did you know? If you are in a DM with me, you don't need a prefix!",
)

if config.token == "":
    raise ValueError("Please set your token in the config file.")
else:
    try:
        client.run(config.token)
    except discord.LoginFailure:
        print("Invalid token passed, exiting.")
