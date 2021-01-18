# protobuf_parser.py
#
#  simple parser for parsing protobuf .proto files
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
hex_integer = Regex(r"[+-]?(?:0x)[0-9abcdef]+")


LBRACE, RBRACE, LBRACK, RBRACK, LPAR, RPAR, EQ, SEMI = map(Suppress, "{}[]()=;")

kwds = """message required optional repeated enum extensions extends extend 
          to package service rpc returns true false option import syntax"""
for kw in kwds.split():
    exec("%s_ = Keyword('%s')" % (kw.upper(), kw))

messageBody = Forward()

messageDefn = MESSAGE_ - ident("messageId") + LBRACE + messageBody("body") + RBRACE

typespec = (
    oneOf(
        """double float int32 int64 uint32 uint64 sint32 sint64 
                    fixed32 fixed64 sfixed32 sfixed64 bool string bytes"""
    )
    | ident
)
rvalue = integer | TRUE_ | FALSE_ | ident
fieldDirective = LBRACK + Group(ident + EQ + rvalue) + RBRACK
fieldDefn = (
    (REQUIRED_ | OPTIONAL_ | REPEATED_)("fieldQualifier")
    - typespec("typespec")
    + ident("ident")
    + EQ
    + integer("fieldint")
    + ZeroOrMore(fieldDirective)
    + SEMI
    + ZeroOrMore(SEMI)
)

# enumDefn ::= 'enum' ident '{' { ident '=' integer ';' }* '}'
enumDefn = (
    ENUM_("typespec")
    - ident("name")
    + LBRACE
    + Dict(
        ZeroOrMore(
            Group(
                ident + EQ + (hex_integer | integer) + ZeroOrMore(fieldDirective) + SEMI
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

# methodDefn ::= 'rpc' ident '(' [ ident ] ')' 'returns' '(' [ ident ] ')' ';'
methodDefn = (
    RPC_
    - ident("methodName")
    + LPAR
    + Optional(ident("methodParam"))
    + RPAR
    + RETURNS_
    + LPAR
    + Optional(ident("methodReturn"))
    + RPAR
) + SEMI

# serviceDefn ::= 'service' ident '{' methodDefn* '}'
serviceDefn = (
    SERVICE_ - ident("serviceName") + LBRACE + ZeroOrMore(Group(methodDefn)) + RBRACE
)


# packageDirective ::= 'package' ident [ '.' ident]* ';'
packageDirective = Group(PACKAGE_ - delimitedList(ident, ".", combine=True) + SEMI)

comment = "//" + restOfLine | cStyleComment

importDirective = IMPORT_ - (quotedString("importFileSpec")) + SEMI

optionDirective = (
    OPTION_
    - ident("optionName")
    + EQ
    + (quotedString("optionValue") | TRUE_ | FALSE_ | ident)
    + SEMI
)

topLevelStatement = Group(messageDefn | messageExtension | enumDefn | serviceDefn)

parser = Optional(packageDirective) + ZeroOrMore(topLevelStatement)

parser.ignore(comment)
parser.ignore("option " + restOfLine)
parser.ignore("import " + restOfLine)
parser.ignore("syntax " + restOfLine)
parser.ignore("map<" + restOfLine)  # don't handle map<x, x> currently, TBD
