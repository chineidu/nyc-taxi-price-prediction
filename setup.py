from pathlib import Path
from setuptools import setup, find_packages


# Package meta-data.
NAME = "src"  # Package name
DESCRIPTION = "A simple package by Neidu."
URL = "https://github.com/chineidu/nyc-taxi-price-prediction"
EMAIL = "neiduezeofor@gmail.com"
AUTHOR = "Chinedu Ezeofor"
REQUIRES_PYTHON = ">=3.7.0"


ROOT_DIR = Path(__file__).absolute().parent

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()


# Required packages
def list_reqs(filename: str = "requirements.txt") -> None:
    with open(ROOT_DIR / filename) as f:
        return f.read().splitlines()


def get_package_version() -> str:
    """Obtain the package version."""
    with open(ROOT_DIR / "src/VERSION", "r") as file:
        _version = file.read().strip()
        return _version


setup(
    name=NAME,
    version=get_package_version(),
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    packages=find_packages(),
    url=URL,
    install_requires=list_reqs(),
    extras_require={},
    python_requires=REQUIRES_PYTHON,
    include_package_data=True,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
)


# if __name__ == '__main__':
#     print(find_packages("src"))
