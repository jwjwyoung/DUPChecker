## ptsd is a pure python thrift parser built using PLY ##

to use, just pip install into a virtualenv or reference the eggs a la carte.


#### using ####
to access the thrift ast:
```python
>>> from ptsd.parser import Parser
>>> with open('testdata/thrift_test.thrift') as fp:
...   tree = Parser().parse(fp.read())
...
>>> tree.includes
[]
>>> tree.namespaces
[<ptsd.ast.Namespace object at 0x1006e4f10>, <ptsd.ast.Namespace object at 0x1006e4cd0>, <ptsd.ast.Namespace object at 0x1006e4d90>,
<ptsd.ast.Namespace object at 0x1006e5650>, <ptsd.ast.Namespace object at 0x1006dd490>, <ptsd.ast.Namespace object at 0x1006dda90>,
<ptsd.ast.Namespace object at 0x1006e5910>, <ptsd.ast.Namespace object at 0x1006e5850>, <ptsd.ast.Namespace object at 0x1006e5b10>,
<ptsd.ast.Namespace object at 0x1006e5510>, <ptsd.ast.Namespace object at 0x1006d9d10>, <ptsd.ast.Namespace object at 0x1006d9e50>,
<ptsd.ast.Namespace object at 0x1006e2ed0>, <ptsd.ast.Namespace object at 0x1006d9d50>, <ptsd.ast.Namespace object at 0x1006d9c90>,
<ptsd.ast.Namespace object at 0x1006d9e90>, <ptsd.ast.Namespace object at 0x1006eeed0>]
>>> tree.body
[<ptsd.ast.Enum object at 0x10122d310>, <ptsd.ast.Const object at 0x10122d410>, <ptsd.ast.Typedef object at 0x1006eee90>,
<ptsd.ast.Struct object at 0x10122d710>, <ptsd.ast.Struct object at 0x10122d910>, <ptsd.ast.Struct object at 0x10122dc90>,
<ptsd.ast.Struct object at 0x10122df50>, <ptsd.ast.Struct object at 0x10122c310>, <ptsd.ast.Struct object at 0x10122c650>,
<ptsd.ast.Struct object at 0x10122cb10>, <ptsd.ast.Exception_ object at 0x10122ce50>, <ptsd.ast.Exception_ object at 0x10122ce10>,
<ptsd.ast.Struct object at 0x10122a150>, <ptsd.ast.Struct object at 0x10122a1d0>, <ptsd.ast.Service object at 0x10122bf90>,
<ptsd.ast.Service object at 0x10122d590>, <ptsd.ast.Struct object at 0x10122efd0>, <ptsd.ast.Struct object at 0x101230a90>,
<ptsd.ast.Struct object at 0x101230d10>, <ptsd.ast.Struct object at 0x101230f90>, <ptsd.ast.Struct object at 0x101231250>,
<ptsd.ast.Struct object at 0x101231a90>, <ptsd.ast.Struct object at 0x101231b50>, <ptsd.ast.Struct object at 0x101231d10>,
<ptsd.ast.Struct object at 0x1012330d0>, <ptsd.ast.Struct object at 0x101233590>, <ptsd.ast.Struct object at 0x101233610>,
<ptsd.ast.Struct object at 0x101233710>, <ptsd.ast.Struct object at 0x101233a10>, <ptsd.ast.Struct object at 0x101233a50>]
>>>
```

each ast object also has its line spans and character spans available:
```python
>>> tree.namespaces[0]._lexspan
(958, 975)
>>> tree.namespaces[0]._linespan
(3, 3)
>>> print(tree.namespaces[0])
namespace c_glib TTest
```

#### bin/ptsd ####

a basic loader script is available in the bin directory that parses a thrift
file and all its includes and prints out the reformatted ast in parseable
thrift:

