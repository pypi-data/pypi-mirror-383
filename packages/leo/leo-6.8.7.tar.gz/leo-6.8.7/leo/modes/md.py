#@+leo-ver=5-thin
#@+node:ekr.20241030152835.1: * @file ../modes/md.py
#@@language python
"""
Leo's colorizer control file for md mode.

This file is in the public domain.

Most of this file is an html colorizer.
"""
# pylint: disable=line-too-long

from leo.core import leoGlobals as g

#@+<< md.py: properties >>
#@+node:ekr.20241105214411.1: ** << md.py: properties >>
# Properties for md mode.

properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
    "indentSize": "4",
    "maxLineLen": "120",
    "tabSize": "4",
}
#@-<< md.py: properties >>
#@+<< md.py: attributes dicts >>
#@+node:ekr.20241105214446.1: ** << md.py: attributes dicts >>
# Attributes dict for md_main ruleset.
md_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for md_inline_markup ruleset.
md_inline_markup_attributes_dict = {
    "default": "markup",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for md_block_html_tags ruleset.
md_block_html_tags_attributes_dict = {
    "default": "markup",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for md_markdown ruleset.
md_markdown_attributes_dict = {
    "default": "markup",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for md_link_label_definition ruleset.
md_link_label_definition_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for md_link_inline_url_title ruleset.
md_link_inline_url_title_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for md_link_inline_url_title_close ruleset.
md_link_inline_url_title_close_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for md_link_inline_label_close ruleset.
md_link_inline_label_close_attributes_dict = {
    "default": "LABEL",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for md_markdown_blockquote ruleset.
md_markdown_blockquote_attributes_dict = {
    "default": "LABEL",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}
#@-<< md.py: attributes dicts >>
#@+<< md.py: dictionaries >>
#@+node:ekr.20241105214525.1: ** << md.py: dictionaries >>
# Dictionary of attributes dictionaries for the md ruleset..
attributesDictDict = {
    "md_block_html_tags": md_block_html_tags_attributes_dict,
    "md_inline_markup": md_inline_markup_attributes_dict,
    "md_link_inline_label_close": md_link_inline_label_close_attributes_dict,
    "md_link_inline_url_title": md_link_inline_url_title_attributes_dict,
    "md_link_inline_url_title_close": md_link_inline_url_title_close_attributes_dict,
    "md_link_label_definition": md_link_label_definition_attributes_dict,
    "md_main": md_main_attributes_dict,
    "md_markdown": md_markdown_attributes_dict,
    "md_markdown_blockquote": md_markdown_blockquote_attributes_dict,
}

# Keywords dict for md_main ruleset.
md_main_keywords_dict = {}

# Keywords dict for md_inline_markup ruleset.
md_inline_markup_keywords_dict = {}

# Keywords dict for md_block_html_tags ruleset.
md_block_html_tags_keywords_dict = {}

# Keywords dict for md_markdown ruleset.
md_markdown_keywords_dict = {}

# Keywords dict for md_link_label_definition ruleset.
md_link_label_definition_keywords_dict = {}

# Keywords dict for md_link_inline_url_title ruleset.
md_link_inline_url_title_keywords_dict = {}

# Keywords dict for md_link_inline_url_title_close ruleset.
md_link_inline_url_title_close_keywords_dict = {}

# Keywords dict for md_link_inline_label_close ruleset.
md_link_inline_label_close_keywords_dict = {}

# Keywords dict for md_markdown_blockquote ruleset.
md_markdown_blockquote_keywords_dict = {}

# Dictionary of keywords dictionaries for md mode.
keywordsDictDict = {
    "md_block_html_tags": md_block_html_tags_keywords_dict,
    "md_inline_markup": md_inline_markup_keywords_dict,
    "md_link_inline_label_close": md_link_inline_label_close_keywords_dict,
    "md_link_inline_url_title": md_link_inline_url_title_keywords_dict,
    "md_link_inline_url_title_close": md_link_inline_url_title_close_keywords_dict,
    "md_link_label_definition": md_link_label_definition_keywords_dict,
    "md_main": md_main_keywords_dict,
    "md_markdown": md_markdown_keywords_dict,
    "md_markdown_blockquote": md_markdown_blockquote_keywords_dict,
}
#@-<< md.py: dictionaries >>
#@+<< md.py: md_main: rules & dict >>
#@+node:ekr.20241105214614.1: ** << md.py: md_main: rules & dict >>
# Rules for the md_main ruleset.

# New in Leo 6.8.3: support @language jupytext.
#@+<< md.py: md_jupytext_comment >>
#@+node:ekr.20241106052736.1: *3* << md.py: md_jupytext_comment >>
def md_jupytext_comment(colorer, s, i):
    """
    Switch to python coloring if s is '# %%', provided that c.p.b contains
    @language jupytext.

    New in Leo 6.8.3.
    """
    trace = 'coloring' in g.app.debug and not g.unitTesting

    try:
        c = colorer.c
    except Exception:
        return 0  # Fail, allowing other matches.

    # Leo 6.8.3. Add special case for @language jupytext.
    in_jupytext_tree = any(
        z.startswith('@language jupytext')
        for z_p in c.p.self_and_parents()
        for z in g.splitLines(z_p.b)
    )
    is_any_jupytext_comment = (
        i == 0
        and s.startswith('# %%')
        and in_jupytext_tree
    )
    if is_any_jupytext_comment:
        # Simulate @language md or @language python.
        language = 'md' if s.startswith('# %% [markdown]') else 'python'
        if trace:
            print('')
            g.trace(f"init_mode({language}) {c.p.h}")
        colorer.init_mode(language)
        state_i = colorer.setInitialStateNumber()
        colorer.setState(state_i)

    # Color the line as comment in the current languages.
    n = colorer.match_eol_span(s, i, kind="comment1", seq="#")
    return n  # Succeed. Do not allow other matches.
#@-<< md.py: md_jupytext_comment >>

def md_heading(colorer, s, i):
    # issue 386.
    # print('md_heading',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"^[#]+")

def md_link(colorer, s, i):
    # issue 386.
    # print('md_link',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"\[[^]]+\]\([^)]+\)")

def md_star_emphasis1(colorer, s, i):
    # issue 386.
    # print('md_underscore_emphasis1',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"\*[^\s*][^*]*\*")

def md_star_emphasis2(colorer, s, i):
    # issue 386.
    # print('md_star_emphasis2',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"\*\*[^*]+\*\*")

def md_underscore_emphasis1(colorer, s, i):
    # issue 386.
    # print('md_underscore_emphasis1',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"_[^_]+_")

def md_underline_equals(colorer, s, i):
    # issue 386.
    # print('md_underline_equals',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"^===[=]+$")

def md_underline_minus(colorer, s, i):
    # issue 386.
    # print('md_underline_minus',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"---[-]+$")

def md_underscore_emphasis2(colorer, s, i):
    # issue 386.
    # print('md_underscore_emphasis2',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"__[^_]+__")

def md_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def md_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script", end="</script>",
          at_line_start=True,
          delegate="html::javascript")

def md_rule2(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="<hr\\b([^<>])*?/?>",
          at_line_start=True)

def md_rule3(colorer, s, i):
    return colorer.match_span_regexp(s, i,
        kind="markup",
        begin="<(p|div|h[1-6]|blockquote|pre|table|dl|ol|ul|noscript|form|fieldset|iframe|math|ins|del)\\b", end="</$1>",
          at_line_start=True,
          delegate="md::block_html_tags")

def md_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=" < ")

def md_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="md::inline_markup")

# Rules dict for md_main ruleset.
rulesDict1 = {
    "#": [md_jupytext_comment, md_heading],  # Order important. #4146 and #386
    "[": [md_link],  # # #386.
    "*": [md_star_emphasis2, md_star_emphasis1],  # #386. Order important
    "=": [md_underline_equals],  # # #386.
    "-": [md_underline_minus],  # # #386.
    "_": [md_underscore_emphasis2, md_underscore_emphasis1],  # #386. Order important.
    " ": [md_rule4],
    "<": [md_rule0, md_rule1, md_rule2, md_rule3, md_rule5],
}
#@-<< md.py: md_main: rules & dict >>
#@+<< md.py: md_inline_markup: rules & dict >>
#@+node:ekr.20241105214946.1: ** << md.py: md_inline_markup: rules & dict >>
rulesDict2 = {}
#@-<< md.py: md_inline_markup: rules & dict >>
#@+<< md.py: md_block_html_tags: rules & dict >>
#@+node:ekr.20241105215036.1: ** << md.py: md_block_html_tags: rules & dict >>
# Rules for md_block_html_tags ruleset.

if 0:  # Rules 6 & 7 will never match?

    def md_rule6(colorer, s, i):
        return colorer.match_eol_span_regexp(s, i, kind="invalid", regexp="[\\S]+",
          at_line_start=True)

    def md_rule7(colorer, s, i):
        return colorer.match_eol_span_regexp(s, i, kind="invalid", regexp="{1,3}[\\S]+",
          at_line_start=True)

def md_rule8(colorer, s, i):
    # leadin: [ \t]
    return colorer.match_eol_span_regexp(s, i, kind="", regexp="( {4}|\\t)",
          at_line_start=True,
          delegate="html::main")

def md_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def md_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def md_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

# Rules dict for md_block_html_tags ruleset.
rulesDict3 = {
    " ": [md_rule8],  # new
    "\t": [md_rule8],  # new
    "\"": [md_rule9],
    "'": [md_rule10],
    # "(": [md_rule8],
    "=": [md_rule11],
    # "[": [md_rule6], # Will never fire: the leadin character is any non-space!
    # "{": [md_rule7], # Will never fire: the leading character is any non-space!
}
#@-<< md.py: md_block_html_tags: rules & dict >>
#@+<< md.py: md_markdown: rules & dict >>
#@+node:ekr.20241105215135.1: ** << md.py: md_markdown: rules & dict >>
# Rules for md_markdown ruleset.

def md_rule12(colorer, s, i):
    # Leadins: [ \t>]
    return colorer.match_eol_span_regexp(s, i, kind="", regexp="[ \\t]*(>[ \\t]{1})+",
          at_line_start=True,
          delegate="md::markdown_blockquote")

def md_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="*")

