#!/usr/bin/env python3

from configparser import ConfigParser
import io

import requests

IGNORE = [
    "baremetal",
    "blazar",
    "collectd",
    "compute",
    "control",
    "cyborg",
    "deployment",
    "freezer",
    "masakari",
    "monitoring",
    "murano",
    "network",
    "sahara",
    "solum",
    "storage",
    "tacker",
    "telegraf",
    "venus",
    "vitrage",
    "watcher",
]

config = ConfigParser(allow_no_value=True)
config.read("inventory/50-kolla")
sections = config.sections()

config = ConfigParser(allow_no_value=True)
config.read("inventory/51-kolla")
sections += config.sections()

url = "https://raw.githubusercontent.com/openstack/kolla-ansible/master/ansible/inventory/multinode"  # noqa
response = requests.get(url, stream=True)

config = ConfigParser(allow_no_value=True)
config.read_file(io.StringIO(response.text))
upstream_sections = config.sections()

for section in [x for x in upstream_sections if x not in sections]:
    if not [x for x in IGNORE if section.startswith(x)]:
        print(f"[{section}]")
        for x in config[section]:
            print(x)
        print()
