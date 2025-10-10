"""helpers"""

import logging
from os import makedirs, path, remove
from shutil import rmtree
from subprocess import run
from typing import Any, Tuple

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def contains_error(stdout: str, stderr: str):
    """Check if the stdout or stderr strings contain an error message
    Parameters
    ----------
    stdout : str
        standard out string from process execution
    stderr : str
        standard error string from process execution
    """
    if len(stderr.strip()) > 0:
        return stderr
    if "ERROR    " in stdout:
        return stdout
    return ""


def prompt_user(prompt: str, default: str):
    """Prompt user for input if default is empty string
    Parameters
    ----------
    prompt : str
        text prompt to display to user
    default : str
        value returned if it's length is > 0
    """
    if len(default) > 0:
        return default
    return input(prompt)


def create_dirs(srcpath: str, dirdict: dict[str, Any]):
    """_summary_
    Parameters
    ----------
    srcpath : str
        _description_
    dirdict : dict[dict]
        _description_
    """
    for dirname, subdirdict in dirdict.items():
        newsrcpath = path.join(srcpath, dirname)
        makedirs(newsrcpath, exist_ok=True)
        if len(subdirdict) > 0:
            create_dirs(newsrcpath, subdirdict)


def remove_item(itempath: str):
    """remote item"""
    if not path.exists(itempath):
        return
    if path.isdir(itempath):
        rmtree(itempath)
    else:
        remove(itempath)


def run_capture_out(cmd: list[str], **kwargs) -> Tuple[str, str]:
    """Run subprocess command and return the stdout and stderr.

    Parameters
    ----------
    cmd : list[str]
        Pass list of shell commands to subprocess.run
    shell : bool
        Pass shell keyword argument to subprocess.run

    Returns
    -------
    stdout  : str
        Standard Output returned from shell
    stderr : str
        Standard Error returned from shell

    """
    proc = run(
        cmd,
        capture_output=True,
        encoding="utf-8",
        check=False,
        errors="ignore",
        **kwargs,
    )
    return proc.stdout, proc.stderr


def config_log(file: str = "", newfile: bool = True):
    """Configure log file using logging module

    Parameters
    ----------
    file : str = ""
        Path to logfile to write
    newfile : bool = True
        Set to false to not overwrite existing log file

    Returns
    -------
    logger object

    """

    logname = "pyprojectlib"
    logger = logging.getLogger(logname)
    if logger.hasHandlers():
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        return logger
    fs = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    dfs = "%d-%m-%y | %H:%M:%S"
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=logging.DEBUG)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logger.propagate = False
    if len(file) > 0:
        if path.exists(file) and newfile:
            remove(file)
        file_handler = logging.FileHandler(file)
        print(f"\n{logname} logfile path: {path.realpath(file)}\n")
        file_handler.setFormatter(logging.Formatter(fs, dfs, "%"))
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    stdout_handler = logging.StreamHandler()  # stdout
    stdout_handler.setFormatter(logging.Formatter(fs, dfs, "%"))
    stdout_handler.setLevel(logging.INFO)
    logger.addHandler(stdout_handler)
    return logger


def check_version_format(version: str):
    """check if version string abides by criteria"""
    versionsplit = version.split(".")
    errstr = (
        "Version string must be in format X.Y.Z where X, Y, "
        + f"and Z are integers.\n    version: {version}"
    )
    if len(versionsplit) != 3:
        raise SyntaxError(errstr)
    for splitnum in versionsplit:
        try:
            int(splitnum)
        except ValueError as error:
            raise SyntaxError(errstr) from error


def attrs_to_dict(obj, namelist: list[str]) -> dict:
    """create kwargs from list of arg names"""
    kwdict = {}
    for name in namelist:
        kwdict[name] = getattr(obj, name)
    return kwdict


def pyversion_check(pyversion: str):
    """check if python version string is properly formatted"""
    pyvers = pyversion.split(".")
    helpstr = "Python version must have 2 numbers with a period between them (X.Y)"
    if any([len(pyvers) < 2, len(pyvers) > 2]):
        raise ValueError(f"pyversion: {pyversion}\n{helpstr}")
    if not all([pyvers[0].isdigit(), pyvers[1].isdigit()]):
        raise ValueError(f"pyversion: {pyversion}\n{helpstr}")
    if any(
        [
            int(pyvers[0]) <= 1,
            int(pyvers[0]) >= 4,
            int(pyvers[1]) < 0,
            int(pyvers[1]) > 12,
        ]
    ):
        raise ValueError(
            f"pyversion: {pyversion}\nPython Version must be in range [2.0, 3.12]"
        )


def pypi_version(pkgname: str, plus: bool = False) -> tuple[str, bool]:
    """get the latest version number of package from pypi"""
    # Initialize the Selenium driver
    driver = webdriver.Chrome()
    driver.get(f"https://pypi.org/project/{pkgname}/")
    # Wait until the page is loaded
    searchstr = "//img[contains(@src, '/static/images/logo-small')]"
    ec_wait = EC.presence_of_element_located((By.XPATH, searchstr))
    WebDriverWait(driver, 10).until(ec_wait)
    try:
        no_pkg_class = "viewport-section__heading"
        no_pkg_resp = driver.find_element(By.CLASS_NAME, no_pkg_class)
        no_pkg_str = "We looked everywhere but couldn't find this page"
        no_pkg = no_pkg_str.lower() in no_pkg_resp.text.lower()
    except NoSuchElementException as _e:
        no_pkg = False
    if no_pkg:
        driver.quit()
        return "0.0.1", False
    # Get the latest version number
    latest = driver.find_element(By.CLASS_NAME, "package-header__name").text
    release = latest.strip().split(" ")[1]
    driver.quit()
    if not plus:
        return release, True
    release_split = release.split(".")
    release_split[2] = str(int(release_split[2]) + 1)
    release = ".".join(release_split)
    return release, True
