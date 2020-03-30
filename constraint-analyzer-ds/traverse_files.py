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
		if regex.match(o) and o != ''	:
			tags.append(o)
	return tags

def construct_all_versions(folder, regex_str):
	tags = extract_tags(folder, regex_str)
	versions = []
	for tag in tags:
		version = Version_class(folder, tag)
		versions.append(version)
	return versions

def extract_proto_change(tag_old, tag_new, folder):
	v_old = Version_class(folder, tag_old)
	v_new = Version_class(folder, tag_new)
	changed_files, changed_contents = getChangedFiles(tag_old, tag_new, folder)
	proto_files = []
	proto_contents = []
	for i in range(len(changed_files)):
		f = changed_files[i]
		if f.endswith(".proto"):
			fc = changed_contents[i]	
			proto_files.append(f)
			proto_contents.append("\n".join(fc))
	return proto_files, proto_contents


def compare2versions(tag_old, tag_new, folder):
	v_old = Version_class(folder, tag_old)
	v_new = Version_class(folder, tag_new)
	changed_files, changed_contents = getChangedFiles(tag_old, tag_new, folder)
	changed_files = getJavaFiles(changed_files)
	v_old.build()
	v_old.parseFiles(changed_files)
	v_new.build()
	v_new.parseFiles(changed_files)
	add_cnt = 0
	delete_cnt = 0
	change_cnt = 0
	unhandled_cnt = 0
	size1 = 0
	size2 = 0
	output_log = "-----------{} vs {}-----------\n".format(tag_old, tag_new)
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
			for value1, value2 in changed_classes:
				size1 += len(value1)	
				size2 += len(value2)
				for old_src, new_src in value2:	
					output_log += "\n".join(old_src)
					output_log += "\n"
					output_log += "+++++++++++++++++++++++\n"	
					output_log += "\n".join(new_src)	
					output_log += "\n"
	output_log += 'add: {}, delete: {}, change: {}, unhandled: {} size_exceptions: {} size_serialize: {}\n'.format(add_cnt, delete_cnt, change_cnt, unhandled_cnt, size1, size2)
	log_file.write(output_log)

def getChangedFiles(tag_old, tag_new, folder):
	files = []
	cmd = 'cd {}; git diff {} {}'.format(folder, tag_old, tag_new)
	output = os.popen(cmd).read()
	cnt = 0
	changed_contents = []
	lines = output.split("\n")
	start_index = 0
	end_index = 0
	for i in range(len(lines)):
		line = lines[i]
		prefix = "diff --git a"
		if line.startswith(prefix):
			start_index = end_index
			end_index = i
			if start_index < end_index:
				changed_contents.append(lines[start_index:end_index])
			filename = folder + line[len(prefix):-1].split(" ")[0]
			if filename not in files:
				files.append(filename)
				# print(filename)
	changed_contents.append(lines[end_index:])
	print(len(files) == len(changed_contents))
	return files, changed_contents

def getJavaFiles(files):
	results = []
	for f in files:
		if f.endswith("java"):
			results.append(f)
	return results
 
def main():
	if __name__== "__main__" :
		parser = argparse.ArgumentParser(description='Change analysis')
		parser.add_argument('--app', dest='app', 
		            help='')
		parser.add_argument('--excep', action='store_true', help='choose whether you want the data of methods for changed exceptions')
		parser.add_argument('--serialize', action='store_true', help='choose whether you want the data of methods of serialization function')
		parser.add_argument('--proto', action='store_true', help='choose whether you want the data of protofiles')
		
		args = parser.parse_args()
		ce = args.excep
		print(ce)
		sf = args.serialize
		proto = args.proto
		folder = "../hbase"
		regex_str = "[0-9]*\.[0-9]*\.[0-9]*\.*RC"
		if args.app:
			folder = args.app
			regex_str = ".*"
		app_name = folder.split("/")[-1]
		tags = extract_tags(folder, regex_str)
		if ce:
			tag_old = tags[-2]
			tag_new = tags[-1]
			global log_file
			log_file_name = app_name + "exceptions.log"
			log_file = open(log_file_name, "w")
			# compare2versions(tag_old, tag_new, folder)
			for i in range(len(tags)-1):
				tag_old = tags[i]
				tag_new = tags[i+1]
				compare2versions(tag_old, tag_new, folder)
				
			log_file.close()
		if sf: 
			tag = tags[-1]
			version = Version_class(folder, tag)
			version.build()
			changed_files = version.files
			version.parseFiles(changed_files)
			cnt = 0
			for name in version.java_files.keys():
				file = version.java_files[name]
				for class_name in file.java_classes.keys():
					java_class = file.java_classes[class_name]
					for method_name in java_class.methods.keys():
						if "serialize" in method_name:
							cnt += 1
			print(cnt)
		if proto:
			proto_log_fn = "proto_change_" + app_name + ".log"
			proto_log_f = open(proto_log_fn, "w")
			for i in range(len(tags)-1):
				tag_old = tags[i]
				tag_new = tags[i+1]
				proto_files, proto_contents = extract_proto_change(tag_old, tag_new, folder)
				proto_log_f.write(str(len(proto_files)))
				proto_log_f.write("\n")
				proto_log_f.write("\n".join(proto_contents))
				v_old = Version_class(folder, tag_old)
				v_old.build()
				v_old.parseFiles(proto_files)
				if len(proto_files) > 0:
					break
				
			proto_log_f.close()
log_file = None
main()
