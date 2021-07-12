# Generic configuration files

## environments/configuration directory

The configuration repository needs to be synchronized regularly with
this repository to obtain any updates. It contains in particular the
directory ``environments/manager``, which is needed to initially build
the manager node, and is updated on a regular basis.

If there are errors when rebuilding an environment, such as a missing Ansible
role, you should first try synchronizing before time-consuming debugging.

The value for ``MANAGER_VERSION`` is stored in
``environments/manager/configuration.yml`` in the ``manager_version``
parameter.

Synchronization has to be performed when updating to a new version. In this
case, ``MANAGER_VERSION`` will be set to the new version.

The following commands are executed within the root directory of the
configuration repository.

```
virtualenv -p python3 .venv
source .venv/bin/activate
pip3 install -r requirements.txt
MANAGER_VERSION=1.0.0 gilt overlay
```

After synchronization, check for changes in the configuration repository.

```
git status
```

If there are any changes, review and commit them.

```
git diff
git add .
git commit
```

## inventory directory

The general hostgroups for Ansible available in OSISM are stored in the
``inventory`` directory. These files are included in the individual
container images, such as the inventory reconciler. The files in this
directory are not intended to be included directly in a configuration
repository.
