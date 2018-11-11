## Modified to be used in my AWS testing environment


## First pass at readme - just listing general requirements

- All plays are designed to be run from the user ansible
- All plays assume remote machine has been configured to be managed by ansible
	- there is a play to configure a machine for this: `init_0_config_ansible.yaml`
- For ansible to configure machines without having to enter rsa passphrase or the root password the following must happen:
	- Load the ansible private rsa key into an ssh agent:
		1. `ssh-agent bash`
		2. `ssh-add <location of private rsa key`
			- ex: `ssh-add user_vars/user_keys/ansible/ansible/ansible`	
	- Ansible needs to know root password for privledge escalation, so each time you run a play you can do the following, which prevents storing the root password in plain text.
		- `--ask-pass <root password>`
			- ex: ` ansible-playbook -i hosts/test-inventory full_system_configuration.yaml --ask-pass`
- This playbook is configured to be run from the directory this readme is located. 		



## useful commands:

- `ansible -i hosts/test-inventory all  -m debug -a 'var=group_names'`
	- Prints each host and what groups they are in
- `ansible -i hosts/test-inventory localhost -m debug -a 'var=groups'`
	- Prints members of each group
- append the following to plays to see what will be run
	- `--list-tasks`
	- `--list-hosts`	
