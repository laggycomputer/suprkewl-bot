import datetime

from dateutil.relativedelta import relativedelta

from .plural import Plural

# From R. Danny.

def human_timedelta(dt, *, source=None, accuracy=None):
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
