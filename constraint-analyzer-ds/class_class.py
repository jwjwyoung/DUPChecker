import os
import javalang
from os import walk
from javalang.tree import MethodDeclaration
from javalang.tree import FormalParameter
from javalang.tree import BasicType

class Java_file():
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


class Java_class():

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
					end_index = body[i+1].position.line
				else:
					end_index = last_index
				con = split_con[start_index:end_index - 1]
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
						if str(method) != str(old_method) and method_src != old_method_src:
							changed_serilize.append([old_method_src, method_src])
					except:
						print("cannot transfer to str")
				if old_method.throws != method.throws:
					changed_excep_methods.append(method)
		return changed_excep_methods, changed_serilize



class Java_method():
	name = ""
	exceptions = []
	params = []
	def __init__(self):
		exceptions = []

class Version_class():
	def __init__(self, folder, tag):
		self.folder = folder
		self.tag = tag
		self.java_files = {}
		self.files = []

	def build(self):
		self.extractFiles()

	def extractFiles(self):
		cmd = 'cd {}; git checkout -f {}'.format(self.folder, self.tag)
		os.system(cmd)
		self.files = []
		for (dirpath, dirnames, filenames) in walk(self.folder):
			for filename in filenames:
				if filename.endswith(".java"):
					class_name = filename[0:-5]
					path = dirpath + "/" + filename
					self.files.append(path)

	def parseFiles(self, changed_files):
		for path in self.files:
			if path in changed_files and os.path.exists(path):
				#print("path " + path)
				try:
					contents = open(path).read()
					ast = javalang.parse.parse(contents)
					jf = Java_file(path, ast, contents)
					self.java_files[path] = jf
					jf.parseAst()
				except:
					print("syntax error")

