import os

from ruamel.yaml import YAML

yaml = YAML()
yaml.explicit_start = True
yaml.width = 200
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.preserve_quotes = True

# get environment parameters

MANAGER_VERSION = os.environ.get("MANAGER_VERSION", "latest")

if MANAGER_VERSION in ["latest"]:

    # load images file
    with open("images.yml") as fp:
        images = yaml.load(fp)

    images['ceph_ansible_tag'] = "{{ ceph_version|default('luminous') }}"
    images['kolla_ansible_tag'] = "{{ openstack_version|default('rocky') }}"

    # write images file
    with open("images.yml", "w+") as fp:
        yaml.dump(images, fp)
