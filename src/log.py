#!/usr/bin/env python3
# -*- coding : utf-8 -*-
"""Utility module: logging support."""
from __future__ import annotations
import logging
import os
import sys


TIMESTAMP: bool = True


ICONS = {
    logging.NOTSET:   "[ ]",
    logging.DEBUG:    "[#]",
    logging.INFO:     "[i]",
    logging.WARNING:  "[!]",
    logging.ERROR:    "[x]",
    logging.CRITICAL: "{x}",
}


class ConsoleFormatter(logging.Formatter):
    """A customized logging formatter."""

    def format(self, record: logging.LogRecord) -> str:
        # Make the icon available
        setattr(record, "x", ICONS[record.levelno])
        if TIMESTAMP:
            width = os.get_terminal_size().columns
            msg = super().format(record)
            asctime = self.formatTime(record, self.datefmt)
            rows = msg.split("\n")
            first = rows[0]
            if len(first) + 1 + len(asctime) <= width:
                first += f"{' '*(width-len(first)-len(asctime))}{asctime}"
            return "\n".join([first, *rows[1:]])
        return super().format(record)


def get_levels() -> list[int]:
    """Get the installed levels, as a list, in severity ascending order."""
    name2level: dict[str, int] | None
    if sys.version_info >= (3, 11):
        name2level = logging.getLevelNamesMapping()  # pylint: disable=no-member
    name2level = getattr(logging, "_nameToLevel", None)
    return sorted(set(
        name2level.values() if name2level
        else map(logging.getLevelName, 'CRITICAL ERROR WARNING INFO DEBUG NOTSET'.split(" "))
    ))


def logging_setup() -> None:
    """Setup `logging` based on command-line flags."""
    DEFAULT_LEVEL = logging.WARNING
    levels = get_levels()
    # Controlla le varie flags che vengono passate al programma
    quietness = sys.argv.count("-q") - sys.argv.count("-v") + levels.index(DEFAULT_LEVEL)
    sys.argv = [x for x in sys.argv if x not in ("-v", "-q")]
    for arg in sys.argv.copy():
        if arg[0] == "-" and arg[1:] and set(arg[1:]) <= {"q", "v"}:
            quietness += arg.count("q") - arg.count("v")
            sys.argv.remove(arg)
    # Determina il livello a partire dalla `silenziosità` richiesta
    quietness = max(0, min(len(levels) - 1, quietness))
    level = levels[quietness]
    # Configurazione
    ch = logging.StreamHandler()
    ch.setFormatter(ConsoleFormatter("{x} {message}", style="{", datefmt="[%Y-%m-%d %H:%M:%S]"))
    ch.setLevel(logging.NOTSET)
    logging.root.addHandler(ch)
    logging.root.setLevel(level)


if __name__ == "__main__":
    logging_setup()
    logger = logging.getLogger(__name__)
    logger.critical("Message")
    logger.error("Message")
    logger.warning("Message")
    logger.info("Message")
    logger.debug("Message")
