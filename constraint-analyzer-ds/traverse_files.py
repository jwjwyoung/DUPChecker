import os
import re
import class_class
import argparse

from class_class import Version_class
# regex_str to match the tag for hbase it's "[0-9]*\.[0-9]*\.[0-9]*\.*RC"
def extract_tags(folder, regex_str=".*"): 
	tags = []
	cmd = 'cd {}; git tag -l --sort version:refname'.format(folder)
	output = os.popen(cmd).read().split("\n")
	regex = re.compile(regex_str)
	for o in output:
		if regex.match(o):
			tags.append(o)
	return tags

def construct_all_versions(folder, regex_str):
	tags = extract_tags(folder, regex_str)
	versions = []
	for tag in tags:
		version = Version_class(folder, tag)
		versions.append(version)
	return versions

def compare2versions(tag_old, tag_new, folder):
	v_old = Version_class(folder, tag_old)
	v_new = Version_class(folder, tag_new)
	changed_files = getChangedFiles(tag_old, tag_new, folder)
	v_old.build()
	v_old.parseFiles(changed_files)
	v_new.build()
	v_new.parseFiles(changed_files)
	add_cnt = 0
	delete_cnt = 0
	change_cnt = 0
	unhandled_cnt = 0
	size = 0
	for key in changed_files:
		java_file_old = None
		java_file_new = None
		if key in v_old.java_files.keys():
			java_file_old = v_old.java_files[key]
			# print("old yes")
		if key in v_new.java_files.keys():
			java_file_new = v_new.java_files[key]
			# print("new yes")
		#unhandled files
		if java_file_old == None and java_file_new == None:
			unhandled_cnt += 1
		# add files
		if java_file_old == None and java_file_new != None:
			add_cnt += 1
		# delete files
		if java_file_old != None and java_file_new == None:
			delete_cnt += 1
		# change files
		if java_file_old != None and java_file_new != None:
			change_cnt += 1
			changed_classes = java_file_new.compare(java_file_old)
			for value in changed_classes:
				size += len(value)			
	output_log = 'add: {}, delete: {}, change: {}, unhandled: {} size: {}\n'.format(add_cnt, delete_cnt, change_cnt, unhandled_cnt, size)
	log_file.write(output_log)

def getChangedFiles(tag_old, tag_new, folder):
	files = []
	cmd = 'cd {}; git diff {} {}'.format(folder, tag_old, tag_new)
	output = os.popen(cmd).read()
	cnt = 0
	for line in output.split("\n"):
		prefix = "diff --git a"
		if line.startswith(prefix):
			filename = folder + line[len(prefix):-1].split(" ")[0]
			if filename.endswith(".java") and filename not in files:
				files.append(filename)
				# print(filename)
	return files
 
def main():
    if __name__== "__main__" :
    	parser = argparse.ArgumentParser(description='Change analysis')
    	parser.add_argument('--app', dest='app', 
                    help='')
    	args = parser.parse_args()
    	folder = "../hbase"
    	regex_str = "[0-9]*\.[0-9]*\.[0-9]*\.*RC"
    	if args.app:
    		folder = args.app
    		regex_str = ".*"
    	tags = extract_tags(folder, regex_str)
    	tag_old = tags[-2]
    	tag_new = tags[-1]
    	global log_file
    	log_file_name = folder.split("/")[-1] + "exceptions.log"
    	log_file = open(log_file_name, "w")
    	for i in range(len(tags)-1):
    		tag_old = tags[i]
    		tag_new = tags[i+1]
    		compare2versions(tag_old, tag_new, folder)

    	log_file.close()
log_file = None
main()