# protobuf_thrift_thrift_parser.py
#
#  simple thrift_thrift_parser for parsing protobuf .proto files
#
#  Copyright 2010, Paul McGuire
#

from pyparsing import (
    Word,
    alphas,
    alphanums,
    Regex,
    Suppress,
    Forward,
    Group,
    oneOf,
    ZeroOrMore,
    Optional,
    delimitedList,
    Keyword,
    restOfLine,
    quotedString,
    Dict,
    cStyleComment,
)

ident = Word(alphas + "_", alphanums + "_.").setName("identifier")

integer = Regex(r"[+-]?\d+")
integer = Regex(r"[-+]?([0-9]*\.[0-9]+|[0-9]+)")
# (0x)?[0-9abcdef]+
hex_integer = Regex(r"[+-]?(?:0x)[0-9a-z]+")

LBRACE, RBRACE, LBRACK, RBRACK, LPAR, RPAR, EQ, SEMI, COMMA, COLON, L1, R1, Q = map(Suppress, "{}[]()=;,:<>\"")

kwds = """typedef namespace exception struct union required optional repeated enum extensions extends extend 
          to package service rpc returns true false option import syntax throws list map set void const"""
for kw in kwds.split():
    exec("%s_ = Keyword('%s')" % (kw.upper(), kw))

messageBody = Forward()

messageDefn = STRUCT_ - ident("messageId") + LBRACE + messageBody("body") + RBRACE

unionDefn = UNION_ - ident("messageId") + LBRACE + messageBody("body") + RBRACE

ts = (
    oneOf(
        """double float int32 int64 uint32 uint64 sint32 sint64 
                    fixed32 fixed64 sfixed32 sfixed64 bool string bytes i16 i32 Text i64 Bytes void string"""
    )
    | ident
)

listType = (LIST_ | SET_) + L1  + ts + R1
mapType = MAP_ + L1 + ts + COMMA + ts + R1

#typespec = ZeroOrMore(Group(MAP_ | LIST_ | SET_))  + ZeroOrMore(L1) + ts + ZeroOrMore(COMMA + ts) + ZeroOrMore(R1)

ts2 = Forward()

ts2 << (listType | mapType | ts)

listType1 = (LIST_ | SET_) + L1  + ts2 + R1

mapType1 = MAP_ + L1 + ts2 + COMMA + ts2 + R1

typespec = Forward()

typespec << (listType1 | mapType1 | ts2)

floatV = Regex(r"[-+]?([0-9]*\.[0-9]+|[0-9]+)")

rvalue = integer | TRUE_ | FALSE_ | ident 
P2 = "{" + ZeroOrMore((ZeroOrMore(Q) + ident + ZeroOrMore(Q) + COLON + (rvalue | "{}"))) + "}"

quoted = (Q + rvalue + Q)

fieldDirective = LBRACK + Group(ident + EQ + rvalue) + RBRACK
fieldDefn = (
    integer("fieldint")
    + COLON
    + ZeroOrMore(REQUIRED_ | OPTIONAL_ | REPEATED_)("fieldQualifier")
    + typespec
    + ident("ident")
    + ZeroOrMore("=" + (rvalue | quoted | ident | hex_integer | P2 ))
    + ZeroOrMore(COMMA)
    + ZeroOrMore(SEMI)
)
fieldDefn2 = (
    integer("fieldint")
    + COLON
    - ident
    + ident("ident")
    + ZeroOrMore(COMMA)
)

versionDefn = CONST_ + typespec + ident("ident") +  EQ + P2
# enumDefn ::= 'enum' ident '{' { ident '=' integer ';' }* '}'
enumDefn = (
    ENUM_("typespec")
    - ident("name")
    + LBRACE
    + Dict(
        ZeroOrMore(
            Group(
                ident + ZeroOrMore(EQ + (hex_integer | integer)) + ZeroOrMore(fieldDirective) + ZeroOrMore(COMMA) + ZeroOrMore(SEMI)
            )
        )
    )("values")
    + RBRACE
)


# extensionsDefn ::= 'extensions' integer 'to' integer ';'
extensionsDefn = EXTENSIONS_ - integer + TO_ + integer + SEMI

# messageExtension ::= 'extend' ident '{' messageBody '}'
messageExtension = EXTEND_ - ident + LBRACE + messageBody + RBRACE

# messageBody ::= { fieldDefn | enumDefn | messageDefn | extensionsDefn | messageExtension }*
messageBody << Group(
    ZeroOrMore(
        Group(fieldDefn | enumDefn | messageDefn | extensionsDefn | messageExtension)
    )
)




# packageDirective ::= 'package' ident [ '.' ident]* ';'


packageDirective = Group(PACKAGE_ - delimitedList(ident, ".", combine=True) + SEMI)

namespaceDefn = NAMESPACE_ - ident("messageId") + delimitedList(ident, ".", combine=True)

exceptionDefn = EXCEPTION_ - ident("messageId") + LBRACE + messageBody("body") + RBRACE


exceptionsDefn = LPAR + fieldDefn + ZeroOrMore(fieldDefn) + RPAR

# methodDefn ::= 'void' ident '(' [ ident ] ')' 'returns' '(' [ ident ] ')' ';'
methodDefn = (
    typespec("typespec")
    - ident("methodName")
    + LPAR
    + ZeroOrMore(Group(fieldDefn))
    + RPAR
    + ZeroOrMore(THROWS_ + Group(exceptionsDefn))
) 

methodDefn2 = (
    ident("ident")
    + VOID_
    - ident("methodName")
    + LPAR
    + ZeroOrMore(Group(fieldDefn))
    + RPAR
    + ZeroOrMore(THROWS_ + Group(exceptionsDefn))
) 

# serviceDefn ::= 'service' ident '{' methodDefn* '}'
serviceDefn = (
    SERVICE_ - ident("serviceName") + LBRACE + ZeroOrMore(Group(methodDefn)) + RBRACE
)
typeDefn = TYPEDEF_ - typespec("typespec") + ident("ident")

comment = "//" + restOfLine | cStyleComment
comment1 = "#" + restOfLine

importDirective = IMPORT_ - (quotedString("importFileSpec")) + SEMI

optionDirective = (
    OPTION_
    - ident("optionName")
    + EQ
    + (quotedString("optionValue") | TRUE_ | FALSE_ | ident)
    + SEMI
)

topLevelStatement = Group(messageDefn | unionDefn | messageExtension | enumDefn | serviceDefn | namespaceDefn | typeDefn | exceptionDefn | versionDefn)

thrift_parser = Optional(packageDirective) + ZeroOrMore(topLevelStatement)

thrift_parser.ignore(comment)
thrift_parser.ignore(comment1)
thrift_parser.ignore("option " + restOfLine)
thrift_parser.ignore("import " + restOfLine)
thrift_parser.ignore("syntax " + restOfLine)
thrift_parser.ignore("service " + restOfLine)
thrift_parser.ignore("const " + restOfLine)
#thrift_thrift_parser.ignore("map<" + restOfLine)  # don't handle map<x, x> currently, TBD

# contents = open("../hbase/hbase-thrift/src/main/resources/org/apache/hadoop/hbase/thrift/Hbase.thrift").read()
# contents = contents.replace(" 0x", " x")
contents ='''
const string VERSION = "20.1.0"
struct CounterColumn {
    1: required binary name = 0.0,
    2: required i64 value
}
'''
#contents = open("cassandra/interface/cassandra.thrift").read()
# r = thrift_parser.parseString(contents)
# print(r)