#@+leo-ver=5-thin
#@+node:ekr.20131016083406.16724: * @button make-sphinx
"""
Run this script from the `gh-pages` branch.

1. Generate intermediate files for all headlines in the table.
2. Run `make html` from the leo/doc/html directory.

After running this script, copy files
- from leo/doc/html/_build/html to leo-editor/docs
- from leo/doc/html/_build/html/_static to leo/editor-docs/_static
"""


g.cls()
g.cls()

from datetime import datetime
import glob
import os
import re
import shutil
from sphinx import __version__ as sphinx_version

trace = False
headlines = [
    "Leo's Documentation"
]

join = os.path.join
norm = os.path.normpath

def finalize(s):
    return g.os_path_finalize(norm(s))

#@+others  # define helpers
#@+node:ekr.20241124122954.1: ** copy_all_files
def copy_all_files(from_directory: str, to_directory: str) -> None:
    """Copy *all* html files from `from_directory` to `to_directory`."""
    trace = False
    if not os.path.exists(to_directory):
        print(f"Directory not found: {to_directory!r}")
        return
    files = glob.glob(f"{from_directory}{os.sep}*")
    files = [z for z in files if os.path.isfile(z)]
    # Announce.
    written = 0
    for f in files:
        try:
            fn = finalize(f)
            shutil.copy2(fn, to_directory)
            written += 1
        except Exception:
            print(f"Not Copied {fn}")
    print(f"Copied {written} files from {from_directory:55} to {to_directory}")
#@+node:ekr.20241127053544.1: ** get_leo_version
conf_version_pat = re.compile(r"version\s*= '([0-9]+\.[0-9]+\.[0-9]+)'")

def get_leo_version():
    """Return the version in conf.py"""    
    h = '@edit html/conf.py'
    p = g.findNodeAnywhere(c, h)
    assert p, h
    for m in conf_version_pat.finditer(p.b):
        version = m.group(1)
        if version:
            return version
    assert False, 'no version in conf.py'
#@+node:ekr.20230303080626.1: ** git_status
def git_status():
    """Report git status"""
    leo_path = finalize(join(g.app.loadDir, '..', '..'))
    os.chdir(leo_path)
    g.execute_shell_commands([
        'git status',
    ])

#@+node:ekr.20230303064734.1: ** make_html
def make_html(html_path):
    """
    Run the `make html` command in the leo/doc/html directory.
    """
    cwd = finalize(os.getcwd())
    assert cwd.lower() == html_path.lower(), (cwd, html_path)
    
    if 0:  # `make clean` is good for testing.
        g.execute_shell_commands(['make clean'])
        
    if 1:  # Simplest, safest.
        g.execute_shell_commands(['make html'])
    elif 0:  # Works. Arguments are from the MakeFile.
        g.execute_shell_commands([
            'python -m sphinx -b html -d _build/doctrees . _build/html',
        ])
    else:  # Fastest, but depends on sphinx's API.
        from sphinx.cmd import build
        args = '-b html -d _build/doctrees . _build/html'
        argv = args.split(' ')
        build.build_main(argv)
#@+node:ekr.20241125122939.1: ** patch_home_page
date_pat = re.compile(r'^(.*?)(Last updated on\s*)(.+)(.*)$')
leo_version_pat = re.compile(r'^(.*?)Leo\s*([0-9]+\.[0-9]+\.[0-9]+)(.*)$')
sphinx_version_pat = re.compile(r'^(.*?)Sphinx\s*([0-9]+\.[0-9]+\.[0-9]+)(.*)$')