```console
mba=; PYTHONPATH=.deps/ply-3.4-py2.6.egg:. bin/ptsd testdata/thrift_test.thrift
Processing /Users/wickman/clients/ptsd/testdata/thrift_test.thrift
Dumping /Users/wickman/clients/ptsd/testdata/thrift_test.thrift

namespace c_glib TTest
namespace java thrift.test
namespace cpp thrift.test
namespace rb Thrift.Test
namespace perl ThriftTest
namespace csharp Thrift.Test
namespace js ThriftTest
namespace st ThriftTest
namespace py ThriftTest
namespace py.twisted ThriftTest
namespace go ThriftTest
namespace php ThriftTest
namespace delphi Thrift.Test
namespace cocoa ThriftTest
namespace noexist ThriftTest
namespace cpp.noexist ThriftTest
namespace * thrift.test

enum Numberz {
  ONE = 1
  TWO = 2
  THREE = 3
  FIVE = 5
  SIX = 6
  EIGHT = 8
}

const Numberz myNumberz = Numberz.ONE

typedef i64 UserId

struct Bonk {
  1: string message
  2: i32 type
}

struct Bools {
  1: bool im_true
  2: bool im_false
}

struct Xtruct {
  1: string string_thing
  4: byte byte_thing
  9: i32 i32_thing
  11: i64 i64_thing
}

struct Xtruct2 {
  1: byte byte_thing
  2: Xtruct struct_thing
  3: i32 i32_thing
}

struct Xtruct3 {
  1: string string_thing
  4: i32 changed
  9: i32 i32_thing
  11: i64 i64_thing
}

struct Insanity {
  1: map<Numberz, UserId> userMap
  2: list<Xtruct> xtructs
}

struct CrazyNesting {
  1: string string_field
  2: set<Insanity> set_field
  3: required list<map<set<i32>, map<i32, set<list<map<Insanity, string>>>>>> list_field
  4: binary binary_field
}

exception Xception {
  1: i32 errorCode
  2: string message
}

exception Xception2 {
  1: i32 errorCode
  2: Xtruct struct_thing
}

struct EmptyStruct {

}

struct OneField {
  1: EmptyStruct field
}

service ThriftTest {
  void testVoid()
  string testString(1: string thing)
  byte testByte(1: byte thing)
  i32 testI32(1: i32 thing)
  i64 testI64(1: i64 thing)
  double testDouble(1: double thing)
  Xtruct testStruct(1: Xtruct thing)
  Xtruct2 testNest(1: Xtruct2 thing)
  map<i32, i32> testMap(1: map<i32, i32> thing)
  map<string, string> testStringMap(1: map<string, string> thing)
  set<i32> testSet(1: set<i32> thing)
  list<i32> testList(1: list<i32> thing)
  Numberz testEnum(1: Numberz thing)
  UserId testTypedef(1: UserId thing)
  map<i32, map<i32, i32>> testMapMap(1: i32 hello)
  map<UserId, map<Numberz, Insanity>> testInsanity(1: Insanity argument)
  Xtruct testMulti(1: byte arg0, 2: i32 arg1, 3: i64 arg2, 4: map<i16,
  string> arg3, 5: Numberz arg4, 6: UserId arg5)
  void testException(1: string arg) throws (1: Xception err1)
  Xtruct testMultiException(1: string arg0, 2: string arg1) throws (1:
  Xception err1 2: Xception2 err2)
  oneway void testOneway(1: i32 secondsToSleep)
}

service SecondService {
  void blahBlah()
}

struct VersioningTestV1 {
  1: i32 begin_in_both
  3: string old_string
  12: i32 end_in_both
}

struct VersioningTestV2 {
  1: i32 begin_in_both
  2: i32 newint
  3: byte newbyte
  4: i16 newshort
  5: i64 newlong
  6: double newdouble
  7: Bonk newstruct
  8: list<i32> newlist
  9: set<i32> newset
  10: map<i32, i32> newmap
  11: string newstring
  12: i32 end_in_both
}

struct ListTypeVersioningV1 {
  1: list<i32> myints
  2: string hello
}

struct ListTypeVersioningV2 {
  1: list<string> strings
  2: string hello
}

struct GuessProtocolStruct {
  7: map<string, string> map_field
}

struct LargeDeltas {
  1: Bools b1
  10: Bools b10
  100: Bools b100
  500: bool check_true
  1000: Bools b1000
  1500: bool check_false
  2000: VersioningTestV2 vertwo2000
  2500: set<string> a_set2500
  3000: VersioningTestV2 vertwo3000
  4000: list<i32> big_numbers
}

struct NestedListsI32x2 {
  1: list<list<i32>> integerlist
}

struct NestedListsI32x3 {
  1: list<list<list<i32>>> integerlist
}

struct NestedMixedx2 {
  1: list<set<i32>> int_set_list
  2: map<i32, set<string>> map_int_strset
  3: list<map<i32, set<string>>> map_int_strset_list
}

struct ListBonks {
  1: list<Bonk> bonk
}

struct NestedListsBonk {
  1: list<list<list<Bonk>>> bonk
}

struct BoolTest {
  1: bool b
  2: string s
}

struct StructA {
  1: required string s
}

struct StructB {
  1: StructA aa
  2: required StructA ab
}


took 113.5ms
```
