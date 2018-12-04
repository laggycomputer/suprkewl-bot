### ToDo

Here's a list of todos for this project. Expect this to change often.

1. Add user status command (currently in progress as s!profile in testing file):
  a. Preferably an embed.
  b. Should include status (online, idle, etc.), server joined date (would render s!joined obsolete), and Discord join date.
2. Copy discord.pw server custom emotes that are useful to the SuprKewl Bot support server, so that we can maintain our own copy of the emotes.
3. Add command to check channel permissions.
4. The variables in s!housefight look like a madhouse. Possibly move fighter-specific varaibles under a new fighter subclass of discord.Member.
5. Add hidden cog reload command, with bot owner check
6. add cooldown error catch and reinvoke. also add error catches for things like disable command, and guild only command. may not be needed, but just in case we want to quickly restrict a command.
7. add command (owner only) to exec(something passes as a param). Make sure it works, doesn't seem to.
8. Change all concatenation and .format to use f-strings.
9. Change all embed author fields to include message author and command invoked (or something like that)