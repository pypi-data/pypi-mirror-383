#@+leo-ver=5-thin
#@+node:ekr.20231103124615.1: * @file ../modes/rust.py
# Leo colorizer control file for rust mode.
# This file is in the public domain.

import re
import string
from leo.core import leoGlobals as g

#@+<< rust: properties dict >>
#@+node:ekr.20250106042726.1: ** << rust: properties dict >>
# Properties for rust mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "doubleBracketIndent": "false",
    "indentCloseBrackets": "}",
    "indentNextLine": "\\s*(((if|while)\\s*\\(|else\\s*|else\\s+if\\s*\\(|for\\s*\\(.*\\))[^{;]*)",
    "indentOpenBrackets": "{",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
    "wordBreakChars": ",+-=<>/?^&*",
}
#@-<< rust: properties dict >>
#@+<< rust: attributes dicts >>
#@+node:ekr.20250105164117.1: ** << rust: attributes dicts >>
# Attributes dict for rust_main ruleset.
rust_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]_]+[lL]?|[[:digit:]_]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for rust mode.
attributesDictDict = {
    "rust_main": rust_main_attributes_dict,
}
#@-<< rust: attributes dicts >>
#@+<< rust: keywords dicts >>
#@+node:ekr.20250106043953.1: ** << rust: keywords dicts >>
# Keywords dict for rust_main ruleset.
rust_main_keywords_dict = {
    'Self': 'keyword1',
    'abstract': 'keyword1',
    'as': 'keyword1',
    'async': 'keyword1',
    'become': 'keyword1',
    'bool': 'keyword2',
    'box': 'keyword1',
    'break': 'keyword1',
    'const': 'keyword1',
    'continue': 'keyword1',
    'crate': 'keyword1',
    'do': 'keyword1',
    'dyn': 'keyword1',
    'else': 'keyword1',
    'enum': 'keyword1',
    'extern': 'keyword1',
    'false': 'keyword1',
    'final': 'keyword1',
    'fn': 'keyword1',
    'for': 'keyword1',
    'i16': 'keyword2',
    'i32': 'keyword2',
    'i64': 'keyword2',
    'i8': 'keyword2',
    'if': 'keyword1',
    'impl': 'keyword1',
    'in': 'keyword1',
    'let': 'keyword1',
    'loop': 'keyword1',
    'macro': 'keyword1',
    'match': 'keyword1',
    'mod': 'keyword1',
    'move': 'keyword1',
    'mut': 'keyword1',
    'override': 'keyword1',
    'priv': 'keyword1',
    'pub': 'keyword1',
    'ref': 'keyword1',
    'return': 'keyword1',
    'self': 'keyword1',
    'static': 'keyword1',
    'str': 'keyword2',
    'struct': 'keyword1',
    'super': 'keyword1',
    'trait': 'keyword1',
    'true': 'keyword1',
    'try': 'keyword1',
    'type': 'keyword1',
    'typeof': 'keyword1',
    'u16': 'keyword2',
    'u32': 'keyword2',
    'u64': 'keyword2',
    'u8': 'keyword2',
    'unsafe': 'keyword1',
    'unsized': 'keyword1',
    'use': 'keyword1',
    'usize': 'keyword2',
    'vec!': 'keyword2',
    'virtual': 'keyword1',
    'where': 'keyword1',
    'while': 'keyword1',
    'yield': 'keyword1',
    'Some': 'keyword3',
    'None': 'keyword3',
    'Result': 'keyword3',
    'Err': 'keyword3',
    'Ok': 'keyword3',
    'include_bytes': 'keyword2',
    'include_str': 'keyword2',
}

# Dictionary of keywords dictionaries for rust mode.
keywordsDictDict = {
    "rust_main": rust_main_keywords_dict,
}
#@-<< rust: keywords dicts >>
#@+<< rust: rules >>
#@+node:ekr.20250105163810.1: ** << rust: rules >>
# Rules for rust_main ruleset.
#@+others
#@+node:ekr.20250106042808.3: *3* function: rust_rule2
def rust_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")
#@+node:ekr.20250106054207.1: *3* function: rust_slash
def rust_slash(colorer, s, i) -> int:

    def has_tag(i: int, pattern: str) -> int:
        m = pattern.match(s, i)
        n = len(m.group(0)) if m else 0
        return n if n > 2 else 0

    delegate = 'rest_comments'

    # Case 1: match entire line.
    if g.match(s, i, '///'):
        colorer.match_seq(s, i, kind='comment1', seq='///')
        return colorer.match_eol_span(s, i + 3, kind=None, delegate=delegate)

    # Case 2: match_span constructs, delegated to rust.
    match_span_table = (
        ('/**', 'comment3'),
        ('/*!', 'comment3'),
        ('/*', 'comment1'),
    )
    for begin, kind in match_span_table:
        if g.match(s, i, begin):
            return colorer.match_span(s, i,
                kind=kind, begin=begin, end="*/", delegate=delegate)

    # Case 3: match_seq constructs.
    match_seq_table = (
        ('//', 'comment2', colorer.match_eol_span),
        ('/', 'operator', colorer.match_plain_seq),
    )
    for seq, kind, matcher in match_seq_table:
        if g.match(s, i, seq):
            return matcher(s, i, kind=kind, seq=seq)

    # Fail.
    return i + 1
