#!/bin/python
# paramiko ,passlib and pyyaml need to be installed to run this script
### This is a modified version of standard user and gives option to disable passphrase generation and generates the same password
### for all users in a group. Will generate unique ssh key per user though.

from passlib.hash import sha512_crypt;
import getpass;
import sys;
import yaml;
import os;
from subprocess import call;
from subprocess import check_output;
from datetime import datetime;
 
# location of user info yaml file
prod_users_file="../../user_vars/user_info/prod_users_info.yaml"
dev_users_file="../../user_vars/user_info/dev_users_info.yaml"
ec2_user_file="../../user_vars/user_info/ec2_user_info.yaml"
ansible_user_file="../../user_vars/user_info/ansible_user_info.yaml"
root_user_file="../../user_vars/user_info/root_user_info.yaml"

user_file_list = {"prod-users":prod_users_file,"dev-users":dev_users_file,"ec2-user":ec2_user_file,"ansible":ansible_user_file,"root":root_user_file}


# location to store keys; file seperation must be appended to this so "/fullpath/folder/"
key_file_location="../../user_vars/user_keys/"

groupname = ""   

yaml_users_list = {}

def update_group(pw,grpname):

	with open(user_file_list.get(grpname)) as f:
		yaml_users_list = yaml.load(f)

	for user,user_info in yaml_users_list.get("users").items():
		user_info.update({'username':user,'password':pw})

	return yaml_users_list
		
def update_yaml_file(yaml_change):
	file_to_update = user_file_list.get(groupname)

	with open(file_to_update, 'w') as f:
		yaml.dump(yaml_change, f)	


################# start of actual script ####################
verify_pass = False
while( not verify_pass):	
	password = getpass.getpass("Enter new password: ")
	password_v = getpass.getpass("Enter password again to verify: ")
	if(password == password_v):
		verify_pass = True
	else:
		print "Passwords did not match"

print "Hashing password... "
hashedpw = sha512_crypt.encrypt(password)
for group, file in user_file_list.items():
	groupname = group
	print "updating "+groupname + " passwords and rsa keys "
	yaml_users_list = update_group(hashedpw,groupname)
	#sys.exit(0)
	print "Writing changes to file"
	update_yaml_file(yaml_users_list)
	if "root" in groupname:
		continue

	date = datetime.now().strftime("%c")
	print yaml_users_list
	groupname = yaml_users_list.get("groupname")
	for user,user_info in yaml_users_list.get("users").items():

		username = user_info["username"]			
		print username + " " + groupname

		print "Generating key for " + username

		file_location = key_file_location+groupname+"/"+username+"/"
		call(["mkdir","-p",file_location])

		#prod users should will not have a passphrase to allow sshing to themelves
		if "prod-users" == groupname:
			passphrase=""
		else:
			passphrase=password
			
		call(["ssh-keygen", "-b", "8192", "-a", "100", "-N",passphrase,"-f",file_location+username,"-C","Generated for group " + groupname+"  user "+username + " on " + date])
		passphrase_check = call(["ssh-keygen", "-y", "-P",passphrase,"-f", file_location+username],stdout=open(os.devnull, 'wb'))

		if passphrase_check == 0:
			print "Passsphrase was created correctly"
			print "Keys created at: " + file_location
		else:
			print "ERROR: Passsphrase was not created  correctly for " + username
			sys.exit(0)

print "Generation complete... "	
