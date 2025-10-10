# PyProjectLib


## Description

Python package for managing local python projects and repositories

## Install

```
pip install pyprojectlib
```

## Usage

### Command Line Usage: "ppl"

usage: ppl [-h] {new,push,pack} ...

Package for managing local python projects and repositories

positional arguments:

* {new,push,pack}  Command to execute (options below)
    * new            Create a new repo, project, or user of a repo
    * push           Save your python project in a local repository
    * pack           Package python project into a distributable module

### Command Line Usage: "ppl">"new"

usage: ppl new [-h] {repo,proj,user} ...

positional arguments:

* {repo,proj,user}  Create something (options below)
    * repo            Create a new empty repository
    * proj            Create a new empty project
    * user            Add a new user to a local repository

### Command Line Usage: "ppl">"new">"repo"

usage: ppl new repo repopath [-h] [-name NAME] [-email EMAIL] [-gituser GITUSER]

positional arguments:
* repopath    Path to local python repository. Directory name = repo name.

options:
* -name NAME, -n NAME             Your full name
* -email EMAIL, -e EMAIL          Your email address
* -gituser GITUSER, -g GITUSER    Your username on Github

### Command Line Usage: "ppl">"new">"project"

usage: ppl new proj projpath [-h]

positional arguments:
* projpath    Path to python project. Directory name = project name.

### Command Line Usage: "ppl">"new">"user"

usage: ppl new user repopath [-h] [-name NAME] [-email EMAIL] [-gituser GITUSER]

positional arguments:
* repopath              Path to local python repository. Directory name = repo name.

options:
* -name NAME, -n NAME             Your full name
* -email EMAIL, -e EMAIL          Your email address
* -gituser GITUSER, -g GITUSER    Your username on Github

### Command Line Usage: "ppl">"push"
usage: ppl push repopath projpath [-h] [-relpath RELPATH] [-noclean] [-nodoc] [-notest] [-version VERSION] [-name NAME] [-email EMAIL] [-gituser GITUSER]

positional arguments:
* repopath              Path to local python repository. Directory name = repo name.
* projpath              Path to python project. Directory name = project name.

options:
* -relpath RELPATH, -r RELPATH    Relative path from repository basedir to add project
* -noclean, -nc                   Flag to prevent checking py files for cleanliness
* -nodoc, -nd                     Flag to prevent html documentation creation
* -notest, -nt                    Flag to prevent pytest from running
* -version VERSION, -v VERSION    Version number of python project (X.Y.Z)
* -name NAME, -n NAME             Your full name
* -email EMAIL, -e EMAIL          Your email address
* -gituser GITUSER, -g GITUSER    Your username on Github

### Command Line Usage: "ppl">"pack"
usage: ppl pack projpath [-h] [-upload] [-install] [-version VERSION] [-name NAME] [-email EMAIL] [-gituser GITUSER] [-pyversion PYTHONVERSION]

positional arguments:
* projpath              Path to python project. Directory name = project name.

options:
* -upload, -u                         Flag to upload python module to PYPI after packaging it
* -install, -i                        Flag to install python module after packaging it
* -version VERSION, -v VERSION        Version number of python project (X.Y.Z)
* -name NAME, -n NAME                 Your full name
* -email EMAIL, -e EMAIL              Your email address
* -gituser GITUSER, -g GITUSER        Your username on Github
* -pyversion PYVERSION, -p PYVERSION  Minimum version of Python required
* -filetypes FILETYPES, -t FILETYPES  Comma-seperated list of file types to include

### Python In-Line Usage

* Example below can be ran as a standalone code example
* Example includes standard Python packages shutil, os, and sys
* In-line usage of pypackagelib is shown when calling "ppl."

```
from os import path
import sys
from shutil import rmtree, copytree
from pyprojectlib.pyuser import User  # type: ignore # pylint: disable=E0401,C0413
from pyprojectlib.pyrepo import Repository  # type: ignore # pylint: disable=E0401,C0413
import pyprojectlib as ppl  # type: ignore # pylint: disable=E0401,C0413,E0611


def test_setup_pyproject():
    """function for testing setup_pyproject"""

    version = "0.0.1"
    pkgpath = path.join(testdir, "../")
    initpath = path.join(testdir, "../../testproj1")
    initpathcopy = path.join(testdir, "examples", "testproj1")
    repopath1 = path.join(testdir, "../../testrepo1")
    repopathcopy1 = path.join(testdir, "./examples/testrepo1")
    repopath2 = path.join(testdir, "../../testrepo2")
    repopathcopy2 = path.join(testdir, "./examples/testrepo2")

    # Delete old tests
    deletelist = [
        initpath,
        initpathcopy,
        repopath1,
        repopathcopy1,
        repopath2,
        repopathcopy2,
    ]
    for dirpath in deletelist:
        if path.exists(dirpath):
            rmtree(dirpath)

    # create new project
    ppl.init_project(initpath)

    # create a user object
    userargs = {
        "name": "Jason Krist",
        "email": "jkrist2696@gmail.com",
        "gituser": "jkrist2696",
    }
    user = User(**userargs)

    # Create new repo and push this package
    ppl.init_repo(repopath1, **userargs)
    repo = Repository(repopath1, user)
    repo.push(pkgpath, version=version, test=False, relpath="python/generic")

    # Create a second repo and push this package
    ppl.init_repo(repopath2, **userargs)
    repo = Repository(repopath2, user)
    repo.push(pkgpath, version=version, test=False, relpath=".")
    # push again to act as new version
    repo.push(pkgpath, test=False)

    # Move all to examples folder
    copytree(initpath, initpathcopy)
    rmtree(initpath)
    copytree(repopath1, repopathcopy1)
    rmtree(repopath1)
    copytree(repopath2, repopathcopy2)
    rmtree(repopath2)

    # package this project
    ppl.Log.package_project(pkgpath, user)


if __name__ == "__main__":
    test_setup_pyproject()


```

## Read The Docs

Download "docs" folder or [check preview](https://htmlpreview.github.io/?https://github.com/jkrist2696/pyprojectlib/blob/main/docs/index.html).

## Contributing

Message me on Github.

## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)

## Copyright:

(c) 2023, Jason Krist