#@+node:ekr.20250106062326.1: *3* rust: strings and chars, with escapes
#@+node:ekr.20250106042808.5: *4* function: rust_char
char_patterns = (
    # '\u{7FFF}'
    re.compile(r"'\\u\{[0-7][0-7a-fA-F]{3}\}'"),
    # '\x7F'
    re.compile(r"'\\x[0-7][0-7a-fA-F]'"),
    # '\n', '\r', '\t', '\\', '\0', '\'', '\"'
    re.compile(r"'\\[\\\"'nrt0]'"),
    # 'x' where x is any unicode character.
    re.compile(r"'.'", re.UNICODE),
    # Lifetime: must be the *last* pattern matched.
    re.compile(r"('static|'[a-zA-Z_])\b")
)

def rust_char(colorer, s, i):

    # Match all valid patterns.
    for pattern in char_patterns:
        m = pattern.match(s, i)
        if m:
            return colorer.match_seq(s, i, kind= "literal1", seq=m.group(0))

    # An unclosed/invalid character literal.
    return colorer.match_seq(s, i, kind= "literal4", seq= "'")
#@+node:ekr.20250106052237.1: *4* function: rust_string
def rust_string(colorer, s, i):
    # match_span handles escapes.
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")
#@+node:ekr.20250108125839.1: *3* function: rust_colon
def rust_colon(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=':')
#@+node:ekr.20250106042808.9: *3* function: rust_raw_string_literal
# #3631
# https://doc.rust-lang.org/reference/tokens.html#raw-string-literals
# Up to 255 '#' are allowed.

def rust_raw_string_literal(colorer, s, i):

    # Count the '#' characters after the 'r'
    j = 0
    while i + 1 + j < len(s) and s[i + 1 + j] == '#':
        j += 1
    delims = '#' * j
    begin = 'r' + delims + '"'
    end = '"' + delims
    if len(delims) < 256:
        # Return 0 if there is no opening '"'.
        return colorer.match_span(s, i, kind="literal2", begin=begin, end=end)
    return 0

#@+node:ekr.20250106042808.12: *3* function: rust_at_operator
def rust_at_operator(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")
#@+node:ekr.20250106054547.1: *3* function: rust_pound
def rust_pound(colorer, s, i):
    return colorer.match_plain_eol_span(s, i, kind="keyword2")
#@+node:ekr.20250106054731.1: *3* function: rust_open_angle & rust_close_angle
def rust_open_angle(colorer, s, i):
    seq = '<=' if i + 2 < len(s) and s[i + 1] == '=' else '<'
    return colorer.match_plain_seq(s, i, kind="operator", seq=seq)

def rust_close_angle(colorer, s, i):
    seq = '>=' if i + 2 < len(s) and s[i + 1] == '=' else '>'
    return colorer.match_plain_seq(s, i, kind="operator", seq=seq)
#@+node:ekr.20250106042808.14: *3* function: rust_rule6
def rust_rule6(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#")
#@+node:ekr.20250106042808.16: *3* function: rust_rule8
def rust_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")
#@+node:ekr.20250106042808.17: *3* function: rust_rule9
def rust_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")
#@+node:ekr.20250106042808.20: *3* function: rust_rule12
def rust_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")
#@+node:ekr.20250106042808.21: *3* function: rust_rule13
def rust_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")
#@+node:ekr.20250106042808.23: *3* function: rust_rule15
def rust_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")
#@+node:ekr.20250106042808.24: *3* function: rust_rule16
def rust_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")
#@+node:ekr.20250106042808.25: *3* function: rust_rule17
def rust_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")
#@+node:ekr.20250106042808.26: *3* function: rust_rule18
def rust_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")
#@+node:ekr.20250106042808.27: *3* function: rust_rule19
def rust_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")
#@+node:ekr.20250106042808.28: *3* function: rust_rule20
def rust_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")
#@+node:ekr.20250106042808.29: *3* function: rust_rule21
def rust_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")
#@+node:ekr.20250106042808.30: *3* function: rust_rule22
def rust_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")
#@+node:ekr.20250106042808.31: *3* function: rust_rule23
def rust_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")
#@+node:ekr.20250106042808.32: *3* function: rust_rule24
def rust_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")
#@+node:ekr.20250106042808.34: *3* function: rust_rule26
def rust_rule26(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)
#@+node:ekr.20250106042808.35: *3* function: rust_keywords
def rust_keywords(colorer, s, i):
    return colorer.match_keywords(s, i)
#@-others
#@-<< rust: rules >>
#@+<< rust: rules dicts >>
#@+node:ekr.20231103125350.1: ** << rust: rules dicts >>
# Rules dict for rust.
rulesDict1 = {
    # New rules...
    ">": [rust_close_angle],
    "'": [rust_char],
    "<": [rust_open_angle],
    "#": [rust_pound],
    "r": [rust_raw_string_literal, rust_keywords],
    "/": [rust_slash],
    '"': [rust_string],
    ':': [rust_colon],
    # Existing rules...
    "@": [rust_at_operator],
    "=": [rust_rule8],
    "!": [rust_rule9],
    "+": [rust_rule12],
    "-": [rust_rule13],
    "*": [rust_rule15],
    "%": [rust_rule18],
    "&": [rust_rule19],
    "|": [rust_rule20],
    "^": [rust_rule21],
    "~": [rust_rule22],
    "}": [rust_rule23],
    "{": [rust_rule24],
    "(": [rust_rule26],
}

# Add *all* characters that could start a Rust identifier.
lead_ins = string.ascii_letters + '_'
for lead_in in lead_ins:
    aList = rulesDict1.get(lead_in, [])
    if rust_keywords not in aList:
        aList.insert(0, rust_keywords)
        rulesDict1[lead_in] = aList
#@-<< rust: rules dicts >>

# x.rulesDictDict for rust mode.
rulesDictDict = {
    "rust_main": rulesDict1,
    # "rust_rest": rust_rest_rules_dict,
}

# Import dict for rust mode.
importDict = {}
#@-leo
