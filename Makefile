venv = . venv/bin/activate
export PATH := ${PATH}:${PWD}/venv/bin

VAULTPASS_FILE ?= ${PWD}/secrets/vaultpass

.PHONY: deps
deps: venv/bin/activate ## Install software preconditions to `venv`.

.PHONY: prune
prune:
	rm -rf venv

venv/bin/activate: Makefile requirements.txt
	@which python3 > /dev/null || { echo "Missing requirement: python3" >&2; exit 1; }
	@[ -e venv/bin/python ] || python3 -m venv venv --prompt osism-$(shell basename ${PWD})
	@${venv} && pip3 install -r requirements.txt
	touch venv/bin/activate

.PHONY: deps
sync: deps
	@[ "${BRANCH}" ] && sed -i -e "s/version: .*/version: ${BRANCH}/" gilt.yml || exit 0
	@${venv} && gilt overlay && gilt overlay



.PHONY: ansible_vault_pass_gather
ansible_vault_pass_gather:
	docker exec osism-ansible cat /share/ansible_vault_password.key > secrets/vaultpass

.PHONY: check_vault_pass
check_vault_pass:
	@test -r ${VAULTPASS_FILE}  || ( echo "the file VAULTPASS_FILE='${VAULTPASS_FILE}' does not exist"; exit 1)


.PHONY: ansible_vault_encrypt_ceph_keys
ansible_vault_encrypt_ceph_keys: deps check_vault_pass
	${venv} ;find . -name "ceph.client.*.keyring"|while read FILE; do \
	 echo "-> $${FILE}"; \
	 if ! ( grep -q ANSIBLE_VAULT $${FILE} );then \
		ansible-vault encrypt $${FILE} --output $${FILE}.vaulted --vault-password-file ${VAULTPASS_FILE} && \
		mv $${FILE}.vaulted $${FILE}; \
	 fi \
	done

.PHONY: ansible_vault_decrypt_ceph_keys
ansible_vault_decrypt_ceph_keys: deps check_vault_pass
	${venv} ;find . -name "ceph.client.*.keyring"|while read FILE; do \
	 echo "-> $${FILE}"; \
	 if ( grep -q ANSIBLE_VAULT $${FILE} );then \
		ansible-vault decrypt $${FILE} --output $${FILE}.unvaulted --vault-password-file ${VAULTPASS_FILE} && \
		mv $${FILE}.unvaulted $${FILE}; \
	 fi \
	done


.PHONY: ansible_vault_rekey
ansible_vault_rekey: deps check_vault_pass
	@if ! git diff-index --quiet HEAD --; then \
	    echo "Error: Uncommitted changes found in the repository. Stash or drop them before rekeying."; \
		 git diff; \
	    exit 1; \
	fi
	openssl rand -base64 24 | tr -dc 'A-Za-z0-9' | head -c 32  > ${VAULTPASS_FILE}.new
	echo "CREATING A BACKUP"
	cp ${VAULTPASS_FILE} ${VAULTPASS_FILE}_backup_$(shell date --date="today" "+%Y-%m-%d_%H-%M-%S")
	echo "PERFORM REKEYING"
	${venv} && find environments/ inventory/ -name "*.yml" -not -path "*/.venv/*" -exec grep -l ANSIBLE_VAULT {} \+|\
		sort -u|\
		xargs -n 1 --verbose ansible-vault rekey  -v \
		--vault-password-file ${VAULTPASS_FILE} \
		--new-vault-password-file ${VAULTPASS_FILE}.new
	echo "MOVE NEW KEY IN PLACE"
	mv ${VAULTPASS_FILE}.new ${VAULTPASS_FILE}

.PHONY: ansible_vault_show
ansible_vault_show: deps check_vault_pass
	${venv} && find environments/ inventory/ -name "*.yml" -and -not -path "*/.venv/*" -exec grep -l ANSIBLE_VAULT {} \+|\
		sort -u|\
		xargs -n 1 --verbose ansible-vault view --vault-password-file ${VAULTPASS_FILE} 2>&1 | less


.PHONY: ansible_vault_edit
ansible_vault_edit: deps check_vault_pass
ifndef FILE
	$(error FILE variable is not set, example 'make ansible_vault_edit FILE=environments/secrets.yml')
endif
	${venv} && ansible-vault edit --vault-password-file ${VAULTPASS_FILE} ${FILE}
