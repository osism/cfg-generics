import os

import jinja2
import requests
import yaml

# get environment parameters

MANAGER_VERSION = os.environ.get("MANAGER_VERSION", "latest")
VERSIONS_URL = os.environ.get(
    "VERSIONS_URL",
    "https://raw.githubusercontent.com/osism/release/main/%s/base.yml"
    % MANAGER_VERSION,  # noqa E501
)
REQUIREMENTS_FILENAME = os.environ.get("REQUIREMENTS_FILENAME", "requirements.yml")

# load versions files from release repository

r = requests.get(VERSIONS_URL)
versions = yaml.full_load(r.text)

# prepare jinja2 environment

loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(REQUIREMENTS_FILENAME))
environment = jinja2.Environment(loader=loader)

# render requirements.yml

template = environment.get_template(REQUIREMENTS_FILENAME)
result = template.render(
    {
        "versions": versions["ansible_roles"],
    }
)
with open(REQUIREMENTS_FILENAME, "w+") as fp:
    fp.write(result)
