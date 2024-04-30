import os
import re

import requests
import yaml

# get environment parameters
MANAGER_VERSION = os.environ.get("MANAGER_VERSION", None)
if not MANAGER_VERSION:
    try:
        with open("manager/configuration.yml") as fp:
            data = yaml.load(fp, Loader=yaml.FullLoader)

        MANAGER_VERSION = data["manager_version"]
    except:
        MANAGER_VERSION = "latest"

VERSIONS_URL = os.environ.get(
    "VERSIONS_URL",
    "https://raw.githubusercontent.com/osism/release/main/%s/base.yml"
    % MANAGER_VERSION,  # noqa E501
)

# load versions files from release repository
r = requests.get(VERSIONS_URL)
versions = yaml.full_load(r.text)

commons_version = versions["ansible_collections"]["osism.commons"]
docker_version = versions["osism_projects"]["docker"]
generics_version = versions["generics_version"]
playbooks_manager = versions.get("manager_playbooks_version", "main")
services_version = versions["ansible_collections"]["osism.services"]

# manage generics version in gilt.yml

try:
    with open("../gilt.yml", "r+") as fp:
        data = fp.read()
        data = re.sub(
            "version: .*",
            f"version: {generics_version}",
            data,
        )
        fp.seek(0)
        fp.write(data)
except FileNotFoundError:
    pass

# manage ansible collection versions in manager/run.sh

try:
    with open("manager/run.sh", "r+") as fp:
        data = fp.read()
        data = re.sub(
            "ANSIBLE_COLLECTION_COMMONS_VERSION=.*",
            f"ANSIBLE_COLLECTION_COMMONS_VERSION=${{ANSIBLE_COLLECTION_COMMONS_VERSION:-v{commons_version}}}",
            data,
        )
        data = re.sub(
            "ANSIBLE_COLLECTION_SERVICES_VERSION=.*",
            f"ANSIBLE_COLLECTION_SERVICES_VERSION=${{ANSIBLE_COLLECTION_SERVICES_VERSION:-v{services_version}}}",
            data,
        )
        data = re.sub(
            "ANSIBLE_PLAYBOOKS_MANAGER_VERSION=.*",
            f"ANSIBLE_PLAYBOOKS_MANAGER_VERSION=${{ANSIBLE_PLAYBOOKS_MANAGER_VERSION:-{playbooks_manager}}}",
            data,
        )
        fp.seek(0)
        fp.write(data)
except FileNotFoundError:
    pass

# manage docker version in environments/configuration.yml and environments/manager/configuration.yml

print(
    "The docker_version parameter in environments/configuration.yml and"
    " environments/manager/configuration.yml is modified"
    " if available there. If the docker_version is configured elsewhere, it must"
    " be adjusted manually.\n\n"
    f"The Docker version for OSISM {MANAGER_VERSION} is '{docker_version}'."
)

try:
    with open("configuration.yml", "r+") as fp:
        data = fp.read()
        data = re.sub("docker_version: .*", f"docker_version: '{docker_version}'", data)
        fp.seek(0)
        fp.write(data)
except FileNotFoundError:
    pass

try:
    with open("manager/configuration.yml", "r+") as fp:
        data = fp.read()
        data = re.sub("docker_version: .*", f"docker_version: '{docker_version}'", data)
        fp.seek(0)
        fp.write(data)
except FileNotFoundError:
    pass
