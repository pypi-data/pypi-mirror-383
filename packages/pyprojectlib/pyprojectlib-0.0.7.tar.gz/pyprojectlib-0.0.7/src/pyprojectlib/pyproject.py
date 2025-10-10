"""pyproject"""

from getpass import getuser
from os import listdir, mkdir, path
from platform import python_version
from re import findall

import tomli
import tomli_w

from . import constants as CONS  # type: ignore # pylint: disable=E0611,E0401
from . import helper as hp


class Project:
    """project"""

    def __init__(self, projpath: str, version: str = ""):
        """init"""
        if not path.exists(projpath):
            raise FileNotFoundError(projpath)
        self.path = path.realpath(projpath)
        self.name = path.basename(self.path)
        self.version = version
        self.pyversion = python_version()
        user = getuser()
        self.owner = user
        self.editors = [user]
        self.config_keys = ["name", "path", "owner", "editors", "remote"]

    def get_config(self, dirpath: str):
        """get"""
        confpath = path.join(dirpath, f"{self.name}")
        if not path.exists(confpath):
            self._save_config(confpath)
        self._load_config(confpath)
        return self

    def get_description(self) -> str:
        """Get description from README"""
        readmefile = path.join(self.path, CONS.READFILE)
        with open(readmefile, "r", encoding="utf-8") as readmereader:
            readmestr = readmereader.read()
        result = findall(CONS.DESC_REGEX, readmestr)
        errstr = (
            f"Please include a Description section to your {CONS.READFILE} file."
            + f"\nReadme Path: {readmefile}"
            + f"\nDesc Search Result: {result}"
        )
        if len(result) == 0:
            raise SyntaxWarning(errstr)
        if len(result[0]) < 2:
            raise SyntaxWarning(errstr)
        description = result[0][1]
        description = description.replace("\n", "")
        return description

    def get_version(self, versionspath: str) -> str:
        """get_version"""
        if len(self.version) > 0:
            return self.version
        release_online, _found = hp.pypi_version(self.name)
        release_dir = "0.0.1"
        if path.exists(versionspath):
            version_dirs = listdir(versionspath)
            if version_dirs:
                version_dirs.sort(key=lambda v: [int(n) for n in v.split(".")])
                release_dir = version_dirs[-1]
        else:
            CONS.log().debug("Version directory could not be found")
            mkdir(versionspath)
        versions = [release_dir, release_online]
        versions.sort(key=lambda v: [int(n) for n in v.split(".")])
        latest_release = versions[-1]
        release_split = latest_release.split(".")
        release_split[2] = str(int(release_split[2]) + 1)
        release = ".".join(release_split)
        logstr = f'Project "{self.name}" Version (old >> new) = {latest_release} >> {release}'
        CONS.log().info(logstr)
        return release

    def _prompt(self):
        """prompt"""
        CONS.log().debug("_prompt function is meant to be overwritten")

    def _save_config(self, confpath: str):
        """save"""
        self._prompt()
        classtype = type(self).__name__
        logstr = f"{classtype} config path: {confpath}"
        CONS.log().debug(logstr)
        items = vars(self).items()
        tomldict = {key: value for key, value in items if key in self.config_keys}
        with open(confpath, "wb") as writer:
            tomli_w.dump(tomldict, writer)

    def _load_config(self, confpath: str):
        """load"""
        with open(confpath, "rb") as reader:
            userdict = tomli.load(reader)
        for key, value in userdict.items():
            setattr(self, key, value)
        classtype = type(self).__name__
        logstr = f"{classtype} config data: {userdict}"
        CONS.log().debug(logstr)