def md_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="_")

def md_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="\\][")

# Invalid regex.

    def md_rule16(colorer, s, i):
        return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]")

def md_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="``` ruby", end="```",
          at_line_start=True,
          delegate="ruby::main")

def md_rule18(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="```", end="```",
          at_line_start=True)

def md_rule19(colorer, s, i):
    # leadin: `
    return colorer.match_span_regexp(s, i, kind="literal2", begin="(`{1,2})", end="$1")

def md_rule20(colorer, s, i):
    # Leadins are [ \t]
    return colorer.match_eol_span_regexp(s, i, kind="literal2", regexp="( {4,}|\\t+)\\S",
          at_line_start=True)

def md_rule21(colorer, s, i):
    # Leadins are [=-]
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[=-]+",
          at_line_start=True)

def md_rule22(colorer, s, i):
    # Leadin is #
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="#{1,6}[ \\t]*(.+?)",
          at_line_start=True)

def md_rule23(colorer, s, i):
    # Leadins are [ \t -_*]
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[ ]{0,2}([ ]?[-_*][ ]?){3,}[ \\t]*",
          at_line_start=True)

def md_rule24(colorer, s, i):
    # Leadins are [ \t*+-]
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}[*+-][ \\t]+",
          at_line_start=True)

def md_rule25(colorer, s, i):
    # Leadins are [ \t0123456789]
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}\\d+\\.[ \\t]+",
          at_line_start=True)

