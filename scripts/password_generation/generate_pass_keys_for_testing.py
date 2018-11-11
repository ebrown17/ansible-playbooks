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
prod_user_file="../../user_vars/user_passwords/prod_user_info.yaml"
ansible_user_file="../../user_vars/user_passwords/ansible_user_info.yaml"
root_user_file="../../user_vars/user_passwords/root_user_info.yaml"

user_file_list = {"prod-users":prod_user_file,"ansible":ansible_user_file,"root":root_user_file}


# location to store keys; file seperation must be appended to this so "/fullpath/folder/"
key_file_location="../../user_vars/user_keys/"

groupname = ""   

yaml_users_list = {}

def update_group(pw,grpname):

	with open(user_file_list.get(grpname)) as f:
		yaml_users_list = yaml.load(f)

	for key,users_list in yaml_users_list.items():
		for user,user_info in users_list.items():					
			users_list.update({user:{'username':user,'password':pw,'group':grpname}})
	
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
	print "Writing changes to file"
	update_yaml_file(yaml_users_list)
	if "root" in groupname:
		continue

	date = datetime.now().strftime("%c")
	print yaml_users_list
	for key,users_list in yaml_users_list.items():

		for user,user_info in users_list.items():
			username = user_info["username"]
			groupname = user_info["group"]
			print username + " " + groupname

			print "Generating key for " + username		
			file_location = key_file_location+groupname+"/"+username+"/"
			call(["mkdir","-p",file_location])

			call(["ssh-keygen", "-b", "8192", "-a", "100", "-N",password,"-f",file_location+username,"-C","Generated for group " + groupname+"  user "+username + " on " + date])
			pass_phrase = call(["ssh-keygen", "-y", "-P",password,"-f", file_location+username],stdout=open(os.devnull, 'wb'))

			if pass_phrase == 0:
				print "Passsphrase was created correctly"
				print "Keys created at: " + file_location
			else:
				print "ERROR: Passsphrase was not created  correctly for " + username
				sys.exit(0)

print "Generation complete... "	
