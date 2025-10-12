#@+leo-ver=5-thin
#@+node:ekr.20250109073005.1: * @file ../modes/rest.py
#@@language python
# Leo colorizer control file for rest mode.
# This file is in the public domain.

import string
from leo.core import leoGlobals as g
assert g

#@+<< rest: properties and attributes >>
#@+node:ekr.20250109073208.1: ** << rest: properties and attributes >>

# Properties for rest mode.
properties = {
    "indentNextLines": ".+::$",
    "lineComment": "..",
}

# Attributes dict for rest_main ruleset.
rest_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for rest mode.
attributesDictDict = {
    "rest_main": rest_main_attributes_dict,
}
#@-<< rest: properties and attributes >>
#@+<< rest: keywords >>
#@+node:ekr.20250109073231.1: ** << rest: keywords >> (empty)

# Keywords dict for rest_main ruleset.
rest_main_keywords_dict = {}

# Dictionary of keywords dictionaries for rest mode.
keywordsDictDict = {
    "rest_main": rest_main_keywords_dict,
}
#@-<< rest: keywords >>
#@+<< rest: rules >>
#@+node:ekr.20250109073256.1: ** << rest: rules >>
# Rules for rest_main ruleset.

#@+others
#@+node:ekr.20250110185142.1: *3* rest underline rules
#@+node:ekr.20250109073551.3: *4* function: rest_rule2
def rest_rule2(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="={3,}")
#@+node:ekr.20250109073551.4: *4* function: rest_rule3
def rest_rule3(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="-{3,}")
#@+node:ekr.20250109073551.5: *4* function: rest_rule4
def rest_rule4(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="~{3,}")
#@+node:ekr.20250109073551.6: *4* function: rest_rule5
def rest_rule5(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="`{3,}")
#@+node:ekr.20250109073551.7: *4* function: rest_rule6
def rest_rule6(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="#{3,}")
#@+node:ekr.20250109073551.8: *4* function: rest_rule7
def rest_rule7(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp='"{3,}')
#@+node:ekr.20250109073551.9: *4* function: rest_rule8
def rest_rule8(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\^{3,}")
#@+node:ekr.20250109073551.10: *4* function: rest_rule9
def rest_rule9(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\+{3,}")
#@+node:ekr.20250111042122.1: *3* function: rest_plain_word (literal1)
def rest_plain_word(colorer, s, i):

    j = i
    while j < len(s) and s[j] in string.ascii_letters:
        j += 1
    return colorer.match_seq(s, i, kind='literal1', seq=s[i : j + 1])
#@+node:ekr.20250110190212.1: *3* function: rest_number (literal2)
def rest_number(colorer, s, i):

    j = i
    while j < len(s) and s[j] in string.digits:
        j += 1
    return colorer.match_seq(s, i, kind='literal2', seq=s[i : j + 1])
#@+node:ekr.20250111053429.1: *3* function: rest_default (operator)
def rest_default(colorer, s, i):
    ch = s[i]
    if ch in ' \t':
        return 1
    return colorer.match_seq(s, i, kind='operator', seq=s[i])
#@+node:ekr.20250109074353.1: *3* function: rest_star (comment1, label, literal3, literal4)
def rest_star(colorer, s, i):

    # Count the number of stars in s[i:].
    j = 0
    while i + j < len(s) and s[i + j] == '*':
        j += 1
    seq = '*' * j

    # Case 1: ***
    if j >= 3:
        return colorer.match_seq(s, i, kind="label", seq=seq)

    # Case 2: no matching '*'
    k = s.find(seq, i + j)
    if k == -1:
        return colorer.match_seq(s, i, kind="comment1", seq='*')

    # Case 3: * or **
    # Use keyword2 for italics, keyword3 for bold.
    kind = 'literal3' if len(seq) == 1 else 'literal4'
    return colorer.match_seq(s, i, kind=kind, seq=s[i : k + j])

    # Rule 10.
    # return colorer.match_seq_regexp(s, i, kind="label", regexp="\\*{3,}")
    # Rule 14.
    # return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="\\*\\*[^*]+\\*\\*")
    # Rule 15.
    # return colorer.match_seq_regexp(s, i, kind="keyword4", regexp="\\*[^\\s*][^*]*\\*")
#@+node:ekr.20250109073551.1: *3* function: rest_rule0 __
def rest_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword3", seq="__",
          at_line_start=True)
#@+node:ekr.20250109073551.2: *3* function: rest_rule1 .. _
def rest_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword3", seq=".. _",
          at_line_start=True)
