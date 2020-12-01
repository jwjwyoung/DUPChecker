import os
import re
import class_class
import argparse
import subprocess
from class_class import Version_class
import numpy as np

# regex_str to match the tag for hbase it's "[0-9]*\.[0-9]*\.[0-9]*\.*RC"
def extract_tags(folder, regex_str=".*"):
    tags = []
    cmd = "cd {}; git tag -l --sort version:refname".format(folder)
    output = os.popen(cmd).read().split("\n")
    regex = re.compile(regex_str)
    for o in output:
        if regex.match(o) and o != "":
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
        if f.endswith(".proto") or f.endswith(".thrift"):
            fc = changed_contents[i]
            proto_files.append(f)
            proto_contents.append("\n".join(fc))
    return proto_files, proto_contents


def compare2versionsProtoFiles(tag_old, tag_new, folder, file_type=None):
    v_old = Version_class(folder, tag_old)
    v_new = Version_class(folder, tag_new)
    proto_files, proto_contents = extract_proto_change(tag_old, tag_new, folder)
    v_old.build()
    v_old.parseFiles(proto_files, file_type)
    old_proto_files = v_old.proto_files
    v_new.build()
    v_new.parseFiles(proto_files, file_type)
    new_proto_files = v_new.proto_files
    added_proto_file_keys = new_proto_files.keys() - old_proto_files.keys()
    deleted_proto_file_keys = old_proto_files.keys() - new_proto_files.keys()
    shared_proto_file_keys = new_proto_files.keys() - added_proto_file_keys
    am_sum = dm_sum = cfm_sum = afm_sum = dfm_sum = 0
    r_msg = [0, 0, 0, 0, 0]
    r_enum = [0, 0, 0, 0, 0]
    for key in shared_proto_file_keys:
        proto_file_old = old_proto_files[key]
        proto_file_new = new_proto_files[key]
        # am: added msg, dm: deleted msg, cfm: changed field msg, afm: added field msg, dfm: deleted field msg
        msgs = proto_file_new.compare(proto_file_old)
        enums = proto_file_new.compare_enums(proto_file_old)
        for index in range(len(msgs)):
            s = msgs[index]
            r_msg[index] += len(s)
        for index in range(len(enums)):
            s = enums[index]
            r_enum[index] += len(s)
    return r_msg, r_enum


def compare2versionsJavaFiles(tag_old, tag_new, folder, file_type=None):
    v_old = Version_class(folder, tag_old)
    v_new = Version_class(folder, tag_new)
    changed_files, changed_contents = getChangedFiles(tag_old, tag_new, folder)
    changed_files = getJavaFiles(changed_files)
    v_old.build()
    v_old.parseFiles(changed_files, file_type)
    v_new.build()
    v_new.parseFiles(changed_files, file_type)
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
        # unhandled files
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
    output_log += "add: {}, delete: {}, change: {}, unhandled: {} size_exceptions: {} size_serialize: {}\n".format(
        add_cnt, delete_cnt, change_cnt, unhandled_cnt, size1, size2
    )
    log_file.write(output_log)


def getChangedFiles(tag_old, tag_new, folder):
    files = []
    cmd = "cd {} ; git diff {} {} > diff.log".format(folder, tag_old, tag_new)
    os.system(cmd)
    output = open("{}/diff.log".format(folder), encoding="latin-1").read()
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
            filename = folder + line[len(prefix) : -1].split(" ")[0]
            if filename not in files:
                files.append(filename)
                # print(filename)
    changed_contents.append(lines[end_index:])
    return files, changed_contents


def getJavaFiles(files):
    results = []
    for f in files:
        if f.endswith("java"):
            results.append(f)
    return results


def main():
    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="Change analysis")
        parser.add_argument("--app", dest="app", help="")
        parser.add_argument("--v1", dest='v1', help="")
        parser.add_argument("--v2", dest='v2', help="")
        parser.add_argument(
            "--excep",
            action="store_true",
            help="choose whether you want the data of methods for changed exceptions",
        )
        parser.add_argument(
            "--serialize",
            action="store_true",
            help="choose whether you want the data of methods of serialization function",
        )
        parser.add_argument(
            "--proto",
            action="store_true",
            help="choose whether you want the data of protofiles",
        )
        parser.add_argument(
            "--thrift",
            action="store_true",
            help="choose whether you want the data of protofiles",
        )

        args = parser.parse_args()
        ce = args.excep
        print(ce)
        sf = args.serialize
        proto = args.proto
        thrift = args.thrift
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
            log_file_name = "log/" + app_name + "exceptions.log"
            log_file = open(log_file_name, "w")
            # compare2versionsJavaFiles(tag_old, tag_new, folder)
            for i in range(len(tags) - 1):
                tag_old = tags[i]
                tag_new = tags[i + 1]
                compare2versionsJavaFiles(tag_old, tag_new, folder)

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
        file_type = []
        if proto:
            file_type.append("proto")
        if thrift:
            file_type.append("thrift")

        if len(file_type) > 0:
            proto_log_fn = "log/" + "proto_change_" + app_name + ".log"
            proto_log_f = open(proto_log_fn, "w")
            cnt = 0
            tag_old = "YARN-5355-branch-2-2016-11-06"
            tag_new = "YARN-5355-branch-2-2017-04-25"
            tag_old = "rel/2.2.6"
            tag_new = "rel/2.3.3"
            if args.v1 and args.v2:
                tag_old = args.v1
                tag_new = args.v2
            compare2versionsProtoFiles(tag_old, tag_new, folder, file_type)
            exit(0)
            results = []
            for i in range(len(tags) - 1):
                tag_old = tags[i]
                tag_new = tags[i + 1]
                proto_files, proto_contents = extract_proto_change(
                    tag_old, tag_new, folder
                )
                proto_log_f.write(str(len(proto_files)))
                print(
                    "======== tag_old: {} vs tag_new: {} #changed proto files: {}=========".format(
                        tag_old, tag_new, len(proto_files)
                    )
                )
                proto_log_f.write("\n")
                r_msg, r_enum = compare2versionsProtoFiles(tag_old, tag_new, folder)
                results.append(r_msg + r_enum)
                if len(proto_files) > 0:
                    cnt += 1
            results = np.array(results)
            proto_log_f.write("{} {}\n".format(cnt, len(tags)))
            cnt, summation = result_to_string(results, proto_log_f)
            proto_log_f.write("SUM {}\n".format(summation))
            proto_log_f.write("CNT {}\n".format(cnt))
            proto_log_f.close()


def result_to_string(results, log_file):
    cnt = ""
    summation = ""
    for i in range(len(results[0])):
        sub_arr = results[:, i]
        summation += str(sub_arr.sum()) + " "
        l_length = len(sub_arr[sub_arr > 0])
        cnt += "{} ".format(l_length)
    return cnt, summation


log_file = None
main()