def md_rule26(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="\\[(.*?)\\]\\:",
          at_whitespace_end=True,
          delegate="md::link_label_definition")

# Invalid regex.

    def md_rule27(colorer, s, i):
        # leadin: [
        return colorer.match_span_regexp(s, i, kind="keyword4", begin="!?\\[[\\p{Alnum}\\p{Blank}]*", end="\\]",
              delegate="md::link_inline_url_title",
              no_line_break=True)

def md_rule28(colorer, s, i):
    # Leadins: [*_]
    return colorer.match_span_regexp(s, i, kind="literal3", begin="(\\*\\*|__)", end="$1",
          no_line_break=True)

def md_rule29(colorer, s, i):
    # Leadins: [*_]
    return colorer.match_span_regexp(s, i, kind="literal4", begin="(\\*|_)", end="$1",
          no_line_break=True)

# Rules dict for md_markdown ruleset.
rulesDict4 = {
# Existing leadins...
    # "!": [md_rule27],
    "#": [md_rule22],
    "*": [md_rule13, md_rule23, md_rule24, md_rule28, md_rule29],  # new: 23,24,28,29.
    "\\": [
        md_rule15,
        # md_rule16,
        md_rule26,
    ],
    "_": [md_rule14, md_rule23, md_rule24, md_rule28, md_rule29],  # new: 23,24,28,29.
    "`": [md_rule17, md_rule18, md_rule19],  # new: 19
    # "[": [md_rule27],  # new: 27 old: 12,21,23,24,25.
# Unused leadins...
    # "(": [md_rule28,md_rule29],
# New leadins...
    " ": [md_rule12, md_rule20, md_rule23, md_rule24, md_rule25],
    "\t": [md_rule12, md_rule20, md_rule23, md_rule24, md_rule25],
    ">": [md_rule12],
    "=": [md_rule21],
    "-": [md_rule21, md_rule23, md_rule24],
    "0": [md_rule25],
    "1": [md_rule25],
    "2": [md_rule25],
    "3": [md_rule25],
    "4": [md_rule25],
    "5": [md_rule25],
    "6": [md_rule25],
    "7": [md_rule25],
    "8": [md_rule25],
    "9": [md_rule25],
}
#@-<< md.py: md_markdown: rules & dict >>
#@+<< md.py: md_link_label_definition: rules & dict >>
#@+node:ekr.20241105215258.1: ** << md.py: md_link_label_definition: rules & dict >>
# Rules for md_link_label_definition ruleset.

