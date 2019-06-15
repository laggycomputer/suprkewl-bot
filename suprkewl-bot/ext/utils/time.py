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

import datetime

from dateutil.relativedelta import relativedelta

from .format_and_convert import Plural


def human_timedelta(dt, *, source=None, accuracy=None):  # From R. Danny.
    now = source or datetime.datetime.utcnow()
    if dt > now:
        delta = relativedelta(dt, now)
        suffix = ""
    else:
        delta = relativedelta(now, dt)
        suffix = " ago"

    if delta.microseconds and delta.seconds:
        delta = delta + relativedelta(seconds=+1)

    attrs = ["years", "months", "days", "hours", "minutes", "seconds"]

    output = []
    for attr in attrs:
        elem = getattr(delta, attr)
        if not elem:
            continue

        if attr == "days":
            weeks = delta.weeks
            if weeks:
                elem -= delta.weeks * 7
                output.append(format(Plural(weeks), "week"))

        if elem > 1:
            output.append(f"{elem} {attr}")
        else:
            output.append(f"{elem} {attr[:-1]}")

    if accuracy is not None:
        output = output[:accuracy]

    if len(output) == 0:
        return "now"
    elif len(output) == 1:
        return output[0] + suffix
    elif len(output) == 2:
        return f"{output[0]} and {output[1]}{suffix}"
    else:
        return f"{output[0]}, {output[1]} and {output[2]}{suffix}"
