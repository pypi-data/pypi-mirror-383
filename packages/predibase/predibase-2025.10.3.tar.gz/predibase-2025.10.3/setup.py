import os
from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

extra_requirements = {"notebook": ["notebook", "jupyterlab"]}

with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line]

with open(path.join(here, "requirements_predictor.txt"), encoding="utf-8") as f:
    extra_requirements["predictor"] = [line.strip() for line in f if line]

version = {}
with open(os.path.join(here, "predibase", "version.py")) as fp:
    exec(fp.read(), version)

setup(
    name="predibase",
    version=version["__version__"],
    author="Predibase Inc.",
    packages=find_packages(),
    zip_safe=False,
    install_requires=requirements,
    extras_require=extra_requirements,
    entry_points={"console_scripts": ["pbase=predibase.cli:main"]},
    include_package_data=True,
)
