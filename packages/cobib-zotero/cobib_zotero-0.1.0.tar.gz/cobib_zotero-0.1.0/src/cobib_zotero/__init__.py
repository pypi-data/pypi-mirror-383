"""cobib-zotero - an importer plugin for coBib.

.. include:: ../../README.md
   :start-after: # coBib Zotero
"""

import subprocess
from pathlib import Path

__version__ = "0.1.0"

if (Path(__file__).parent.parent.parent / ".git").exists():  # pragma: no branch
    # if installed from source, append HEAD commit SHA to version info as metadata
    with subprocess.Popen(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE) as proc:
        git_revision, _ = proc.communicate()
    __version__ += "+" + git_revision.decode("utf-8")[:7]
