# remote_fs.py
from __future__ import annotations
from typing import*
import subprocess, shlex, os , glob, posixpath, re
# Accept strings like:
#   "/local/abs/dir"
#   "relative/local/dir"
#   "user@host:/abs/dir"
REMOTE_RE = re.compile(r"^(?P<host>[^:\s]+@[^:\s]+):(?P<path>/.*)$")
AllowedPredicate = Optional[Callable[[str], bool]]

