import os
import re

from packaging.version import Version
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

if MANAGER_VERSION == "latest" or Version(MANAGER_VERSION) >= Version("7.0.3"):
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

# manage docker cli version in environments/configuration.yml and environments/manager/configuration.yml

try:
    with open("configuration.yml", "r+") as fp:
        data = fp.read()
        data = re.sub(
            "docker_cli_version: .*", f"docker_cli_version: '{docker_version}'", data
        )
        fp.seek(0)
        fp.write(data)
except FileNotFoundError:
    pass

try:
    with open("manager/configuration.yml", "r+") as fp:
        data = fp.read()
        data = re.sub(
            "docker_cli_version: .*", f"docker_cli_version: '{docker_version}'", data
        )
        fp.seek(0)
        fp.write(data)
except FileNotFoundError:
    pass

# check for openstack_version & ceph_version

if MANAGER_VERSION != "latest":
    try:
        with open("manager/configuration.yml", "r") as fp:
            data = fp.read()
            if "openstack_version" in data:
                print(
                    "openstack_version is available in x. If the manager_version is"
                    " not set to latest, this parameter should not be present there."
                    " Please check and remove the parameter."
                )
            if "ceph_version" in data:
                print(
                    "ceph_version is available in x. If the manager_version is"
                    " not set to latest, this parameter should not be present there."
                    " Please check and remove the parameter."
                )
    except FileNotFoundError:
        pass
