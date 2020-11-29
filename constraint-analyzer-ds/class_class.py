import os
import javalang
from os import walk
from javalang.tree import MethodDeclaration
from javalang.tree import FormalParameter
from javalang.tree import BasicType
import numpy as np
from protobuf_parser import parser


class Java_file:
    def __init__(self, path, ast, contents):
        self.java_classes = {}
        self.path = path
        self.ast = ast
        self.contents = contents

    def parseAst(self):
        if self.ast and self.ast.types:
            for t in self.ast.types:
                if type(t) == javalang.tree.ClassDeclaration:
                    class_name = t.name
                    jc = Java_class(class_name, t)
                    jc.parseClassAst(self.contents)
                    self.java_classes[class_name] = jc

    def compare(self, old_java_file):
        old_jcs = old_java_file.java_classes
        changed_classes = []
        for key in self.java_classes.keys():
            new_jc = self.java_classes[key]
            if key in old_jcs.keys():
                old_jc = old_jcs[key]
                changed_excep_methods = new_jc.compare(old_jc)
                changed_classes.append(changed_excep_methods)
        return changed_classes


class Java_class:
    def __init__(self, class_name, ast):
        self.class_name = class_name
        self.ast = ast
        self.methods = {}
        self.methods_source = {}
        self.package_name = ""
        self.class_name = ""
        self.upper_class_name = ""
        self.path = ""

    def parseClassAst(self, contents):
        if not self.ast:
            return
        # handle upper class
        if self.ast.extends:
            upper_class_name = self.ast.extends.name
        split_con = contents.split("\n")
        # print("split_con " + str(len(split_con)))
        last_index = len(split_con) - 1 - split_con[::-1].index("}")
        # print("last_index " + str(last_index))
        if self.ast.body:
            body = self.ast.body
            for i in range(len(body)):
                b = body[i]
                start_index = b.position.line - 1

                if i < len(body) - 1:
                    end_index = body[i + 1].position.line
                else:
                    end_index = last_index
                con = split_con[start_index : end_index - 1]
                if type(b) == MethodDeclaration:
                    name = b.name
                    param_types = []
                    parameters = b.parameters
                    if parameters:
                        for p in parameters:
                            if type(p) == BasicType:
                                param_types.append(p.name)
                    key = name + "|" + " ".join(param_types)
                    self.methods[key] = b
                    self.methods_source[key] = con

    def compare(self, old_java_class):
        changed_excep_methods = []
        changed_serilize = []
        old_methods = old_java_class.methods
        old_methods_src = old_java_class.methods_source
        for key in self.methods.keys():
            method = self.methods[key]
            method_src = self.methods_source[key]
            if key in old_methods.keys():
                old_method = old_methods[key]
                old_method_src = old_methods_src[key]
                if "serialize" in key:
                    try:
                        if (
                            str(method) != str(old_method)
                            and method_src != old_method_src
                        ):
                            changed_serilize.append([old_method_src, method_src])
                    except:
                        print("cannot transfer to str")
                if old_method.throws != method.throws:
                    changed_excep_methods.append(method)
        return changed_excep_methods, changed_serilize


class Java_method:
    def __init__(self):
        self.exceptions = []


