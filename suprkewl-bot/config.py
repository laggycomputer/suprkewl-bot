import logging

# Your Discord bot token here:
token = ""
# Logging path and level.
logpath = "../suprkewl.log"
loglevels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
# You can set this to one of the above values, or try your own integer value from 0 to 50 inclusive.
# See the logging docs at https://docs.python.org/3/library/logging.html#levels for more info.
loglevel = loglevels[4]

# If this is true, the log will be cleared on bot startup.
clearLog = False