if 0:  # Invalid regex.

    def md_rule30(colorer, s, i):
        return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]")

def md_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\"")

def md_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def md_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

# Rules dict for md_link_label_definition ruleset.
rulesDict5 = {
    "\"": [md_rule31],
    "(": [md_rule32],
    ")": [md_rule33],
    # "\\": [md_rule30],
}
#@-<< md.py: md_link_label_definition: rules & dict >>
#@+<< md.py: md_link_inline_url_title: rules & dict >>
#@+node:ekr.20241105215340.1: ** << md.py: md_link_inline_url_title: rules & dict >>
# Rules for md_link_inline_url_title ruleset.

def md_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def md_rule35(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="\\[", end="\\]",
          delegate="md::link_inline_label_close",
          no_line_break=True)

def md_rule36(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="\\(", end="\\)",
          delegate="md::link_inline_url_title_close",
          no_line_break=True)

# Rules dict for md_link_inline_url_title ruleset.
rulesDict6 = {
    "(": [md_rule36],
    "[": [md_rule35],
    "]": [md_rule34],
}
#@-<< md.py: md_link_inline_url_title: rules & dict >>
#@+<< md.py: md_link_inline_url_title_close: rules & dict >>
#@+node:ekr.20241105215437.1: ** << md.py: md_link_inline_url_title_close: rules & dict >>
# Rules for md_link_inline_url_title_close ruleset.

def md_rule37(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="null", seq=")",
          delegate="md::main")

# Rules dict for md_link_inline_url_title_close ruleset.
rulesDict7 = {
    ")": [md_rule37],
}
#@-<< md.py: md_link_inline_url_title_close: rules & dict >>
#@+<< md.py: md_link_inline_label_close: rules & dict >>
#@+node:ekr.20241105215506.1: ** << md.py: md_link_inline_label_close: rules & dict >>
# Rules for md_link_inline_label_close ruleset.

def md_rule38(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="null", seq="]",
          delegate="md::main")

# Rules dict for md_link_inline_label_close ruleset.
rulesDict8 = {
    "]": [md_rule38],
}
#@-<< md.py: md_link_inline_label_close: rules & dict >>
#@+<< md.py: md_markdown_blockquote: rules & dict >>
#@+node:ekr.20241105215622.1: ** << md.py: md_markdown_blockquote: rules & dict >>
# Rules for md_markdown_blockquote ruleset.

def md_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=" < ")

def md_rule40(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="md::inline_markup")

def md_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="*")

def md_rule42(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="_")

def md_rule43(colorer, s, i):
    # leadin: backslash.
    return colorer.match_plain_seq(s, i, kind="null", seq="\\][")