class Proto_file:
    def __init__(self, path, ast, contents):
        self.path = path
        self.ast = ast
        self.contents = contents
        self.messages = {}

    def parseAst(self):
        for item in self.ast:
            if item[0] == "package":
                self.package = item[1]
            if item[0] == "message":
                name = item[1]
                ast = item[2]
                pm = Proto_message(name, ast, self)
                pm.parseAst()
                key = self.path + "_" + name
                self.messages[key] = pm
                for enum_name, enum in pm.defined_enums.items():
                    # add self defined enums within msgs to proto files
                    key = "{}.{}".format(name, enum_name)
                    self.enums[key] = enum
            if item[0] == "enum":
                name = item[1]
                ast = item[2]
                pe = Proto_enum(name, ast)
                pe.parseAst()
                self.enums[name] = pe

    def compare_enums(self, old_proto_file):
        old_enums = old_proto_file.enums
        new_enums = self.enums
        added_enum_keys = new_enums.keys() - old_enums.keys()
        for key in added_enum_keys:
            print("INFO Add Enum in Message {}: {}".format(key, new_enums[key]))
        deleted_enum_keys = old_enums.keys() - new_enums.keys()
        for key in deleted_enum_keys:
            print("INFO Delete Enum in Message {}: {}".format(key, old_enums[key]))
        shared_enum_keys = new_enums.keys() - added_enum_keys
        added_field_enum_keys = []
        deleted_field_enum_keys = []
        changed_field_enum_keys = []
        for key in shared_enum_keys:
            old_enum = old_enums[key]
            new_enum = new_enums[key]
            added_field_keys = new_enum.keys() - old_enum.keys()
            deleted_field_keys = old_enum.keys() - new_enum.keys()
            shared_field_keys = new_enum.keys() - added_field_keys
            changed_field_keys = {}
            if len(added_field_keys) > 0:
                added_field_enum_keys.append(key)
            for field_name in added_field_keys:
                print(
                    "Add Field in Enum {} Key: {} Value {}".format(
                        key, field_name, new_enum[field_name]
                    )
                )
            if len(deleted_field_keys) > 0:
                deleted_field_enum_keys.append(key)
            for field_name in deleted_field_keys:
                print(
                    "Delete Field in Enum {} Key: {} Value {}".format(
                        key, field_name, old_enum[field_name]
                    )
                )
            for field_name in shared_field_keys:
                old_value = old_enum[field_name]
                new_value = new_enum[field_name]
                if old_value != new_value:
                    changed_field_keys[field_name] = new_enum
                    print(
                        "Delete Field in Enum {} Key: {} OldValue: {} NewValue: {}".format(
                            key, field_name, old_value, new_value
                        )
                    )
            if len(changed_field_enum_keys) > 0:
                changed_field_enum_keys.append(key)
        return (
            added_enum_keys,
            deleted_enum_keys,
            changed_field_enum_keys,
            added_field_enum_keys,
            deleted_field_enum_keys,
        )

    def compare(self, old_proto_file):
        # compare messages change
        old_msgs = old_proto_file.messages
        new_msgs = self.messages
        added_msg_keys = new_msgs.keys() - old_msgs.keys()
        deleted_msg_keys = old_msgs.keys() - new_msgs.keys()
        shared_msg_keys = new_msgs.keys() - added_msg_keys
        changed_field_msg_keys = []
        added_field_msg_keys = []
        deleted_field_msg_keys = []
        for add_msg_key in added_msg_keys:
            print("INFO Added Message {}".format(add_msg_key))
        for deleted_msg_key in deleted_msg_keys:
            print("INFO Deleted Message {}".format(deleted_msg_key))
        for pm_name in shared_msg_keys:
            old_msg = old_msgs[pm_name]
            old_msg_fields = old_msg.fields
            new_msg = new_msgs[pm_name]
            new_msg_fields = new_msg.fields
            added_field_keys = new_msg_fields.keys() - old_msg_fields.keys()
            deleted_field_keys = old_msg_fields.keys() - new_msg_fields.keys()
            if len(added_field_keys) > 0:
                added_field_msg_keys.append(pm_name)
                for field_name in added_field_keys:
                    field = new_msg_fields[field_name]
                    level = "INFO"
                    if field.field_qf == "required":
                        level = "ERROR"
                    print(
                        "{} Added Field In Message {}: {} AST: {} {}".format(level,
                            pm_name, field_name, field.to_string(), old_msg.file.path
                        )
                    )
            if len(deleted_field_keys) > 0:
                deleted_field_msg_keys.append(pm_name)
                for field_name in deleted_field_keys:
                    field = old_msg_fields[field_name]
                    level = 'INFO'
                    if field.field_qf == "required":
                        level = "ERROR"
                    print(
                        "{} Deleted Field In Message #{}: {} AST: {}".format(
                            level, pm_name, field_name, field.to_string()
                        )
                    )
            shared_field_keys = new_msg_fields.keys() - added_field_keys
            changed_fields = {}
            c_type_fields = {}
            c_tag_fields = {}
            c_qf_fields = {}
            for field_name in shared_field_keys:
                old_field = old_msg_fields[field_name]
                new_field = new_msg_fields[field_name]
                if not old_field.is_same(new_field):
                    changed_fields[field_name] = new_field
                    if old_field.tag_number != new_field.tag_number:
                        c_tag_fields[field_name] = new_field
                    if old_field.field_type != new_field.field_type:
                        c_type_fields[field_name] = new_field
                    if old_field.field_qf != new_field.field_qf:
                        c_qf_fields[field_name] = new_field
            if len(changed_fields) > 0:
                changed_field_msg_keys.append(pm_name)
            for field_name in changed_fields:
                field = new_msg_fields[field_name]
                old_field = old_msg_fields[field_name]
                level = 'INFO'
                if old_field.field_qf != 'required' and field.field_qf == 'required':
                    level = 'WARNING'
                
                if old_field.field_qf == 'required' and field.field_qf != 'required':
                    level = 'WARNING'

                if old_field.tag_number != field.tag_number:
                    level = 'ERROR'

                print(
                    "{} Changed Field In Message {}: {} OLD_AST: {} NEW_AST: {} in {}".format(
                        level, pm_name, field_name, old_field.to_string(), field.to_string(), old_msg.file.path
                    )
                )
        #print(
        #    "deleted: {}\tadded: {}\ttchanged: {}".format(
        #        len(deleted_msg_keys), len(added_msg_keys), len(changed_field_msg_keys),
        #    )
        #)
        # print("am {} dm {} cfm{} afm {} dfm {}".format(len(added_msg_keys), len(deleted_msg_keys), len(changed_field_msg_keys), len(added_field_msg_keys) ,len(deleted_field_msg_keys)))
        return (
            added_msg_keys,
            deleted_msg_keys,
            changed_field_msg_keys,
            added_field_msg_keys,
            deleted_field_msg_keys,
        )


