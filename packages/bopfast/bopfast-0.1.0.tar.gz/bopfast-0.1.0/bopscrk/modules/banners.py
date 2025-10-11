#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://github.com/r3nt0n/bopscrk
# bopscrk - banner and help functions module

from time import sleep
from random import randint

from .color import color
from .transforms import *


# Set the time interval (in secs) between printing each line
interval = 0.03


def banner(name, version, author="r3nt0n"):
    try:
        name_rand_leet = leet_transforms(name)
        name_rand_leet = name_rand_leet[randint(0, (len(name_rand_leet) - 1))]
    except:
        name_rand_leet = name
    name_rand_case = case_transforms_basic(name)
    name_rand_case = name_rand_case[
        randint((len(name_rand_case) - 3), (len(name_rand_case) - 1))
    ]
    # version = version[:3]
    print("  ,----------------------------------------------------,   ,------------,")
    sleep(interval)
    print(
        "  | [][][][][]  [][][][][]  [][][][]  [][__]  [][][][] |   |   v{}{}{}   |".format(
            color.BLUE, version, color.END
        )
    )
    sleep(interval)
    print("  |                                                    |   |------------|")
    sleep(interval)
    print(
        "  |  [][][][][][][][][][][][][][_]    [][][]  [][][][] |===|  {}-{}-{} |".format(
            color.RED, name_rand_leet, color.END
        )
    )
    sleep(interval)
    print(
        "  |  [_][][][]{}[]{}[][][][]{}[][]{}[][][ |   [][][]  [][][][] |===|  {}{}-{}-{} |".format(
            color.KEY_HIGHL,
            color.END,
            color.KEY_HIGHL,
            color.END,
            color.BOLD,
            color.RED,
            name,
            color.END,
        )
    )
    sleep(interval)
    print(
        "  | [][_][]{}[]{}[][][][][]{}[]{}[][][][]||     []    [][][][] |===|  {}-{}-{} |".format(
            color.KEY_HIGHL,
            color.END,
            color.KEY_HIGHL,
            color.END,
            color.RED,
            name_rand_case,
            color.END,
        )
    )
    sleep(interval)
    print(
        "  | [__][][][]{}[]{}[]{}[]{}[][][][][][__]    [][][]  [][][]|| |   |------------|".format(
            color.KEY_HIGHL, color.END, color.KEY_HIGHL, color.END
        )
    )
    sleep(interval)
    print(
        "  |   [__][________________][__]              [__][]|| |   |{}   {}   {}|".format(
            color.GREEN, author, color.END
        )
    )
    sleep(interval)
    print("  `----------------------------------------------------´   `------------´\n")
    sleep(interval)


def help_banner():
    print(
        "    Advanced usage and documentation: {}https://github.com/jotyGill/bopfast{}".format(
            color.ORANGE, color.END
        )
    )
    sleep(interval)


def bopscrk_banner():
    sleep(interval * 4)
    print("\n")
    print(
        "{}{} {}{}".format(
            color.ORANGE,
            " ▄▄▄▄    ▒█████   ██▓███  ",
            color.RED,
            "  █████▒▄▄▄        ██████ ▄▄▄█████▓",
        )
    )
    sleep(interval)
    print(
        "{}{} {}{}".format(
            color.ORANGE,
            "▓█████▄ ▒██▒  ██▒▓██░  ██▒",
            color.RED,
            "▓██   ▒▒████▄    ▒██    ▒ ▓  ██▒ ▓▒",
        )
    )
    sleep(interval)
    print(
        "{}{} {}{}".format(
            color.ORANGE,
            "▒██▒ ▄██▒██░  ██▒▓██░ ██▓▒",
            color.RED,
            "▒████ ░▒██  ▀█▄  ░ ▓██▄   ▒ ▓██░ ▒░",
        )
    )
    sleep(interval)
    print(
        "{}{} {}{}".format(
            color.ORANGE,
            "▒██░█▀  ▒██   ██░▒██▄█▓▒ ▒",
            color.RED,
            "░▓█▒  ░░██▄▄▄▄██   ▒   ██▒░ ▓██▓ ░ ",
        )
    )
    sleep(interval)
    print(
        "{}{} {}{}".format(
            color.ORANGE,
            "░▓█  ▀█▓░ ████▓▒░▒██▒ ░  ░",
            color.RED,
            "░▒█░    ▓█   ▓██▒▒██████▒▒  ▒██▒ ░ ",
        )
    )
    sleep(interval)
    print(
        "{}{} {}{}".format(
            color.ORANGE,
            "░▒▓███▀▒░ ▒░▒░▒░ ▒▓▒░ ░  ░",
            color.RED,
            " ▒ ░    ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░  ▒ ░░   ",
        )
    )
    sleep(interval)
    print(
        "{}{} {}{}".format(
            color.ORANGE,
            "▒░▒   ░   ░ ▒ ▒░ ░▒ ░     ",
            color.RED,
            " ░       ▒   ▒▒ ░░ ░▒  ░ ░    ░    ",
        )
    )
    sleep(interval)
    print(
        "{}{} {}{}".format(
            color.ORANGE,
            " ░    ░ ░ ░ ░ ▒  ░░       ",
            color.RED,
            " ░ ░     ░   ▒   ░  ░  ░    ░     ",
        )
    )
    sleep(interval)
    print(
        "{}{} {}{}".format(
            color.ORANGE,
            " ░          ░ ░           ",
            color.RED,
            "             ░  ░      ░          ",
        )
    )
    print("{}".format(color.END))

    # sleep(interval*2)
