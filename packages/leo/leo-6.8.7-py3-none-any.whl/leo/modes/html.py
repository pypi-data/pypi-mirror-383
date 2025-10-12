#@+leo-ver=5-thin
#@+node:ekr.20230419050031.1: * @file ../modes/html.py
"""
leo/modes/html.py: Leo's mode file for @language html.
"""
#@+<< html.py: imports >>
#@+node:ekr.20241120013234.1: ** << html.py: imports >>
from __future__ import annotations
import re
from typing import Any
from leo.core import leoGlobals as g
assert g
#@-<< html.py: imports >>
#@+others  # Rules
#@+node:ekr.20230419051223.1: ** main ruleset
#@+others
#@+node:ekr.20230419050050.1: *3* html_rule_comment <!--..-->
def html_rule_comment(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

#@+node:ekr.20230419050050.2: *3* html_rule_script <script..</script>
def html_rule_script(colorer: Any, s: str, i: int) -> int:

    if i != 0 or not s.startswith("<script"):
        return 0  # Fail, but allow other matches.

    # Colorize the element as an html element...
    colorer.match_span(s, i, kind="markup", begin="<script", end=">")

    # Start javascript mode.
    colorer.push_delegate('javascript')
    return len(s)  # Success.



#@+node:ekr.20230419050050.4: *3* html_rule_style <style..</style>
def html_rule_style(colorer, s, i):

    if i != 0 or not s.startswith("<style"):
        return 0  # Fail, but allow other matches.

    # Colorize the element as an html element..
    colorer.match_span(s, i, kind="markup", begin="<style", end=">")

    # Start css mode.
    colorer.push_delegate('css')
    return len(s)  # Success.
#@+node:ekr.20230419050050.6: *3* html_rule3 <!..>
def html_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">")

#@+node:ekr.20230419050050.7: *3* html_rule4 <..>
tag_pat = re.compile(r"</?[\w]+")  # Match both opening and closing tags

def html_rule4(colorer, s, i):

    # Find the opening or closing tag.
    for m in tag_pat.finditer(s, i):  # Don't create substrings.
        if m.group(0) and m.start() == i:
            tag = m.group(0)
            return colorer.match_span(s, i,
                kind="markup", begin=tag, end=">", delegate="html::tags")

    # An error.
    return colorer.match_span(s, i, kind="comment", begin="<", end=">")
#@+node:ekr.20230419050050.8: *3* html_rule5 &..;
def html_rule5(colorer, s, i):
    c = colorer.c
    if c.p.b.startswith(('@language katex', '@language latex', '@language mathjax')):
        # This rule interferes with LaTeX coloring.
        return 0
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
        no_word_break=True)
#@+node:ekr.20230419050050.9: *3* html_rule_handlebar {{..}}
# New rule for handlebar markup, colored with the literal3 color.
def html_rule_handlebar(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="{{", end="}}")
#@+node:ekr.20241121083510.1: *3* html_rule_at_language @language
def html_rule_at_language(colorer, s, i):

    if i == 0 and s.startswith("@language "):
        return colorer.match_at_language(s, i)
    return 0  # Fail, but allow other matches.
#@+node:ekr.20241120172252.1: *3* html_rule_end_template </template>
def html_rule_end_template(colorer, s, i):

    if i != 0 or not s.startswith("</template>"):
        return 0  # Fail, but allow other matches.

    # Colorize the element as an html element.
    colorer.match_seq(s, i, kind="markup", seq="</template>")

    # Restart any previous delegate.
    colorer.pop_delegate()
    return len(s)  # Success.
#@+node:ekr.20241227074125.1: *3* html_rule_percent
def html_rule_percent(colorer, s, i):
    # A hack for @language latex/mathjax.
    c = colorer.c
    if c.p.b.startswith(('@language katex', '@language latex', '@language mathjax')):
        if i == 0 and s and s[i] == '%':
            # Color '%' as a whole-line comment.
            colorer.match_eol_span(s, i, kind="comment1", seq="%")
            return len(s)
    return 0

#@-others

#@+node:ekr.20230419050351.1: ** html_tags ruleset
# Rules for html_tags ruleset.

def html_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def html_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def html_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")
#@-others
#@+<< html.py: dictionaries >>
#@+node:ekr.20241120012038.1: ** << html.py: dictionaries >>
#@+others
#@+node:ekr.20241120012226.1: *3* html.py: Properties dict
# Properties for html mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}
#@+node:ekr.20230419050200.1: *3* html.py: Attributes dicts
# Attributes dict for html_main ruleset.
html_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for html_tags ruleset.
html_tags_attributes_dict = {
    "default": "markup",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for html_javascript ruleset.
html_javascript_attributes_dict = {
    "default": "markup",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for html_back_to_html ruleset.
html_back_to_html_attributes_dict = {
    "default": "markup",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for html_css ruleset.
html_css_attributes_dict = {
    "default": "markup",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for html mode.
attributesDictDict = {
    "html_back_to_html": html_back_to_html_attributes_dict,
    "html_css": html_css_attributes_dict,
    "html_javascript": html_javascript_attributes_dict,
    "html_main": html_main_attributes_dict,
    "html_tags": html_tags_attributes_dict,
}
#@+node:ekr.20230419050229.1: *3* html.py: Keywords dicts
# Keywords dict for html_main ruleset.
html_main_keywords_dict = {}

# Keywords dict for html_tags ruleset.
html_tags_keywords_dict = {}

# Keywords dict for html_javascript ruleset.
html_javascript_keywords_dict = {}

# Keywords dict for html_back_to_html ruleset.
html_back_to_html_keywords_dict = {}

# Keywords dict for html_css ruleset.
html_css_keywords_dict = {}

# Dictionary of keywords dictionaries for html mode.
keywordsDictDict = {
    "html_back_to_html": html_back_to_html_keywords_dict,
    "html_css": html_css_keywords_dict,
    "html_javascript": html_javascript_keywords_dict,
    "html_main": html_main_keywords_dict,
    "html_tags": html_tags_keywords_dict,
}
#@+node:ekr.20241120012542.1: *3* html.py: Rules dicts
# Rules dict for html_main ruleset.
rulesDict1 = {
    "%": [html_rule_percent],
    "&": [html_rule5],
    "@": [html_rule_at_language],
    "<": [
        html_rule_script,
        html_rule_style,
        html_rule_end_template,
        html_rule_comment,
        # After all the above rules.
        html_rule3,
        html_rule4,
    ],
    "{": [html_rule_handlebar],
}

# Rules dict for html_tags ruleset.
rulesDict2 = {
    "\"": [html_rule6],
    "'": [html_rule7],
    "=": [html_rule8],
}
#@-others

# Import dict for html mode.
importDict = {}

# x.rulesDictDict for html mode.
rulesDictDict = {
    "html_main": rulesDict1,
    "html_tags": rulesDict2,  # Used by md.py and pandoc.py.
}
#@-<< html.py: dictionaries >>

#@@language python
#@@tabwidth -4
#@-leo
