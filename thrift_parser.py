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
# (0x)?[0-9abcdef]+
hex_integer = Regex(r"[+-]?(?:0x)[0-9a-z]+")

LBRACE, RBRACE, LBRACK, RBRACK, LPAR, RPAR, EQ, SEMI, COMMA, COLON, L1, R1 = map(Suppress, "{}[]()=;,:<>")

kwds = """typedef namespace exception struct required optional repeated enum extensions extends extend 
          to package service rpc returns true false option import syntax throws list map set"""
for kw in kwds.split():
    exec("%s_ = Keyword('%s')" % (kw.upper(), kw))

messageBody = Forward()

messageDefn = STRUCT_ - ident("messageId") + LBRACE + messageBody("body") + RBRACE

ts = (
    oneOf(
        """double float int32 int64 uint32 uint64 sint32 sint64 
                    fixed32 fixed64 sfixed32 sfixed64 bool string bytes i16 i32 Text i64 Bytes void string"""
    )
    | ident
)

listType = (LIST_ + L1  + ts + R1)
mapType = (MAP_ + L1 + ts + COMMA + ts + R1)


typespec = ZeroOrMore(Group(MAP_ | LIST_ | SET_))  + ZeroOrMore(L1) + ts + ZeroOrMore(COMMA + ts) + ZeroOrMore(R1)

rvalue = integer | TRUE_ | FALSE_ | ident

fieldDirective = LBRACK + Group(ident + EQ + rvalue) + RBRACK
fieldDefn = (
    integer("fieldint")
    + COLON
    + ZeroOrMore(REQUIRED_ | OPTIONAL_ | REPEATED_)("fieldQualifier")
    + typespec
    + ident("ident")
    + ZeroOrMore(EQ + (rvalue | ('"' + ident + '"') | ident | hex_integer))
    + ZeroOrMore(COMMA)
)
fieldDefn2 = (
    integer("fieldint")
    + COLON
    - ident
    + ident("ident")
    + ZeroOrMore(COMMA)
)

# enumDefn ::= 'enum' ident '{' { ident '=' integer ';' }* '}'
enumDefn = (
    ENUM_("typespec")
    - ident("name")
    + LBRACE
    + Dict(
        ZeroOrMore(
            Group(
                ident + EQ + (hex_integer | integer) + ZeroOrMore(fieldDirective) + ZeroOrMore(COMMA)
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

# serviceDefn ::= 'service' ident '{' methodDefn* '}'
serviceDefn = (
    SERVICE_ - ident("serviceName") + LBRACE + ZeroOrMore(Group(methodDefn)) + RBRACE
)
typeDefn = TYPEDEF_ - typespec("typespec") + ident("ident")

comment = "//" + restOfLine | cStyleComment

importDirective = IMPORT_ - (quotedString("importFileSpec")) + SEMI

optionDirective = (
    OPTION_
    - ident("optionName")
    + EQ
    + (quotedString("optionValue") | TRUE_ | FALSE_ | ident)
    + SEMI
)

topLevelStatement = Group(messageDefn | messageExtension | enumDefn | serviceDefn | namespaceDefn | typeDefn | exceptionDefn)

thrift_parser = Optional(packageDirective) + ZeroOrMore(topLevelStatement)

thrift_parser.ignore(comment)
thrift_parser.ignore("option " + restOfLine)
thrift_parser.ignore("import " + restOfLine)
thrift_parser.ignore("syntax " + restOfLine)
#thrift_thrift_parser.ignore("map<" + restOfLine)  # don't handle map<x, x> currently, TBD

# contents = open("../hbase/hbase-thrift/src/main/resources/org/apache/hadoop/hbase/thrift/Hbase.thrift").read()
# contents = contents.replace(" 0x", " x")
# r = thrift_thrift_parser.parseString(contents)
# print(r)