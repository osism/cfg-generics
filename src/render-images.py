import os

import jinja2
import requests
import yaml

# get environment parameters

MANAGER_VERSION = os.environ.get("MANAGER_VERSION", None)
if not MANAGER_VERSION:
    try:
        with open("configuration.yml") as fp:
            data = yaml.load(fp, Loader=yaml.FullLoader)

        MANAGER_VERSION = data["manager_version"]
    except:
        MANAGER_VERSION = "latest"

VERSIONS_URL = os.environ.get(
    "VERSIONS_URL",
    "https://raw.githubusercontent.com/osism/release/main/%s/base.yml"
    % MANAGER_VERSION,
)
IMAGES_URL = os.environ.get(
    "IMAGES_URL",
    "https://raw.githubusercontent.com/osism/release/main/etc/images.yml",
)

# load versions files from release repository

r = requests.get(VERSIONS_URL)
versions = yaml.full_load(r.text)

r = requests.get(IMAGES_URL)
images = yaml.full_load(r.text)

# always use latest osism if manager version is latest
if MANAGER_VERSION == "latest":
    versions["docker_images"]["inventory_reconciler"] = "latest"
    versions["docker_images"]["osism"] = "latest"
    versions["docker_images"]["osism_ansible"] = "latest"
    versions["docker_images"]["osism_kubernetes"] = "latest"

if "osism_ansible" not in versions["docker_images"]:
    versions["docker_images"][
        "osism_ansible"
    ] = "{{ manager_version|default('latest') }}"

if "osism_kubernetes" not in versions["docker_images"]:
    versions["docker_images"][
        "osism_kubernetes"
    ] = "{{ manager_version|default('latest') }}"

# prepare jinja2 environment

loader = jinja2.FileSystemLoader(searchpath=".")
environment = jinja2.Environment(loader=loader)

# render images.yml

template = environment.get_template("images.yml")
result = template.render(
    {
        "images": images,
        "manager_version": MANAGER_VERSION,
        "versions": versions["docker_images"],
    }
)
with open("images.yml", "w+") as fp:
    fp.write(result)
