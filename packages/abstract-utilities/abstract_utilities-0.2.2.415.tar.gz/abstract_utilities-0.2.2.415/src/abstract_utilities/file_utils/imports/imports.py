from pathlib import Path
from typing import *
from dataclasses import dataclass, field
import fnmatch, fnmatch, os, glob, platform, textwrap, pkgutil, re, textwrap, sys, types, importlib, importlib.util, inspect
from types import ModuleType
# Accept strings like:
#   "/local/abs/dir"
#   "relative/local/dir"
#   "user@host:/abs/dir"
REMOTE_RE = re.compile(r"^(?P<host>[^:\s]+@[^:\s]+):(?P<path>/.*)$")
AllowedPredicate = Optional[Callable[[str], bool]]
