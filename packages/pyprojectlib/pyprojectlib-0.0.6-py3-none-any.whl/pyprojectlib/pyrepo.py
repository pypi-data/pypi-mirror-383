"""
Written by Jason Krist
"""

from os import listdir, makedirs, mkdir, path
from re import findall
from shutil import copyfile, copytree

import pytest  # pylint: disable=E0401
from cleandoc import clean_all, gen_docs
from git import Repo

from . import constants as CONS  # type: ignore # pylint: disable=E0611,E0401
from .helper import prompt_user, remove_item
from .pypackage import Package
from .pyproject import Project
from .pyuser import User


class Repository:
    """local repo for saving code modules"""

    def __init__(self, repopath: str, user: User):
        """init"""
        self.path = path.realpath(repopath)
        self.name = path.basename(repopath)
        self.projectnames: list[str] = []
        self.projpath = path.join(repopath, CONS.PROJECTS_DIR)
        self._get_projects()
        self.userpath = path.join(repopath, CONS.USERS_DIR)
        self.user = user
        self.user.get_config(self.userpath)
        self.owner = self.get_owner()

    def push(self, projpath: str, **kwargs):
        """add project"""
        relpath = kwargs.pop("relpath", "")
        version = kwargs.pop("version", "")
        project = RepoProject(projpath, self, relpath=relpath, version=version)
        logstr = f'Pushing Project "{project.name}" to Repo "{self.name}"'
        CONS.log().info(logstr)
        project.update(**kwargs)
        self.projectnames.append(project.name)
        return project

    def pull(self, pkgname: str, version: str = ""):
        """get project version"""
        logstr = f"PULL FUNCTION NOT CREATED YET {pkgname} {version}"
        CONS.log().critical(logstr)

    def get_owner(self):
        """get"""
        ownpath = path.join(self.path, "owner")
        if not path.exists(ownpath):
            self.user.save_config(ownpath)
        owner = User()
        owner.load_config(ownpath)
        return owner

    def _get_projects(self):
        """get projects in repo"""
        self.projectnames = listdir(self.projpath)


class RepoProject(Project):
    """repoproject"""

    def __init__(self, pkgpath: str, repo: Repository, **kwargs):
        """init"""
        relpath = kwargs.pop("relpath", "")
        super().__init__(pkgpath, **kwargs)
        self.config_keys.append("relpath")
        self.repo = repo
        self._check_args()
        self.relpath = relpath
        # self.get_config(self.repo.projpath)
        self.repoprojpath = path.join(repo.path, self.relpath, self.name)
        self.versiondir = path.join(self.repoprojpath, CONS.VERSIONS_DIR)
        self.version = self.get_version(self.versiondir)
        self.versionpath = path.join(self.versiondir, self.version)
        self.required = [CONS.REQFILE, CONS.READFILE, CONS.TEST_DIR, f"src/{self.name}"]

    def update(
        self,
        test: bool = True,
        clean: bool = True,
        doc: bool = True,
        git: bool = True,
    ):
        """check code quality, then copy over new version"""
        self._check_required()
        srcpath = path.join(self.path, "src", self.name)
        if clean:
            logstr = (
                f'Repo "{self.repo.name}" Project "{self.name}" - '
                + "checking all source files for cleanliness"
            )
            CONS.log().info(logstr)
            clean_all(srcpath, write=False, skip=True)
        if test:
            pytest.main()  # Make sure this exits if there are errors!
        if not path.exists(self.repoprojpath):
            if path.exists(path.dirname(self.repoprojpath)):
                mkdir(self.repoprojpath)
            elif self.repo.user.user == self.repo.owner.user:
                makedirs(self.repoprojpath, exist_ok=True)
            else:
                errstr = (
                    f'User "{self.repo.user.user}" does not own the repository, '
                    + "so you cannot create new sub-directories. "
                    + f'You can ask the owner "{self.repo.owner.user}" '
                    + "nicely to create the sub-directory for you."
                )
                raise PermissionError(errstr)
        self.get_config(self.repo.projpath)
        if self.repo.user.user not in self.editors:
            errstr = (
                "Your username is not in list of editors for project:"
                + f"\n    project : {self.name}"
                + f"\n    username: {self.repo.user}"
                + f"\n    editors : {self.editors}"
            )
            raise PermissionError(errstr)
        self._remove_last_version()
        if not path.exists(self.versiondir):
            mkdir(self.versiondir)
        mkdir(self.versionpath)
        self._copy_and_backup()
        if doc:
            logstr = (
                f'Repo "{self.repo.name}" Project "{self.name}" - '
                + "creating documentation for latest version"
            )
            CONS.log().info(logstr)
            reposrcpath = path.join(self.repoprojpath, "src", self.name)
            gen_docs(reposrcpath, release=self.version)
        if git:
            logstr = (
                f'Repo "{self.repo.name}" Project "{self.name}" - '
                + "updating git repo"
            )
            CONS.log().info(logstr)
            if not path.exists(path.join(self.repoprojpath, ".git")):
                git_repo = Repo.init(self.repoprojpath)
            git_repo = Repo(self.repoprojpath)
            git_repo.index.add("**")
            git_repo.index.commit(self.version)
            git_repo.close()
        logstr = (
            f'Repo "{self.repo.name}" Project "{self.name}" '
            + f'update to version "{self.version}" has completed'
        )
        CONS.log().info(logstr)

    def package(self, **kwargs):
        """build project into package"""
        upload = kwargs.pop("upload", False)
        install = kwargs.pop("install", False)
        pyversion = kwargs.pop("pyversion", "")
        filetypes = kwargs.pop("filetypes", "")
        pkg = Package(self.repoprojpath, self.repo.user, **kwargs)
        pkg.save_toml(pyversion=pyversion, filetypes=filetypes)
        pkg.build(upload=upload, install=install)

    def _prompt(self):
        """prompt"""
        self.relpath = prompt_user("Relative Path in Repo: ", self.relpath)

    def _check_args(self):
        """check args"""
        if len(findall(r"[^_a-z]", self.name)):
            raise SyntaxWarning(
                "Project Folder name must contain only"
                + " lowercase letters or underscores. Directory Name: "
                + str(self.name)
            )
        logstr = f"\nSource Path: {self.path}\nRepo Path: {self.repo.path}\n"
        CONS.log().debug(logstr)
        if (self.path in self.repo.path) or (self.repo.path in self.path):
            raise RecursionError(
                "Source path and repo path overlap! This would result in a recursive copy tree."
            )

    def _check_required(self):
        """check"""
        for item in self.required:
            if not path.exists(path.join(self.path, item)):
                raise FileNotFoundError(path.join(self.path, item))

    def _remove_last_version(self):
        """remove old files"""
        for item in self.required:
            remove_item(path.join(self.repoprojpath, item))

    def _copy_and_backup(self):
        """copy backup"""
        for item in self.required:
            srcpath = path.join(self.path, item)
            repopath = path.join(self.repoprojpath, item)
            backuppath = path.join(self.versionpath, item)
            if path.isdir(srcpath):
                copytree(srcpath, repopath)
                copytree(srcpath, backuppath)
            elif path.isfile(srcpath):
                copyfile(srcpath, repopath)
                copyfile(srcpath, backuppath)
            else:
                raise FileNotFoundError(path.join(srcpath, item))
