#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://github.com/r3nt0n/bopscrk
# bopscrk - init script


name = "bopfast"
desc = "Faster bopscrk, Generate smart and powerful wordlists"
__version__ = "0.1.0"
__author__ = "JG"
__status__ = "Development"


def start():
    try:
        from .modules import main
    except ImportError:
        # catching except when running python3 bopscrk.py
        # (sketchy, need some refactor)
        from modules import main

    main.run(name, __version__)


if __name__ == "__main__":
    start()
