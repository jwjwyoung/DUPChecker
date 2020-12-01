from protobuf_parser import parser
from protobuf_parser import enumDefn
from class_class import Proto_file
import os
from os import walk
from class_class import Version_class

tag = "master"
folder = "../hbase"
v = Version_class(folder, tag)
v.build()
v.protoOverview()
