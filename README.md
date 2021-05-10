# SuprKewl Bot

<p align="center">
<a href="https://discord.gg/CRBBJVY"><img src="https://img.shields.io/discord/498185249952366602.svg"></a>
<img src="https://img.shields.io/github/repo-size/laggycomputer/suprkewl-bot">
<img src="https://img.shields.io/github/last-commit/laggycomputer/suprkewl-bot">
<a href="./LICENSE-agpl3.txt"><img src="https://img.shields.io/github/license/laggycomputer/suprkewl-bot.svg?style=popout"></a>
<a href=https://travis-ci.com/laggycomputer/suprkewl-bot><img src=https://travis-ci.com/laggycomputer/suprkewl-bot.svg?branch=master></a>
<br>
<a href="https://top.gg/bot/408869071946514452"><img src="https://top.gg/api/widget/408869071946514452.png"></a>
</p>

An open-sourced Discord bot, written with `discord.py==1.7.1`. 

If you want to host this bot:

* Ensure your bot application has both intents enabled.
* Copy `suprkewl-bot/config.py.example` to `suprkewl-bot/config.py`. Fill out the config parameters.
* You need to set up both a Redis and a Lavalink instance and fill out the credentials in config.
* You need the tables `tf2idb_item` and `tf2idb_item_attributes` from [here](https://github.com/flaminsarge/tf2idb) (migrate them in using pgloader)
* You also need Postgres (if you don't already have it); install it and type the following lines into `psql`:
  * `CREATE ROLE skbot WITH LOGIN PASSWORD '123';`
  * `CREATE DATABASE skbot OWNER skbot;`
  * `CREATE EXTENSION pg_trgm;`
* Finally, you can use `pip3 install -r requirements.txt` at the root of this repo to install the requirements.

**Please ensure that you run the bot with the repo root as your current directory.**
(If you forget about this and run the bot, you can use `sk!jsk py import os; os.chdir("<repo root dir here>")`.)

Oh and hey, if you wanna PR this bot, I'm not merging/rebasing until the build passes. Thanks anyway.
