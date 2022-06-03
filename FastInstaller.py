#! /usr/bin/env python3
# coding: utf-8

import os

# basic settings

NAME = ""
DESCRIPTION = ""
ICON = ""
TERMINAL = False

# uncoment the categories that you want.
categories = [
    # "AudioVideo",
    # "Audio",
    # "Video",
    # "Development",
    # "Education",
    # "Game",
    # "Graphics",
    # "Network",
    # "Office",
    # "Settings",
    # "Utility",
]


def main():
    print(flamewok.__version__)


if __name__ == "__main__":
    import pkg_resources
    dependencies = [
        'flamewok>=1.0.3',
    ]
    try:
        pkg_resources.require(dependencies)
    except pkg_resources.DistributionNotFound:
        os.system('pip install flamewok')

    import flamewok

    main()