def patch_home_page():
    """
    Update (in *this*file) the "Last updated" and "Created using" fields in
    the node `@file ../../docs/index.html` or its descendants.
    """
    today = datetime.today()
    date = datetime.date(today).strftime("%B %d, %Y")  # Same as conf.py.
    leo_version = get_leo_version()

    def date_repl(m: re.Match) -> str:
        s = m.group(0)
        i, j = m.start(3), m.end(3)
        return s[:i] + date + s[j:]
    
    def leo_version_repl(m: re.Match) -> str:
        s = m.group(0)
        i, j = m.start(2), m.end(2)
        return s[:i] + leo_version + s[j:]

    def sphinx_version_repl(m: re.Match) -> str:
        s = m.group(0)
        i, j = m.start(2), m.end(2)
        return s[:i] + sphinx_version + s[j:]

    table = (
        (date_pat, date_repl),
        (leo_version_pat, leo_version_repl),
        (sphinx_version_pat, sphinx_version_repl),
    )
    h = '@file ../../docs/index.html'
    home_page = g.findNodeAnywhere(c, h)
    if not home_page:
        g.trace(f"Not found: {h!r}")
        return
    any_changed = False
    for p in home_page.self_and_subtree():
        old_lines = g.splitLines(p.b)
        new_lines = old_lines[:]
        for i, old_line in enumerate(old_lines):
            new_line = old_line
            for pattern, repl in table:
                new_line = re.sub(pattern, repl, new_line)
                if new_line != old_lines[i]:
                    print('')
                    print(f"Changed line {i:<2} of {p.h}")
                    print(new_line.rstrip())
                    new_lines[i] = old_lines[i] = new_line
                    changed = True
        if new_lines != g.splitLines(p.b):
            p.b = ''.join(new_lines)
            print('')
            c.setChanged()
            home_page.setDirty()
            any_changed = True
#@+node:ekr.20230228105847.1: ** run
#@@language python

def run():
    """
    Make all html files using sphinx and copy the results to leo-editor/docs.
    """
    # Step 1. Compute all paths.

    # Base paths. Not finalized.
    docs = join(g.app.loadDir, '..', '..', 'docs')
    doc = join(g.app.loadDir, '..', 'doc')
    
    # We will cd to the html path.
    html_path = finalize(join(doc, 'html'))

    # We will copy all files from build_path to docs_path.
    build_path = finalize(join(doc, 'html', '_build', 'html'))
    docs_path = finalize(docs)
    
    # We will copy the static folder from doc/html/_build/html/_static to docs.
    # We *must* use the _build-related path to update sphinx .css files.
    docs_static_path = finalize(join(docs, '_static'))
    doc_static_path = finalize(join(doc, 'html', '_build', 'html', '_static' ))
    
    # Step 2: Make sure all paths exist.
    paths = (build_path, docs_path, docs_static_path, html_path)
    fails = [z for z in paths if not g.os_path_exists(z)]
    if fails:
        g.printObj(fails, tag='run: Missing paths...')
        return
        
    # Step 3: Do nothing else outside 'gh-pages' branch.
    if not g.gitBranchName().startswith('gh-pages'):
        g.es_print('Run `make-sphinx` from `gh-pages` branch')
        return
    try:
        old_p = c.p
        os.chdir(html_path)
        patch_home_page()
        write_intermediate_files()
        make_html(html_path)
        print('')
        copy_all_files(build_path, docs_path)
        copy_all_files(doc_static_path, docs_static_path)
        print('')
        git_status()
    finally:
        c.selectPosition(old_p)
#@+node:ekr.20230111165336.1: ** write_intermediate_files
def write_intermediate_files() -> int:
    """Return True if the rst3 command wrote any intermediate files."""
    total_n = 0
    for headline in headlines:
        p = g.findTopLevelNode(c, headline)
        if p:
            c.selectPosition(p)
            n = c.rstCommands.rst3()
            total_n += n
        else:
            g.es_print(f"Not found: {headline!r}")
            return False
    if total_n == 0:
        g.es_print('No intermediate files changed', color='red')
    return total_n > 0
#@-others

if c.isChanged():  # Save this file initially.
    c.save()
run()
if c.isChanged():  # Save this file again if we have patched the home page.
    c.save()
#@-leo

