import logging

# Your Discord bot token here:
token = ""
prefix = "s!"
# Logging path and level.
logpath = "../suprkewl.log"
loglevels = (logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)
# You can set this to one of the above values, or try your own integer value from 0 to 50 inclusive.
# See the logging docs at https://docs.python.org/3/library/logging.html#levels for more info.
loglevel = loglevels[4]

# If this is true, the log will be cleared on bot startup.
clearLog = False

# Redis config
redis_host = "192.168.1.23"
# IMPORTANT: If you running the bot on a server that is open to the web,
# CHANGE BOTH THESE VALUES HERE AND IN REDIS CONFIG, ESPECIALLY THE PASSWORD
redis_port = "6379"
# Again, this is insecure
# CHANGE IT
redis_password = "testing"

# This is intentionally useless without being set. SET IT
db_path = "C:\\Users\\WindowsUser\\Documents\\suprkewl-bot\\skbot.db"
