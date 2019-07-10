# SuprKewl Bot

<p align="center">
<a href="https://discord.gg/CRBBJVY"><img src="https://img.shields.io/discord/498185249952366602.svg"></a>
<a href="./LICENSE-agpl3.txt"><img src="https://img.shields.io/github/license/laggycomputer/suprkewl-bot.svg?style=popout"></a>
<a href=https://travis-ci.com/laggycomputer/suprkewl-bot><img src=https://travis-ci.com/laggycomputer/suprkewl-bot.svg?branch=master></a>
</p>

An open-sourced Discord bot, written with `discord.py==1.2.2`. 

If you want to host this bot:

* Copy `suprkewl-bot/config.py.example` to `suprkewl-bot/config.py`. Fill in your Discord bot token.
* Repeat with your Redis server IP (can be internal) and port, and password (don't set one if you don't want to use one).
* Then, install Redis on your host of choice, and set it up with the same password that you configured.
* Fill in all the extra API values, and you're all set.
* Finally, you can use `pip3 install -r requirements.txt` at the root of this repo to install the requirements.

**Please ensure that you run the bot with the repo root as your current directory.**
(If you forget about this and run the bot, you can use `s!jsk py import os; os.chdir("..")`.)

Oh and hey, if you wanna PR this bot, I'm not merging/rebasing until the build passes. Thanks anyway.
