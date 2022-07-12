#!/usr/bin/env python3
# -*- coding : utf-8 -*-
"""Utility module: logging support."""
from __future__ import annotations
from contextlib import contextmanager
from typing import Any, ContextManager, Iterator, cast
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL, getLogger as _getLogger
import inspect
import time
import logging
import os
import sys


# Prova ad importare `rich`, se possibile
RICH: bool
try:
    import rich.markup
    import rich.logging
    import rich.highlighter
except ModuleNotFoundError:
    RICH = False
else:
    RICH = True


__all__ = [
    # Exported from `logging`
    "NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL",
    # Overridden from `logging`
    "getLogger", "debug", "info", "warning", "error", "critical", "exception",
    # Defined here
    "TIMESTAMP", "DEFAULT_LEVEL", "ICONS",
    "moduleLogger", "task", "cli_configure",
]


def getLogger(name: str = "") -> Logger:
    """Get the logger associated with this given name."""
    return cast(Logger, _getLogger(name))


def moduleLogger(name: str | None = None, /, *, depth: int = 0) -> Logger:
    """Get the logger associated with the module that's calling this function."""
    return getLogger(
        inspect.stack()[1 + depth].frame.f_globals["__name__"]
        if name is None else name
    )


TIMESTAMP: bool = True

ICONS = {
    NOTSET:   "[ ]",
    DEBUG:    "[#]",
    INFO:     "[i]",
    WARNING:  "[!]",
    ERROR:    "[x]",
    CRITICAL: "{x}",
}

STYLES = {
    NOTSET:   "normal",
    DEBUG:    "dim",
    INFO:     "cyan",
    WARNING:  "yellow",
    ERROR:    "red",
    CRITICAL: "bold red",
}

DEFAULT_LEVEL = INFO if __debug__ else WARNING  # '-O' works like a '-q'

if RICH:
    MESSAGE_FORMAT = (
        "{x} {message}",
        "[/][dim][bold]{took}[/bold][{asctime}]"
    )
else:
    MESSAGE_FORMAT = ("{x} {message}", "{took}[{asctime}]")

_setup_done: bool = False


class ConsoleFormatter(logging.Formatter):
    """A customized logging formatter."""

    def __init__(self, lfmt: str, rfmt: str, *args, **kwargs) -> None:
        """Left and right formatter strings."""
        lfmt, rfmt = lfmt.replace('\0', ''), rfmt.replace('\0', '')
        super().__init__(f"{lfmt}\0{rfmt}", *args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        # Make the console markup working
        if RICH:
            setattr(record, "markup", True)
        # Make the `icon` available and escape it if necessary
        icon = ICONS[record.levelno]
        if RICH:
            icon = rich.markup.escape(icon)
        setattr(record, "x", icon)
        # Fix `took` missing
        if not hasattr(record, "took"):
            setattr(record, "took", "")
        # Apply indent
        if hasattr(record, "indent"):
            record.msg = " " * getattr(record, "indent") * 4 + record.msg
            delattr(record, "indent")
        # Format and right-align text
        text = (f"[{STYLES[record.levelno]}]" + super().format(record) + "[/]")
        styles_len = len(text) - len(rich.markup.render(text)) if RICH else 0
        left, right = text.split("\0")
        if right:
            # Right-align text only if needed
            width = os.get_terminal_size().columns  # Terminal width
            rows = left.split("\n")
            first = rows[0]
            if len(first) + 1 + len(right) - styles_len <= width:
                # Don't add the right text if the left one is too long
                first += f"{' '*(width - len(first) - len(right) + styles_len)}{right}"
            return "\n".join([first, *rows[1:]])
        return left + "[/]"


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
        tsk = self.getChild("task")
        tsk._indent = self._indent + 1  # pylint: disable=protected-access
        t0 = time.time_ns()
        try:
            yield tsk
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
                dts = time.strftime("%H:%M:%S", time.gmtime(dt / 1_000_000_000))
            # Stampa il messaggio
            tsk.info(f"done{f' ({tsk.done_extra})' if tsk.done_extra else ''}.", extra=dict(took=f"took {dts} "))


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
    ch = rich.logging.RichHandler(
        highlighter=rich.highlighter.NullHighlighter(),
        show_level=False,
        show_time=False,
        rich_tracebacks=True,
        show_path=False,
    ) if RICH else logging.StreamHandler()
    ch.setFormatter(ConsoleFormatter(*MESSAGE_FORMAT, style="{", datefmt="%Y-%m-%d %H:%M:%S"))
    ch.setLevel(NOTSET)
    logging.setLoggerClass(Logger)
    root = getLogger()
    root.__class__ = Logger
    root.addHandler(ch)
    root.setLevel(level)
    root._indent = 0  # pylint: disable=protected-access
    _setup_done = True


def task(msg: str) -> ContextManager[Logger]:
    """Log an debug message."""
    return moduleLogger(depth=1).task(msg)


def debug(msg: Any, *args: Any, extra: dict[str, Any] | None = None, **kwargs) -> None:
    """Log an debug message."""
    moduleLogger(depth=1).debug(msg, *args, extra=extra, **kwargs)


def info(msg: Any, *args: Any, extra: dict[str, Any] | None = None, **kwargs) -> None:
    """Log an information."""
    moduleLogger(depth=1).info(msg, *args, extra=extra, **kwargs)


def warning(msg: Any, *args: Any, extra: dict[str, Any] | None = None, **kwargs) -> None:
    """Log a warning."""
    moduleLogger(depth=1).warning(msg, *args, extra=extra, **kwargs)


def error(msg: Any, *args: Any, extra: dict[str, Any] | None = None, **kwargs) -> None:
    """Log an error."""
    moduleLogger(depth=1).error(msg, *args, extra=extra, **kwargs)


def critical(msg: Any, *args: Any, extra: dict[str, Any] | None = None, **kwargs) -> None:
    """Log an error that causes the program's termination."""
    moduleLogger(depth=1).critical(msg, *args, extra=extra, **kwargs)


def exception(msg: Any, *args: Any, extra: dict[str, Any] | None = None, **kwargs) -> None:
    """Log an exception."""
    moduleLogger(depth=1).exception(msg, *args, extra=extra, **kwargs)


if not eval(os.environ.get("NO_AUTO_LOGGING_CONFIG", "0") or "0"):
    cli_configure()


if __name__ == "__main__":
    cli_configure()
    logger = getLogger(__name__)
    logger.critical("Critical")
    logger.error("Error")
    logger.warning("Warning")
    logger.info("Info")
    logger.debug("Debug")
    with logger.task("Running some serious computation...") as computation:
        time.sleep(1)
        computation.done_extra = "wasn't so useful"
