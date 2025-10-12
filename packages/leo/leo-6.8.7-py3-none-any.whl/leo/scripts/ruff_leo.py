#@+leo-ver=5-thin
#@+node:ekr.20240406061929.1: * @file ../scripts/ruff_leo.py
"""
run_ruff_leo.py: Run ruff on the leo-editor/leo folder.

leo-editor/ruff.toml contains configuration settings.

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867

EKR's ruff-leo.cmd:
    @echo off
    cd {path-to-leo-editor}
    echo python -m ruff check leo
    python -m ruff check leo
"""

import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)

args = ' '.join(sys.argv[1:])
isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

command = fr'{python} -m ruff check leo'
subprocess.Popen(command, shell=True).communicate()
#@-leo
