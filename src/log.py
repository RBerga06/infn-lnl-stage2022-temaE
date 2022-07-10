#!/usr/bin/env python3
# -*- coding : utf-8 -*-
"""Utility module: logging support."""
from __future__ import annotations
from contextlib import contextmanager
from typing import Iterator, cast
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL, getLogger as _getLogger
import time
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


def getLogger(name: str = "") -> Logger:
    """Get the logger associated with this given name."""
    return cast(Logger, _getLogger(name))


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
        # Make the `icon` available
        setattr(record, "x", ICONS[record.levelno])
        # Fix `took` missing
        if not hasattr(record, "took"):
            setattr(record, "took", "")
        # Apply indent
        record.msg = " " * getattr(record, "indent", 0) * 4 + record.msg
        delattr(record, "indent")
        # Format and right-align text
        left, right = super().format(record).split("\0")
        if right:
            # Right-align text only if needed
            width = os.get_terminal_size().columns  # Terminal width
            rows = left.split("\n")
            first = rows[0]
            if len(first) + 1 + len(right) <= width:
                # Don't add the right text if the left one is too long
                first += f"{' '*(width-len(first)-len(right))}{right}"
            return "\n".join([first, *rows[1:]])
        return left


class Logger(logging.Logger):
    """An enhanced logger."""
    _indent: int
    done_extra: str

    def __init__(self, name: str, level: int | str = NOTSET) -> None:
        super().__init__(name, level)
        self._indent = 0
        self.done_extra = ""

    def makeRecord(self, *args, **kwargs) -> logging.LogRecord:
        record = super().makeRecord(*args, **kwargs)
        setattr(record, "indent", self._indent + getattr(record, "indent", 0))
        return record

    @contextmanager
    def task(self, msg: str) -> Iterator[Logger]:
        """Log the fact we're doing something."""
        self.info(f"--> {msg}")
        task = self.getChild("task")
        task._indent = self._indent + 1  # pylint: disable=protected-access
        t0 = time.time_ns()
        try:
            yield task
        finally:
            t1 = time.time_ns()
            dt = t1 - t0
            # Converti il ∆t in un formato utile
            dts: str
            if dt < 1_000:
                dts = f"{dt} ns"
            elif dt < 1_000_000:
                dts = f"{dt/1_000} µs"
            elif dt < 1_000_000_000:
                dts = f"{dt/1_000_000} ms"
            else:
                dts = time.strftime("%H:%M:%S", time.gmtime(dt/1_000_000_000))
            # Stampa il messaggio
            task.info(f"done{f' ({task.done_extra})' if task.done_extra else ''}.", extra=dict(took=f"took {dts} "))


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
    ch.setFormatter(ConsoleFormatter("{x} {message}", "{took}[{asctime}]", style="{", datefmt="%Y-%m-%d %H:%M:%S"))
    ch.setLevel(NOTSET)
    logging.setLoggerClass(Logger)
    root = getLogger()
    root.__class__ = Logger
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
    with logger.task("Running some serious computation...") as computation:
        time.sleep(1)
        computation.done_extra = "wasn't so useful"
