#!/usr/bin/env python3
# -*- coding : utf-8 -*-
"""Utility module: logging support."""
from __future__ import annotations
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL, getLogger
import logging
import os
import sys


__all__ = [
    # Export from `logging`
    "NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL",
    "getLogger",
    # Defined here
    "TIMESTAMP", "DEFAULT_LEVEL", "ICONS",
    "cli_configure",
]


TIMESTAMP: bool = True

ICONS = {
    NOTSET:   "[ ]",
    DEBUG:    "[#]",
    INFO:     "[i]",
    WARNING:  "[!]",
    ERROR:    "[x]",
    CRITICAL: "{x}",
}

DEFAULT_LEVEL = INFO if __debug__ else WARNING  # '-O' works like a '-q'
_setup_done: bool = False


class ConsoleFormatter(logging.Formatter):
    """A customized logging formatter."""

    def __init__(self, lfmt: str, rfmt: str, *args, **kwargs) -> None:
        """Left and right formatter strings."""
        lfmt, rfmt = lfmt.replace('\0', ''), rfmt.replace('\0', '')
        super().__init__(f"{lfmt}\0{rfmt}", *args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        # Make the icon available
        setattr(record, "x", ICONS[record.levelno])
        left, right = super().format(record).split("\0")
        if right:
            # Right-align text
            width = os.get_terminal_size().columns  # Terminal width
            rows = left.split("\n")
            first = rows[0]
            if len(first) + 1 + len(right) <= width:
                # Don't add the right text if the left one is too long
                first += f"{' '*(width-len(first)-len(right))}{right}"
            return "\n".join([first, *rows[1:]])
        return left


def get_levels() -> list[int]:
    """Get the installed levels, as a list, in severity ascending order."""
    name2level: dict[str, int] | None
    if sys.version_info >= (3, 11):
        name2level = logging.getLevelNamesMapping()  # pylint: disable=no-member
    else:
        name2level = getattr(logging, "_nameToLevel", None)
    return sorted(set(
        name2level.values() if name2level
        else map(logging.getLevelName, 'CRITICAL ERROR WARNING INFO DEBUG NOTSET'.split(" "))
    ))


def cli_configure() -> None:
    """Setup `logging` based on command-line flags."""
    global _setup_done  # pylint: disable=global-statement
    if _setup_done:
        return
    levels = get_levels()
    # Controlla le varie flags che vengono passate al programma
    quietness = sys.argv.count("-q") - sys.argv.count("-v") + levels.index(DEFAULT_LEVEL)
    sys.argv = [x for x in sys.argv if x not in ("-v", "-q")]
    for arg in sys.argv.copy():
        if arg[0] == "-" and arg[1:] and set(arg[1:]) <= {"q", "v"}:
            quietness += arg.count("q") - arg.count("v")
            sys.argv.remove(arg)
    # Determina il livello a partire dalla `silenziosità` richiesta
    quietness = max(0, min(len(levels) - 1, quietness))
    level = levels[quietness]
    # Configurazione
    ch = logging.StreamHandler()
    ch.setFormatter(ConsoleFormatter("{x} {message}", "[{asctime}]", style="{", datefmt="%Y-%m-%d %H:%M:%S"))
    ch.setLevel(NOTSET)
    root = getLogger()
    root.addHandler(ch)
    root.setLevel(level)
    _setup_done = True


if not eval(os.environ.get("NO_AUTO_LOGGING_CONFIG", "0") or "0"):
    cli_configure()


if __name__ == "__main__":
    cli_configure()
    logger = getLogger(__name__)
    logger.critical("Message")
    logger.error("Message")
    logger.warning("Message")
    logger.info("Message")
    logger.debug("Message")
