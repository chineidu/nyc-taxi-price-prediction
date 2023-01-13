from pathlib import Path

from setuptools import setup, find_namespace_packages

docs_packages = ["mkdocs==1.4.2", "mkdocstrings==0.19.1", "mkdocs-material==9.0.4"]
style_packages = ["black==22.10.0", "flake8==5.0.4", "isort==5.10.1", "pylint==2.15.10"]
test_packages = ["evidently==0.2.1", "pytest>=7.2.0", "pytest-cov==4.0.0"]

ROOT_DIR = Path(__file__).absolute().parent

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()


# Required packages
def list_reqs(*, filename: str = "requirements.txt") -> None:
    with open(ROOT_DIR / filename, encoding="utf-8") as f:
        return f.read().splitlines()


setup(
    name="my-package",
    version="0.1.0",
    description="A simple package by Neidu.",
    author="Chinedu Ezeofor",
    author_email="neidue@email.com",
    packages=find_namespace_packages(),
    url="https://github.com/chineidu/nyc-taxi-price-prediction",
    install_requires=list_reqs(),
    python_requires=">=3.8",
    extras_require={
        "dev": docs_packages + style_packages + test_packages + ["pre-commit==2.21.0"],
        "docs": docs_packages,
        "test": test_packages,
    },
    include_package_data=True,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
)