#@+node:ekr.20250109073551.12: *3* function: rest_rule11 .. |...|
def rest_rule11(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp=r"\.\.\s\|[^|]+\|",
          at_line_start=True)
#@+node:ekr.20250109073551.13: *3* function: rest_rule12 |...|
def rest_rule12(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal4", regexp=r"\|[^|]+\|")
#@+node:ekr.20250109073551.14: *3* function: rest_rule13 .. word::
def rest_rule13(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp=r"\.\.\s[A-z][A-z0-9-_]+::",
          at_line_start=True)
#@+node:ekr.20250109073551.17: *3* function: rest_rule16 ..
def rest_rule16(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="..",
          at_line_start=True)
#@+node:ekr.20250109073551.18: *3* function: rest_rule17 `word`_
def rest_rule17(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="`[A-z0-9]+[^`]+`_{1,2}")
#@+node:ekr.20250109073551.19: *3* function: rest_rule18 [number]_
def rest_rule18(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\[[0-9]+\]_")
#@+node:ekr.20250109073551.20: *3* function: rest_rule19 [#word]_
def rest_rule19(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\[#[A-z0-9_]*\]_")
#@+node:ekr.20250109073551.21: *3* function: rest_rule20 []_
def rest_rule20(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\[*\]_")
#@+node:ekr.20250109073551.22: *3* function: rest_rule21 [word]_
def rest_rule21(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\[[A-z][A-z0-9_-]*\]_")
#@+node:ekr.20250109073551.23: *3* function: rest_rule22 ``...``
def rest_rule22(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="``", end="``")
#@+node:ekr.20250109073551.24: *3* function: rest_rule23 `...`
def rest_rule23(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword1", regexp="`[^`]+`")
#@+node:ekr.20250109073551.25: *3* function: rest_rule24 :word=:
def rest_rule24(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword1", regexp=r":[A-z][A-z0-9 \t=\s\t_]*:")
#@+node:ekr.20250109073551.26: *3* function: rest_rule25 +-
def rest_rule25(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\+-[+-]+")
#@+node:ekr.20250109073551.27: *3* function: rest_rule26 +=
def rest_rule26(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\+=[+=]+")
#@-others
#@-<< rest: rules >>
#@+<< rest: rulesDict1 >>
#@+node:ekr.20250109073509.1: ** << rest: rulesDict1 >>
# Rules dict for rest_main ruleset.
rulesDict1 = {
    "\"": [rest_rule7],
    "#": [rest_rule6],
    "*": [rest_star],
    "+": [rest_rule9, rest_rule25, rest_rule26],
    "-": [rest_rule3],
    ".": [rest_rule1, rest_rule11, rest_rule13, rest_rule16],
    ":": [rest_rule24],
    "=": [rest_rule2],
    "[": [rest_rule18, rest_rule19, rest_rule20, rest_rule21],
    "^": [rest_rule8],
    "_": [rest_rule0],
    "`": [rest_rule5, rest_rule17, rest_rule22, rest_rule23],
    "|": [rest_rule12],
    "~": [rest_rule4],
}

# Color words and numbers explicitly, allowing them to have non-default colors.

lead_in_table = (
    (string.ascii_letters, rest_plain_word),
    (string.digits, rest_number),
)
for lead_ins, matcher in lead_in_table:
    for lead_in in lead_ins:
        aList = rulesDict1.get(lead_in, [])
        if matcher not in aList:
            aList.insert(0, matcher)
            rulesDict1[lead_in] = aList

# Color everything as literal1 by default.
for lead_in in string.printable:
    aList = rulesDict1.get(lead_in, [])
    aList.append(rest_default)
    rulesDict1[lead_in] = aList

#@-<< rest: rulesDict1 >>

# x.rulesDictDict for rest mode.
rulesDictDict = {
    "rest_main": rulesDict1,
}

# Import dict for rest mode.
importDict = {}
#@-leo
