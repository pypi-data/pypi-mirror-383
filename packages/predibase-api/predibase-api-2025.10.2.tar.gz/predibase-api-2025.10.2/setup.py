from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line]

with open(path.join(here, "version.txt")) as fp:
    version = fp.read().strip()

setup(
    name="predibase-api",
    version=version,
    author="Predibase Inc.",
    packages=find_packages(),
    zip_safe=False,
    install_requires=requirements,
    include_package_data=True,
)
