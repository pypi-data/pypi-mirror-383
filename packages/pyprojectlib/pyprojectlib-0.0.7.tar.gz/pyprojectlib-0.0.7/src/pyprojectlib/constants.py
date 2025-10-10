"""
Written by Jason Krist
"""

import sys
from os import path

from .helper import config_log

log = config_log  # pylint: disable=R0903

NAME = "pyprojectlib"

PYPI = "https://pypi.org/project"
GITHUB = "https://github.com"

SRC_DIR = "src"
DOCS_DIR = "docs"
TEST_DIR = "test"
USERS_DIR = ".users"
VERSIONS_DIR = ".versions"
PROJECTS_DIR = ".projects"

REQFILE = "requirements.txt"
LICFILE = "LICENSE.txt"
READFILE = "README.md"
DESC_REGEX = r"(?s)# Description(.*?)#"

PYEXE = sys.executable
ENVPATH = path.dirname(PYEXE)
PIPEXE = path.join(ENVPATH, "Scripts", "pip3")
TWINEEXE = path.join(ENVPATH, "Scripts", "twine")

TOMLSTR_START = """
[tool.setuptools.packages.find]
where = ["src"]
exclude = ["**.__pycache__"]
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
[project]
license = "GPL-3.0-or-later"
readme = "README.md"
classifiers = [
    "Programming Language :: Python :: 3",
    'Operating System :: Microsoft :: Windows',
    'Operating System :: Unix',
]
"""

IGNORELIST = [
    ".versions/",
    ".users/",
    ".git/",
    ".mypy_cache/",
    ".vscode/",
    "build/",
    "dist/",
    "docs/conf.txt",  # "src/proj/__pycache__
    "test/__pycache__",
    "test/.mypy_cache/",
    "test/docs",
    "test/examples",
    "test/cleandoc_log.txt",
    "src/*.egg-info/",
    "src/*/__pycache/",
    "old/",
]
