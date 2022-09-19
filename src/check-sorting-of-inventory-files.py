#!/usr/bin/env python3

from configparser import ConfigParser
import os

from tabulate import tabulate

IGNORE = ["cephclient:children"]

headers = ["filename", "", ""]
result = []

for filename in os.listdir("inventory"):
    config = ConfigParser(allow_no_value=True)
    config.read(os.path.join("inventory", filename))

    sections = config.sections()

    i = 1
    while i < len(sections):
        if sections[i] < sections[i-1] and sections[i-1] not in IGNORE:
            result.append([filename, sections[i-1], sections[i]])
        i += 1

print(tabulate(result, headers, tablefmt="psql"))
