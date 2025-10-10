"""
Written by Jason Krist
"""

from argparse import ArgumentParser

# CLI variable and command names
PROG = "ppl"
CMDNAME = "command"
NEWNAME = "new"
PUSHNAME = "push"
PACKNAME = "pack"
REPONAME = "repo"
PROJNAME = "proj"
USERNAME = "user"
REPOPATHNAME = "repopath"
PROJPATHNAME = "projpath"
NAMENAME = "name"
EMNAME = "email"
GUNAME = "gituser"
PYVERNAME = "pyversion"
FILETNAME = "filetypes"
RELNAME = "relpath"
NCNAME = "noclean"
NDNAME = "nodoc"
NTNAME = "notest"
VERNAME = "version"
UPNAME = "upload"
INNAME = "install"

# Helper strings for Command Line Arguments
DESC_H = "Package for managing local python projects and repositories"
COMMAND_H = "Command to execute (options below)"
NEW_H = "Create a new repo, project, or user of a repo"
NEW_OPTS_H = "Create something (options below)"
PUSH_H = "Save your python project in a local repository"
PACK_H = "Package python project into a distributable module"
REPO_H = "Create a new empty repository"
PROJ_H = "Create a new empty project"
USER_H = "Add a new user to a local repository"
REPOPATH_H = "Path to local python repository. Directory name = repo name."
PROJPATH_H = "Path to python project. Directory name = project name."
VERSION_H = "Version number of python project (X.Y.Z)"
INSTALL_H = "Flag to install python module after packaging it"
UPLOAD_H = "Flag to upload python module to PYPI after packaging it"
RELPATH_H = "Relative path from repository basedir to add project"
NOCLEAN_H = "Flag to prevent checking py files for cleanliness"
NODOC_H = "Flag to prevent html documentation creation"
NOTEST_H = "Flag to prevent pytest from running"
NAME_H = "Your full name"
EMAIL_H = "Your email address"
GITU_H = "Your username on Github"
PYVERS_H = "Minimum version of Python required"
FILET_H = "Comma-seperated list of file types to include"


def cli_parse():
    """Run command line parsing"""

    parser = ArgumentParser(prog=PROG, description=DESC_H)
    subparsers = parser.add_subparsers(dest=CMDNAME, help=COMMAND_H)
    new_parser = subparsers.add_parser(NEWNAME, help=NEW_H)
    new_subparsers = new_parser.add_subparsers(dest=NEWNAME, help=NEW_OPTS_H)

    newrepo_parser = new_subparsers.add_parser(REPONAME, help=REPO_H)
    newrepo_parser.add_argument(REPOPATHNAME, type=str, help=REPOPATH_H)

    newproj_parser = new_subparsers.add_parser(PROJNAME, help=PROJ_H)
    newproj_parser.add_argument(PROJPATHNAME, type=str, help=PROJPATH_H)

    newuser_parser = new_subparsers.add_parser(USERNAME, help=USER_H)
    newuser_parser.add_argument(REPOPATHNAME, type=str, help=REPOPATH_H)
    newuser_parser.add_argument(f"-{NAMENAME}", "-n", type=str, default="", help=NAME_H)
    newuser_parser.add_argument(f"-{EMNAME}", "-e", type=str, default="", help=EMAIL_H)
    newuser_parser.add_argument(f"-{GUNAME}", "-g", type=str, default="", help=GITU_H)

    push_parser = subparsers.add_parser("push", help=PUSH_H)
    push_parser.add_argument(REPOPATHNAME, type=str, help=REPOPATH_H)
    push_parser.add_argument(PROJPATHNAME, type=str, help=PROJPATH_H)
    push_parser.add_argument(f"-{RELNAME}", "-r", type=str, default="", help=RELPATH_H)
    push_parser.add_argument(f"-{NCNAME}", "-nc", action="store_true", help=NOCLEAN_H)
    push_parser.add_argument(f"-{NDNAME}", "-nd", action="store_true", help=NODOC_H)
    push_parser.add_argument(f"-{NTNAME}", "-nt", action="store_true", help=NOTEST_H)
    push_parser.add_argument(f"-{VERNAME}", "-v", type=str, default="", help=VERSION_H)
    push_parser.add_argument(f"-{NAMENAME}", "-n", type=str, default="", help=NAME_H)
    push_parser.add_argument(f"-{EMNAME}", "-e", type=str, default="", help=EMAIL_H)
    push_parser.add_argument(f"-{GUNAME}", "-g", type=str, default="", help=GITU_H)

    pack_parser = subparsers.add_parser("pack", help=PACK_H)
    pack_parser.add_argument(PROJPATHNAME, type=str, help=PROJPATH_H)
    pack_parser.add_argument(f"-{UPNAME}", "-u", action="store_true", help=UPLOAD_H)
    pack_parser.add_argument(f"-{INNAME}", "-i", action="store_true", help=INSTALL_H)
    pack_parser.add_argument(f"-{VERNAME}", "-v", type=str, default="", help=VERSION_H)
    pack_parser.add_argument(f"-{NAMENAME}", "-n", type=str, default="", help=NAME_H)
    pack_parser.add_argument(f"-{EMNAME}", "-e", type=str, default="", help=EMAIL_H)
    pack_parser.add_argument(f"-{GUNAME}", "-g", type=str, default="", help=GITU_H)
    pack_parser.add_argument(f"-{PYVERNAME}", "-p", type=str, default="", help=PYVERS_H)
    pack_parser.add_argument(f"-{FILETNAME}", "-ft", type=str, default="", help=FILET_H)

    args = parser.parse_args()
    argitems = vars(args).items()
    args_str = "\n    ".join([f"{key.ljust(8)}: {value}" for key, value in argitems])
    print(f"\nCommand Line Args:\n    {args_str}\n")
    helpdict: dict[str, str] = {}
    helpdict[CMDNAME] = parser.format_help()
    helpdict[NEWNAME] = new_parser.format_help()
    helpdict[NEWNAME + REPONAME] = newrepo_parser.format_help()
    helpdict[NEWNAME + PROJNAME] = newproj_parser.format_help()
    helpdict[NEWNAME + USERNAME] = newuser_parser.format_help()
    helpdict[PUSHNAME] = push_parser.format_help()
    helpdict[PACKNAME] = pack_parser.format_help()

    return args, helpdict


def print_all_help(helpdict: dict[str, str]):
    """print all strings in dictionary"""
    for string in helpdict.values():
        print(string)


if __name__ == "__main__":
    _args, helper = cli_parse()
    print_all_help(helper)
