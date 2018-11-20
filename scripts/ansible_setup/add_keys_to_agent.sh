#!/bin/bash
cd ~/ansible-playbooks

# add ssh agent
ssh-agent bash

# add ansible key to agent
ssh-add ~/ansible-playbooks/user_vars/user_keys/ansible/ansible/ansible

# add ec2-user key to agent
ssh-add ~/ansible-playbooks/user_vars/user_keys/ec2-user/ec2-user/ec2-user