class Proto_message:
    def __init__(self, name, ast, f=None):
        self.messages = {}
        self.name = name
        self.ast = ast
        self.fields = {}
        self.file = f
        self.defined_enums = {}

    def parseAst(self):
        for item in self.ast:
            if item[0] == "message":
                name = item[1]
                ast = item[2]
                pm = Proto_message(name, ast, self.file)
                self.messages[name] = pm
                pm.parseAst()
            if item[0] in ["repeated", "optional", "required"]:
                field_qf = item[0]
                field_type = item[1]
                field_name = item[2]
                tag_number = int(item[3])
                pfield = Proto_field(field_type, field_name, field_qf, tag_number, self)
                if len(item) >= 5:
                    default_arr = item[4]
                    if default_arr[0] == "default":
                        default_value = default_arr[1]
                        pfield.default_value = default_value
                        # print("SET DEFAULT VALUE {}".format(default_value))
                self.fields[field_name] = pfield
            if item[0] == "enum":
                name = item[1]
                ast = item[2]
                pe = Proto_enum(name, ast)
                pe.parseAst()
                self.defined_enums[name] = pe
        # check whether the field type is one of the defined enum types within this msg
        self.find_enum_type()

    def find_enum_type(self):
        for field in self.fields.values():
            field_type = field.field_type
            if field_type in self.defined_enums.keys():
                self.defined_enums[field_type].is_used = True
                field.is_enum_type = True
                self.has_enum_type = True
            parent_msg = self.parent
            while(parent_msg):
                if field_type in parent_msg.defined_enums.keys():
                    parent_msg.defined_enums[field_type].is_used = True
                    field.is_enum_type = True
                    self.has_enum_type = True
                parent_msg = parent_msg.parent
                    

            


class Proto_enum:
    def __init__(self, enum_name, ast):
        self.enum_name = enum_name
        self.ast = ast
        self.enum = {}
        self.is_used = False

    def parseAst(self):
        for i in self.ast:
            if i[1].startswith("0x"):
                self.enum[i[0]] = int(i[1], 16)
            else:
                self.enum[i[0]] = int(i[1])


class Proto_field:
    def __init__(self, field_type, field_name, field_qf, tag_number, message):
        self.tag_number = tag_number
        self.field_type = field_type
        self.field_qf = field_qf
        self.field_name = field_name
        self.default_value = None
        self.is_enum_type = False
        self.message = message

    def is_same(self, other_field):
        return (
            self.tag_number == other_field.tag_number
            and self.field_type == other_field.field_type
            and self.field_qf == other_field.field_qf
        )

    def to_string(self):
        return "{} {} {} = {}".format(
            self.field_qf, self.field_type, self.field_name, self.tag_number
        )


