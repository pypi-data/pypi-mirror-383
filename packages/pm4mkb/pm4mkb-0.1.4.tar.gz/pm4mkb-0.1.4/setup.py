from os import path, walk
from platform import system
from re import M, search
from subprocess import run
from typing import Iterable

from setuptools import setup

LIB_TITLE = "pm4mkb"
PATH_SEPARATOR = "\\" if system() == "Windows" else "/"
ROOT_PATH = path.abspath(path.dirname(__file__))
LIB_PATH = f"{ROOT_PATH}{PATH_SEPARATOR}{LIB_TITLE}"
VERSION_FILE = f"{LIB_TITLE}{PATH_SEPARATOR}_version.py"


def get_packages() -> Iterable:
    """
    Returns:
        Iterable: list of packages available in library, nested starting with LIB_TITLE: pm4mkb
    """

    def replace_module_abs_path_with_relative_dotted(lib_module_abs_path):
        return f"{lib_module_abs_path.replace(f'{LIB_PATH}', f'{LIB_TITLE}').replace(f'{PATH_SEPARATOR}', '.')}"

    return [replace_module_abs_path_with_relative_dotted(module) for module, _, _ in walk(LIB_PATH)]


def get_readme_description() -> str:
    """
    Load README description
    """
    with open(path.join(f"{ROOT_PATH}{PATH_SEPARATOR}", "README.md"), encoding="utf-8") as f:
        description = f.read()

    return description


def get_version_number(version_file_path: str) -> str:
    version_line = open(version_file_path, "rt", encoding="utf8").read()
    pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"

    version_desc = search(pattern, version_line, M)
    if version_desc:
        return version_desc[1]

    raise RuntimeError(f"Unable to find version string in {version_file_path}.")


def parse_requirements(filename: str) -> Iterable:
    """load requirements from a pip requirements file"""
    return [
        line
        for line in (line.strip() for line in open(filename, encoding="utf-8"))
        if line and not line.startswith("#")
    ]


setup(
    name="pm4mkb",
    version=get_version_number(VERSION_FILE),
    description="Library that is intended to operate with various process mining tasks.",
    long_description=get_readme_description(),
    long_description_content_type="text/markdown",
    author="Maximov Pavel, MKB team",
    author_email="pm291097@list.ru",
    packages=get_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    install_requires=parse_requirements("requirements.txt"),
)
