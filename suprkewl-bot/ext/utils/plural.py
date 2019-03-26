def plural(values):
    if len(values) == 0:
        return ""
    elif len(values) == 1:
        return values[0]
    elif len(values) == 2:
        return f"{values[0] and values[1]}"
    else:
        ret = ", ".join(values[:-3])
        ret += f", {values[-2]}, and {values[-1]}"
        return ret