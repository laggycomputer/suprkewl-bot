# SuprKewl Bot

<p align="center">
<a href="https://discord.gg/CRBBJVY"><img src="https://img.shields.io/discord/498185249952366602.svg"></a>
<a href="./LICENSE-mit.txt"><img src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
</p>


An open-sourced Discord bot. We've moderation, fun, user info, and more planned.

If you want to host this bot:

* Edit `suprkewl-bot/config.py` to include your token.
* Repeat with your Redis server IP (can be internal) and port, and password (don't set one if you don't want to use one).
* Then, install Redis on your host of choice, and set it up with the same password that you configured.
* Finally, you can use `pip3 install -r requirements.txt` at the root of this repo to install the requirements, and `./purgepyc.sh` to purge `__pycache__` from all code folders.
