# What SuprKewl Bot stores

The following persitent data is logged when you use this bot:
* `sk!inspire`: When you favorite an image, your user ID and the ID of the image are stored. This data is deleted when you clear your favorites library. 
* `sk!snipe`: When you delete a message in a channel this bot can read, the user, message, channel, and guild IDs are stored with the message content. This is deleted when the bot is removed from the guild containing the message.
* Economy commands (`sk!daily`, `sk!trivia`, etc.): Your balance, daily streak, and the last time at which you claimed a daily are stored under your user ID. You can delete this data by waiting at least 24 hours after claiming a daily, then paying someone else your entire balance.
* `sk!ign`: Past usernames are cached with a UUID. This is public information and will not be deleted.
* `sk!blacklist`: When you are blacklisted, your user ID is stored on the blacklist. There is no way for this to be deleted other than you saying the magic word (please) and hoping you get unblacklisted.
* Guild-wide settings like custom bot and currency prefixes are deleted when the bot leaves the guild.

All other data is either deleted after a timeout or unloaded when the bot restarts.