class Version_class:
    def __init__(self, folder, tag):
        self.folder = folder
        self.tag = tag
        self.java_files = {}
        self.files = []
        self.proto_file_paths = []
        self.proto_files = {}

    def build(self):
        self.extractFiles()

    def extractFiles(self):
        cmd = "cd {}; git checkout -f {}".format(self.folder, self.tag)
        os.system(cmd)
        self.files = []
        for (dirpath, dirnames, filenames) in walk(self.folder):
            for filename in filenames:
                if filename.endswith(".java"):
                    class_name = filename[0:-5]
                    path = dirpath + "/" + filename
                    self.files.append(path)
                if filename.endswith(".proto"):
                    class_name = filename[0:-6]
                    path = dirpath + "/" + filename
                    self.files.append(path)

    def protoOverview(self):
        self.parseFiles([], ["proto"])
        all_fields = []
        all_msgs_dic = {}
        outside_enums_dic = {}
        for key in self.proto_files.keys():
            pf = self.proto_files[key]
            all_msgs_dic.update(pf.messages)
            outside_enums_dic.update(pf.enums)
        all_msgs = all_msgs_dic.values()
        outside_enums = outside_enums_dic.values()
        print(len(all_msgs))
        all_all_msgs = []       
        for msg in all_msgs:
            all_all_msgs += self.extract_every_msgs(msg)
        all_all_msgs += all_msgs
        inside_enums = [e for msg in all_all_msgs for e in msg.defined_enums.values()]
        all_enums = list(outside_enums) + inside_enums
        for msg in all_all_msgs:
            all_fields += msg.fields.values()
            for field in msg.fields.values():
                self.find_enum_type(field, all_msgs_dic, all_enums)
                field_type = field.field_type
                if field_type in outside_enums_dic:
                    outside_enums_dic[field_type].is_true = True
        print("THERE ARE {} msgs".format(len(all_all_msgs)))

        msgs_used_enums = [m for m in all_msgs if m.has_enum_type]
        fields_used_enums = [f for f in all_fields if f.is_enum_type]
        used_enums = [e for e in all_enums if e.is_used]
        unused_enums = [e for e in all_enums if not e.is_used] 
        for enum in unused_enums:
            print(enum.enum_name)
            os.system("grep {} --include=\"*.proto\" {} -r >> grep.log".format(enum.enum_name, self.folder))
        print(
            "-------MESSAGE BREAKDOWN-------\nThere are {} messages, {} of them has used enum within them".format(
                len(all_msgs), len(msgs_used_enums)
            )
        )
        print(
            "-------SELF DEFINED ENUMS WITHIN MESSAGES-------\nThere are {} enums defined within msgs".format(
                len(inside_enums)
            )
        )
        print(
            "-------ENUM BREAKDOWN-------\nThere are {} of enums, {} of them has been used".format(
                len(all_enums), len(used_enums)
            )
        )
        # breakdown of field type
        optional_fields = [f for f in all_fields if f.field_qf == "optional"]
        required_fields = [f for f in all_fields if f.field_qf == "required"]
        repeated_fields = [f for f in all_fields if f.field_qf == "repeated"]
        default_value_fields = [f for f in all_fields if f.default_value != None]
        print(
            "-------FIELD BREAKDOWN-------\nThere are {} fields in total, {} are optional, {} are required, {} are repeated, {} have set default value, {} are of enum type".format(
                len(all_fields),
                len(optional_fields),
                len(required_fields),
                len(repeated_fields),
                len(default_value_fields),
                len(fields_used_enums),
            )
        )
    def extract_every_msgs(self, msg):
        results = []
        if type(msg) == Proto_message:
            if len(msg.messages) == 0:
                results.append(msg)
                return results
            for m in msg.messages.values():
                results += self.extract_every_msgs(m)
        return results

    def find_enum_type(self, field, all_msgs, all_enums):
        field_type = field.field_type
        name_arr = field_type.split('.')
        msgs = all_msgs
        if len(name_arr) == 1:
            enum_name = name_arr[-1]
            if enum_name in field.message.defined_enums:
                field.message.defined_enums[enum_name].is_used = True
            for e in all_enums:
                if e.enum_name == enum_name:
                    e.is_used = True
        if len(name_arr) >= 2:
            enum_name = name_arr[-1]  # the last element is the name of enum
            print("enum_name is {}".format(field_type))
            for name in name_arr:
                key = field.message.path + "_" + name
                if key in msgs:
                    message = msgs[key]
                    if enum_name in message.defined_enums:
                        message.defined_enums[enum_name].is_used = True
                        field.is_enum_type = True
                        print("ENUM type {} in {} is used in {}".format(enum_name, message.name, field_type))
                        break
                    else:
                        msgs = message.messages
                else:
                    break
            

    # if changed files are empty or None, then will process all certain files
    def parseFiles(self, changed_files, file_types=None):
        for path in self.files:
            if os.path.exists(path):
                # print("path " + path)
                if len(changed_files) == 0 or (
                    len(changed_files) > 0 and path in changed_files
                ):
                    try:
                        contents = open(path).read()
                        if path.endswith(".java"):
                            if (not file_types) or "java" in file_types:
                                ast = javalang.parse.parse(contents)
                                jf = Java_file(path, ast, contents)
                                self.java_files[path] = jf
                                jf.parseAst()
                        if path.endswith(".proto"):
                            if (not file_types) or "proto" in file_types:
                                # print(path)
                                # print(contents)
                                ast = parser.parseString(contents)
                                pf = Proto_file(path, ast, contents)
                                self.proto_files[path] = pf
                                pf.parseAst()
                    except SyntaxError:
                        print("syntax error " + path)
