#! /usr/bin/env python3
# coding: utf-8

"""
REMINDER:
1- build
./setup.py sdist bdist_wheel
2- basic verifications
twine check dist/*
2.5- Deploy on testpypi (optionnal, site here : https://test.pypi.org/):
twine upload --repository testpypi dist/*
3- upload to PyPi
twine upload dist/*
"""

from geninstaller import __version__
import pathlib
from setuptools import setup


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="geninstaller",
    version=f"{__version__}",
    description=(
        "Linux universal app installer and manager, in the user's space only"
        ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/byoso/geninstaller",
    author="Vincent Fabre",
    author_email="peigne.plume@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
    ],
    packages=[
        "geninstaller",
        "geninstaller.plop",
        "geninstaller.plop.gui",
        "geninstaller.plop.database",
        "geninstaller.plop.database.migrations",
        "geninstaller.plop.installer",
        ],
    # include_package_data=True,
    package_data={'': ['*.sqlite3', '*.sql', 'installer', '*.png']},
    python_requires='>=3.6',
    install_requires=[
        "silly-db >= 2.0.1",
    ],
    keywords='install installer linux',
    entry_points={
        "console_scripts": [
            "geninstaller=geninstaller.cmd:cmd",
        ]
    },
    setup_requires=['wheel'],
)
