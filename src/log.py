#!/usr/bin/env python3
# -*- coding : utf-8 -*-
"""Utility module: logging support."""
from __future__ import annotations
from typing import Any, Iterator, cast
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
from contextlib import contextmanager, _GeneratorContextManager
from io import StringIO
import logging
import inspect
import time
import os
import sys


# Prova ad importare `rich`, se possibile
NO_RICH = bool(eval(os.environ.get("NO_RICH", "") or "0"))
RICH: bool
try:
    if NO_RICH:
        raise ModuleNotFoundError
    import rich
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
    # Defined here
    "TIMESTAMP", "DEFAULT_LEVEL", "ICONS", "STYLES",
    "ConsoleFormatter", "Logger",
    "cli_configure", "getLogger", "moduleLogger",
    "debug", "info", "warning", "error", "critical", "exception", "task",
]


def style(message: str, style: str) -> str:
    """Apply the given `style` to `message` only if `rich` is available."""
    if RICH:
        return f"[{style}]{message}[/{style}]"
    return message


def sprint(*values, sep: str = " ", end: str = "\n", style: str = ""):
    """Print styled text to console."""
    if RICH:
        if style:
            io = StringIO()
            print(*values, sep=sep, end=end, file=io, flush=True)
            io.seek(0)
            rich.print(f"[{style}]{io.read()}[/{style}]", end="", flush=True)
        else:
            rich.print(*values, sep=sep, end=end, flush=True)
    else:
        print(*values, sep=sep, end=end, flush=True)


def getLogger(name: str = "") -> Logger:
    """Get the logger associated with this given name."""
    if not name:
        raise ValueError("You should not use the root logger!")
    if name == "root":
        name = "root_"
    return cast(Logger, logging.getLogger(name))


def moduleLogger(name: str | None = None, /, *, depth: int = 0) -> Logger:
    """Get the logger associated with the module that's calling this function."""
    return getLogger(
        inspect.stack()[1 + depth].frame.f_globals["__name__"]
        if name is None else name
    )


def taskLogger(module: str | None = None, /, id: str = "", *, depth: int = 0) -> Logger:
    """Get the task logger for the module that's calling this function."""
    tl = moduleLogger(module, depth=1 + depth).getChild("task")
    if id:
        return tl.getChild(id)
    return tl


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
    ERROR:    "red1",
    CRITICAL: "bold red",
}

DEFAULT_LEVEL = INFO if __debug__ else WARNING  # '-O' works like a '-q'

if RICH:
    MESSAGE_FORMAT = (
        "{x} {message}",
        "[/][dim][bold]{took}[/bold][{asctime}]"
    )
else:
    MESSAGE_FORMAT = (
        "{x} {message}",
        "{took}[{asctime}]"
    )

TASK_MESSAGE = style("--> {}", "bold")

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
        text = super().format(record)
        if RICH:
            text = f"[{STYLES[record.levelno]}]{text}[/]"
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
    __slots__ = ("_indent", "result", "_result_logged", "_timestamp")
    _indent: int
    result: str
    _result_logged: bool
    _timestamp: int | None

    def __init__(self, name: str, level: int | str = NOTSET) -> None:
        super().__init__(name, level)
        self._indent = 0
        self._task_reset()

    def _task_reset(self):
        """Resetta gli attributi relativi alla `task`."""
        self.result = ""
        self._result_logged = False
        self._timestamp = None

    def makeRecord(self, *args, **kwargs) -> logging.LogRecord:
        record = super().makeRecord(*args, **kwargs)
        setattr(record, "indent", self._indent + getattr(record, "indent", 0))
        return record

    @contextmanager
    def task(self, msg: str, level: int = INFO, id: str | None = None) -> Iterator[Logger]:
        """Log the fact we're doing something."""
        # pylint: disable=protected-access
        self.log(level, TASK_MESSAGE.format(msg))  # pylint: disable=logging-format-interpolation
        tsk = self.getChild("task")
        if id:
            tsk = tsk.getChild(id)
        tsk._indent = self._indent + 1
        tsk.save_timestamp()
        try:
            yield tsk
        finally:
            # Stampa il messaggio
            if not tsk._result_logged:
                tsk.done()
            # Resetta questo logger
            tsk._task_reset()

    def save_timestamp(self) -> None:
        """Salva il tempo attuale in nanosecondi."""
        self._timestamp = time.time_ns()

    @staticmethod
    def _repr_dt(dt: int) -> str:
        # Converti il ∆t in un formato utile
        if dt < 1_000:
            return f"{dt} ns"
        if dt < 1_000_000:
            return f"{dt/1_000} µs"
        if dt < 1_000_000_000:
            return f"{dt/1_000_000} ms"
        return time.strftime("%H:%M:%S", time.gmtime(dt / 1_000_000_000))

    def done(self, result: str | None = None, level: int = INFO) -> None:
        """Log a 'done (...)' message."""
        t = time.time_ns()
        if self._timestamp:
            extra = dict(took=f"took {self._repr_dt(t - self._timestamp)} ")
        else:
            extra = {}
        result = self.result if result is None else result
        self.log(level, f"done{f' ({result})' if result else ''}.", extra=extra)
        self._result_logged = True

    def fail(self, result: str | None = None, level: int = ERROR) -> None:
        """Log a 'fail (...)' message."""
        t = time.time_ns()
        if self._timestamp:
            extra = dict(took=f"took {self._repr_dt(t - self._timestamp)} ")
        else:
            extra = {}
        result = self.result if result is None else result
        self.log(level, f"failed{f' ({result})' if result else ''}.", extra=extra)
        self._result_logged = True


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
    root = logging.getLogger()
    root.addHandler(ch)
    root.setLevel(level)
    _setup_done = True


def task(msg: str, level: int = INFO, id: str | None = "") -> _GeneratorContextManager[Logger]:
    """Start logging a task."""
    return moduleLogger(depth=1).task(msg, level=level, id=id)


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
    # Silenzia i messaggi di debug di alcune librerie
    getLogger("matplotlib").setLevel(WARNING)


if __name__ == "__main__":
    cli_configure()
    logger = getLogger(__name__)
    logger.critical("Critical")
    logger.error("Error")
    logger.warning("Warning")
    logger.info("Info")
    logger.debug("Debug")
    with logger.task("Null task #1") as computation:
        pass
    with logger.task("Null task #2") as computation:
        computation.done()
    with logger.task("Null task #3") as computation:
        computation.done("explicit")
    with logger.task("Null task #4") as computation:
        computation.fail("explicit")
    with logger.task("Null task #5") as computation:
        computation.result = "custom result"
    with logger.task("Sleep task #1 (1s)") as computation:
        time.sleep(1)
        computation.fail()
    with logger.task("Sleep task #2 (10s, loop)") as computation:
        for _ in range(10):
            time.sleep(1)
        computation.done()
    with logger.task("Sleep task #3 (10s, loop, log at every iteration)") as computation:
        for _ in range(10):
            time.sleep(1)
            computation.info("Just slept 1s.")
        computation.done()
    logger.debug("About to define function `_foo` with `@task` decorator")

    @task("Foo task")
    def _foo(x: int) -> None:
        for __ in range(x):
            time.sleep(1)

    logger.debug("After defining function `_foo` with `@task` decorator")
    _foo(2)
