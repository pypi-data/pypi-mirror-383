"""user"""
from getpass import getuser
from os import path

import tomli
import tomli_w

from . import constants as CONS  # type: ignore # pylint: disable=E0611,E0401
from .helper import prompt_user


class User:
    """user"""

    def __init__(self, name: str = "", email: str = "", gituser: str = ""):
        """init"""
        self.user = getuser()
        self.name = name
        self.email = email
        self.gituser = gituser

    def get_config(self, dirpath: str):
        """get"""
        confpath = path.join(dirpath, f"{self.user}")
        if not path.exists(confpath):
            self.save_config(confpath)
        self.load_config(confpath)
        return self

    def prompt(self):
        """prompt"""
        self.name = prompt_user("Name: ", self.name)
        self.email = prompt_user("Email: ", self.email)
        self.gituser = prompt_user("Github Username: ", self.gituser)

    def save_config(self, confpath: str):
        """save"""
        self.prompt()
        classtype = type(self).__name__
        logstr = f"{classtype} config path: {confpath}"
        CONS.log().debug(logstr)
        with open(confpath, "wb") as writer:
            tomli_w.dump(vars(self), writer)

    def load_config(self, confpath: str):
        """load"""
        with open(confpath, "rb") as reader:
            userdict = tomli.load(reader)
        for key, value in userdict.items():
            setattr(self, key, value)
        classtype = type(self).__name__
        logstr = f"{classtype} config data: {userdict}"
        CONS.log().debug(logstr)
