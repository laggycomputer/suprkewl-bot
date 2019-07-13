# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 laggycomputer

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


import json


permissions_converter = {
    "add_reactions": "Add Reactions", "administrator": "Administrator", "attach_files": "Attach Files",
    "ban_members": "Ban Members", "change_nickname": "Can Change Own Nickname", "connect": "Connect to Voice Channels",
    "create_instant_invite": "Create Server Invites", "deafen_members": "Deafen Members", "embed_links": "Embed Links",
    "external_emojis": "(Nitro Only) Use External Emotes", "kick_members": "Kick Members",
    "manage_channels": "Manage Channels", "manage_emojis": "Create, Delete, and Rename Server Emotes",
    "manage_guild": "Manage Server", "manage_messages": "Manage Messages", "manage_nicknames": "Manage Nicknames",
    "manage_roles": "Manage Roles", "manage_webhooks": "Manage Webhooks",
    "mention_everyone": "Ping @\u200beveryone and @\u200bhere", "move_members": "Move Members Between Voice Channels",
    "mute_members": "Mute Members", "priority_speaker": "Use Priority PTT",
    "read_message_history": "Read Past Messages in Text Channels",
    "read_messages": "Read Messages and See Voice Channels", "send_messages": "Send Messages",
    "send_tts_messages": "Send TTS Messages", "speak": "Speak", "use_voice_activation": "No Voice Activity",
    "view_audit_log": "View the Server Audit Log"
}


def escape_codeblocks(line):
    if not line:
        return line

    i = 0
    n = 0
    while i < len(line):
        if line[i] == "`":
            n += 1
        if n == 3:
            line = line[:i] + "\u200b" + line[i:]
            n = 1
            i += 1
        i += 1

    if line[-1] == "`":
        line += "\u200b"

    return line


def format_json(string):
    return json.dumps(string, indent=2, ensure_ascii=False, sort_keys=True)


class Plural:  # From R. Danny.

    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"


def human_join(seq, delim=", ", final="or"):  # Again from R. Danny.
    size = len(seq)
    if size == 0:
        return ""

    if size == 1:
        return seq[0]

    if size == 2:
        return f"{seq[0]} {final} {seq[1]}"

    return delim.join(seq[:-1]) + f" {final} {seq[-1]}"
