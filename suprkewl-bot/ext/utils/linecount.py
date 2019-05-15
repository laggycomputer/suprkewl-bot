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
                    for i, l in enumerate(f):
                        if l.strip().startswith("#") or len(l.strip()) == 0:
                            pass
                        else:
                            total += 1

    return f"I am made of {total:,} lines of Python, spread across {file_amount:,} files!"
