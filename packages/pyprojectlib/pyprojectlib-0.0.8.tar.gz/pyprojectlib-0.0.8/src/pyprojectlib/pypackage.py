"""
pypackage

Manual Build Steps:
    python -m build
    twine check dist/*
    pip install .
    twine upload dist/*

"""

from os import mkdir, path
from re import split
from shutil import rmtree

import pipreqs.pipreqs as pr  # type: ignore # pylint: disable=E0401

from . import constants as CONS  # type: ignore # pylint: disable=E0611,E0401
from .helper import pyversion_check  # fmt: skip
from .helper import contains_error, prompt_user, run_capture_out
from .pyproject import Project
from .pyuser import User


class Package(Project):
    """package"""

    def __init__(self, pkgpath: str, user: User, **kwargs):
        """init"""
        # , cli: str = ""
        # self.remote = False
        # example cli: {self.name} = "{self.name}:{self.clifxn}"
        self.cli = kwargs.pop("cli", "")
        super().__init__(pkgpath, **kwargs)
        self.config_keys.append("cli")
        self.description = self.get_description()
        self.dep_pkgs: list[str] = []
        self.get_dep_pkgs()
        if len(self.version) == 0:
            self.version: str = self.get_version(
                path.join(self.path, CONS.VERSIONS_DIR)
            )
        userconfig = path.join(CONS.ENVPATH, CONS.USERS_DIR)
        if not path.exists(userconfig):
            mkdir(userconfig)
        self.author = user
        self.author.get_config(userconfig)
        projconfig = path.join(CONS.ENVPATH, CONS.PROJECTS_DIR)
        if not path.exists(projconfig):
            mkdir(projconfig)
        self.get_config(projconfig)
        self.required = [
            CONS.REQFILE,
            CONS.READFILE,
            CONS.TEST_DIR,
            f"src/{self.name}",
        ]

    def get_dep_pkgs(self):
        """get dep pkgs"""
        self._get_pipreqs()
        self._get_requirements()
        self._remove_dep_dups()
        self._save_requirements()

    def save_toml(self, pyversion: str = "", filetypes: str = ""):
        """save_toml
        Should decide where pyversion, filetypes, cli, etc. are provided"""
        depstr = ",".join([f'"{pkg}"' for pkg in self.dep_pkgs])
        toml_str = CONS.TOMLSTR_START + f'name = "{self.name}"\n'
        toml_str += f'version = "{self.version}"\n'
        author = self.author
        toml_str += 'authors = [{ name = "'
        toml_str += f'{author.name}", email = "{author.email}" }}]\n'
        toml_str += f'description = "{self.description}"\n'
        if "current" in pyversion.lower():
            toml_str += f'requires-python = ">={self.pyversion}"\n'
        elif len(pyversion) > 0:
            pyversion_check(pyversion)
            toml_str += f'requires-python = ">={pyversion}"\n'
        toml_str += f"dependencies = [{depstr}]\n"
        # toml_str += '[tool.setuptools.packages.find]\nwhere = ["src"]\n'
        # toml_str += f'exclude = ["*.__pycache__"]\n'
        toml_str += "[tool.setuptools.package-data]\n"
        filetypes_list = [ft for ft in filetypes.split(",") if len(ft) > 0]
        filetypes_list = [ft[1:] if ft[0] == "." else ft for ft in filetypes_list]
        filetypes_str = '", "*.'.join(["typed"] + filetypes_list)
        toml_str += f'{self.name} = ["*.{filetypes_str}"]\n'
        # toml_str += "[tool.setuptools.exclude-package-data]\n"
        # toml_str += f'{self.name} = ["__pycache__/*", "__pycache__"]\n'
        if len(self.cli.strip()) > 0:
            toml_str += "[project.scripts]\n"
            toml_str += f"{self.cli}\n"
        if len(author.gituser) > 0:
            toml_str += f'[project.urls]\n"Homepage" = "{CONS.GITHUB}/'
            toml_str += f'{author.gituser}/{self.name}"\n'
        tomlpath = path.join(self.path, "pyproject.toml")
        logstr = f"Saving pyproject.toml: {tomlpath}"
        CONS.log().info(logstr)
        with open(tomlpath, "wb") as writer:
            writer.write(bytes(toml_str, encoding="utf-8"))

    def build(self, upload=False, install=False):
        """build"""
        eggpath = path.join(self.path, "src", f"{self.name}.egg-info")
        if path.exists(eggpath):
            rmtree(eggpath)
        buildlog = f'Building Package "{self.name}" v{self.version}'
        checklog = f'Checking Package "{self.name}" v{self.version}'
        arglists = [
            (buildlog, [CONS.PYEXE, "-m", "build"]),
            (checklog, [CONS.TWINEEXE, "check", "dist/*"]),
        ]
        if install:
            installlog = f'Installing Package "{self.name}" v{self.version}'
            arglists.append((installlog, [CONS.PIPEXE, "install", "."]))
        if upload:
            uploadlog = f'Uploading Package "{self.name}" v{self.version}'
            arglists.append((uploadlog, [CONS.TWINEEXE, "upload", "dist/*"]))
        for logstr, arglist in arglists:
            CONS.log().info(logstr)
            stdout, stderr = run_capture_out(arglist, cwd=self.path)
            logstr = f"stdout from args: {arglist}\n\n{stdout}\n"
            CONS.log().debug(logstr)
            error_str = contains_error(stdout, stderr)
            if len(error_str) > 0:
                logstr = f"error from args: {arglist}\n\n{error_str}\n"
                CONS.log().error(error_str)
                raise ChildProcessError(error_str)
        if path.exists(path.join(self.path, CONS.VERSIONS_DIR)):
            mkdir(path.join(self.path, CONS.VERSIONS_DIR, self.version))

    def _prompt(self):
        """prompt"""
        # Add remote? self. = prompt_user(" ", self.)
        self.cli = prompt_user("Command-Line Interface String: ", self.cli)
        if len(self.cli) == 0:
            self.cli = " "

    def _check_required(self):
        """check"""
        for item in self.required:
            if not path.exists(path.join(self.path, item)):
                raise FileNotFoundError(path.join(self.path, item))

    def _get_pipreqs(self):
        """Get Module Dependencies and their Versions with pipreqs"""
        srcpath = path.join(self.path, "src", self.name)
        imports = pr.get_all_imports(srcpath, encoding="utf-8")
        pkgnames = pr.get_pkg_names(imports)
        pkgdicts_all = pr.get_import_local(pkgnames, encoding="utf-8")
        pkgdicts: list = []
        for pkgdict_orig in pkgdicts_all:
            pkgdicts_names = [pkgdict["name"] for pkgdict in pkgdicts]
            if pkgdict_orig["name"] not in pkgdicts_names:
                pkgdicts.append(pkgdict_orig)
        pkglist = [pkgdict["name"] + ">=" + pkgdict["version"] for pkgdict in pkgdicts]
        logstr = f"    pipreqs packages: {pkglist}"
        CONS.log().debug(logstr)
        self.dep_pkgs.extend(pkglist)

    def _get_requirements(self):
        """Get dependencies from requirements.txt"""
        reqfile = path.join(self.path, "requirements.txt")
        with open(reqfile, "r", encoding="utf-8") as reqreader:
            reqlines = reqreader.readlines()
        reqlines = [line.strip() for line in reqlines if len(line.strip()) > 0]
        logstr = f"    requirements.txt packages: {reqlines}"
        CONS.log().debug(logstr)
        self.dep_pkgs.extend(reqlines)

    def _remove_dep_dups(self):
        """remove duplicate packages"""
        new_dep_pkgs: list[str] = []
        new_pkgnames: list[str] = []
        for pkgstr in self.dep_pkgs:
            pkgsplit = split("[~<>=]", pkgstr)
            pkgname = pkgsplit[0]
            skipappend = False
            for np, new_pkgname in enumerate(new_pkgnames):
                if pkgname != new_pkgname:
                    continue
                skipappend = True
                if len(pkgstr) <= len(new_dep_pkgs[np]):
                    continue
                new_dep_pkgs[np] = pkgstr
            if skipappend:
                continue
            new_dep_pkgs.append(pkgstr)
            new_pkgnames.append(pkgname)
        self.dep_pkgs = new_dep_pkgs
        logstr = f"    dependent packages: {self.dep_pkgs}"
        CONS.log().debug(logstr)

    def _save_requirements(self):
        """resave edited requirements.txt"""
        reqfile = path.join(self.path, "requirements.txt")
        with open(reqfile, "w", encoding="utf-8") as writer:
            for pkgstr in self.dep_pkgs:
                writer.write(f"{pkgstr}\n")


# TOML EXTRAS BELOW:
# keywords = [""] add later?
# 'Operating System :: POSIX',
# 'Operating System :: MacOS',
# [tool.setuptools] need anything here?
# [tool.setuptools.packages.find]
# where = ["src"]
# I think below is covered automatically? I should test though
# ["pkg.assets"]
# pykwargs["package_data"] = ({f"{pkgname}": ["assets/*"]},)
# pykwargs["include_package_data"] = True
