# -*- coding: utf-8 -*-

"""
Copyright (C) 2020 Dante "laggycomputer" Dam

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

import codecs
import os
import pathlib


def linecount():
    path_to_search = "./"
    total = 0
    file_amount = 0
    for path, subdirs, files in os.walk(path_to_search):
        for name in files:
            if name.endswith(".py"):
                file_amount += 1
                with codecs.open(path_to_search + str(pathlib.PurePath(path, name)), "r", "utf-8") as f:
                    for line in list(f)[20:]:
                        if line.strip().startswith("#") or len(line.strip()) == 0:
                            pass
                        else:
                            total += 1

    avg = round(total / file_amount, 2)

    return f"I am made of {total:,} lines of Python, spread across {file_amount:,} files! That's an average of about" \
        f" {avg:,} lines per file."