if 0:  # Invalid regex.

    def md_rule44(colorer, s, i):
        # leadin: backslash.
        return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]")

def md_rule45(colorer, s, i):
    # leadin: `
    return colorer.match_span_regexp(s, i, kind="literal2", begin="(`{1,2})", end="$1")

def md_rule46(colorer, s, i):
    # leadins: [ \t]
    return colorer.match_eol_span_regexp(s, i, kind="literal2", regexp="( {4,}|\\t+)\\S")

def md_rule47(colorer, s, i):
    # leadins: [=-]
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[=-]+")

def md_rule48(colorer, s, i):
    # leadin: #
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="#{1,6}[ \\t]*(.+?)")

def md_rule49(colorer, s, i):
    # leadins: [ -_*]
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[ ]{0,2}([ ]?[-_*][ ]?){3,}[ \\t]*")

def md_rule50(colorer, s, i):
    # leadins: [ \t*+-]
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}[*+-][ \\t]+")

def md_rule51(colorer, s, i):
    # leadins: [ \t0123456789]
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}\\d+\\.[ \\t]+")

def md_rule52(colorer, s, i):
    # leadin: [
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="\\[(.*?)\\]\\:",
          delegate="md::link_label_definition")

if 0:  # invalid regex.

    def md_rule53(colorer, s, i):
        # leadin: [
        return colorer.match_span_regexp(s, i, kind="keyword4", begin="!?\\[[\\p{Alnum}\\p{Blank}]*", end="\\]",
              delegate="md::link_inline_url_title",
              no_line_break=True)

def md_rule54(colorer, s, i):
    # leadins: [*_]
    return colorer.match_span_regexp(s, i, kind="literal3", begin="(\\*\\*|__)", end="$1")

def md_rule55(colorer, s, i):
     # leadins: [*_]
    return colorer.match_span_regexp(s, i, kind="literal4", begin="(\\*|_)", end="$1")

# Rules dict for md_markdown_blockquote ruleset.
rulesDict9 = {
# old, unused.
# "!": [], # 53
# "[": [], # 47,49,50,51,
    " ": [md_rule39, md_rule46, md_rule49, md_rule50],  # new: 46,49,50
    "\t": [md_rule46, md_rule50],  # new: 46,50
    "#": [md_rule48],
    "(": [md_rule54, md_rule55],  # 45,46
    "*": [md_rule41, md_rule49, md_rule50, md_rule54, md_rule55],  # new: 49,50,54,55
    "<": [md_rule40],
    "\\": [
        md_rule43,
        # md_rule44,
    ],  # 52,53
    "_": [md_rule42, md_rule49, md_rule54, md_rule55],  # new: 49,54,55
# new leadins:
    "+": [md_rule50],
    "-": [md_rule47, md_rule49, md_rule50],
    "=": [md_rule47],
    "[": [
            md_rule52,
            # md_rule53,
        ],
    "`": [md_rule45],
    "0": [md_rule50],
    "1": [md_rule50],
    "2": [md_rule50],
    "3": [md_rule50],
    "4": [md_rule50],
    "5": [md_rule50],
    "6": [md_rule50],
    "7": [md_rule50],
    "8": [md_rule50],
    "9": [md_rule50],
}
#@-<< md.py: md_markdown_blockquote: rules & dict >>
#@+<< md.py: interface dicts >>
#@+node:ekr.20241105221310.1: ** << md.py: interface dicts >>
# x.rulesDictDict for md mode.
rulesDictDict = {
    "md_block_html_tags": rulesDict3,
    "md_inline_markup": rulesDict2,
    "md_link_inline_label_close": rulesDict8,
    "md_link_inline_url_title": rulesDict6,
    "md_link_inline_url_title_close": rulesDict7,
    "md_link_label_definition": rulesDict5,
    "md_main": rulesDict1,
    "md_markdown": rulesDict4,
    "md_markdown_blockquote": rulesDict9,
}

# Import dict for md mode.
importDict = {
    "md_inline_markup": ["html::tags"],
    "md_link_label_definition": ["md_link_label_definition::markdown"],
    "md_main": ["md_main::markdown"],
}
#@-<< md.py: interface dicts >>
#@-leo
