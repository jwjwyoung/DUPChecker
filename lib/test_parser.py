from protobuf_parser import parser
from protobuf_parser import enumDefn
from class_class import Proto_file
import os
from os import walk

test_s = """
enum INodeType {
  I_NODE = 3;
  I_I = 0x1;
  I_II = 2;
}
"""
p = parser.parseString(test_s)
assert len(p[0][2]) == 3
assert type(p[0][2][0][1]) == str
assert p[0][2][0][1] == "3"
assert p[0][2][1][1] == "0x1"
assert p[0][2][2][1] == "2"

test_msg = """
message ExportRequest {
  required Scan scan = 1;
  required string outputPath = 2;
  optional bool compressed = 3 [default = false];
  optional string compressType = 4;
  optional string compressCodec = 5;
  optional DelegationToken fsToken = 6;
}
"""
p = parser.parseString(test_msg)


path = "../hbase/hbase-protocol-shaded/src/main/protobuf/BucketCacheEntry.proto"
con = open(path).read()
ast = parser.parseString(con)
pf = Proto_file(path, ast, con)
pf.parseAst()
print(len(pf.messages))

cnt = 0
total = 0
lz_cnt = 0
for (dirpath, dirnames, filenames) in walk("../hbase"):
    for filename in filenames:
        if filename.endswith(".proto"):
            total += 1
            try:
                print(filename)
                class_name = filename[0:-6]
                path = dirpath + "/" + filename
                print(path)
                con = open(path).read()
                ast = parser.parseString(con)
                pf = Proto_file(path, ast, con)
                pf.parseAst()
                print(len(pf.messages))
                cnt += 1
                if len(pf.messages) > 0:
                    lz_cnt += 1
            except:
                print("parse error" + path)
print("{} / {} = {}% {}".format(cnt, total, cnt * 100.0 / total, lz_cnt))
