def escape_codeblocks(line):
    if not line:
        return line

    i = 0
    n = 0
    while i < len(line):
        if (line[i]) == '`':
            n += 1
        if n == 3:
            line = line[:i] + '\u200b' + line[i:]
            n = 1
            i += 1
        i += 1

    if line[-1] == '`':
        line += '\u200b'

    return line
