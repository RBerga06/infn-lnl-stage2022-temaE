#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Un programma di utility che compila in Cython i moduli richiesti.

    python compile.py [COMMAND] [ARGUMENTS]
    python compile.py help
    python compile.py commands
"""
from __future__ import annotations

from typing import Any, Callable, NoReturn, Sequence
from functools import reduce
from pathlib import Path
import operator as op
import subprocess
import shutil
import sys
import os


def _dep_error(pkg: str, req: str, msg: str) -> NoReturn:
    print(f"""\
ERROR: {msg}

Please install {pkg} via:
    pip install "{pkg}{req}"
""", file=sys.stderr)
    sys.exit(1)


try:
    from packaging.version import Version as V
except ModuleNotFoundError:
    try:
        from setuptools._vendor.packaging.version import Version as V
    except ModuleNotFoundError:
        _dep_error("setuptools", "", "setuptools not found.")


CYTHON_MIN_V = V("3.0.0a7")


def _cython_dep_error(msg: str) -> NoReturn:
    _dep_error("Cython", f">={CYTHON_MIN_V}", msg)


try:
    import cython
    from Cython.Build.Cythonize import main as cythonize
except ModuleNotFoundError:
    _cython_dep_error("Cython not found.")
else:
    CYTHON_VERSION = V(cython.__version__)
    if CYTHON_VERSION < CYTHON_MIN_V:  # type: ignore
        _cython_dep_error("No compatible Cython version found.")


SRC = Path(__file__).parent / "src"
TARGETS = [f.stem for f in SRC.glob("*.py")]
PYTHON_FRAMES: bool = True

# Set this to `False` if running in Spyder's IPython console
RUN_IN_SUBPROCESS: bool = True  # False


def list_targets() -> None:
    """Ottieni una lista di tutti i moduli disponibili.

    python compile.py list
    """
    print("all", *TARGETS, sep=", ")


def build(*targets: str) -> int:
    """Compila con Cython i moduli specificati.

    python compile.py build *[TARGETS]
    python compile.py build log root stagisti
    """
    if "all" in targets:
        return build(*TARGETS)
    for target in targets:
        if target not in TARGETS:
            continue
        sources = [str(f.resolve()) for f in [SRC / f"{target}.py", SRC / f"{target}.pxd"] if f.exists()]
        print(f"--> Building {target} ({', '.join(sources)})")
        try:
            args = [
                "-3",
                "-i",
                "--annotate-fullc",
                "-j", str(os.cpu_count()),
                # "-X", f"linetrace={PYTHON_FRAMES}",
                # "-X", f"profile={PYTHON_FRAMES}",
                "--lenient",
                *sources,
            ]
            print(f"$ cythonize {' '.join(args)}")
            cythonize(args)
        except SystemExit as e:
            return e.code
    return 0


def rm(*paths: str | Path):
    """Elimina i file e le cartelle in `paths`."""
    for path in paths:
        if not isinstance(path, Path):
            path = Path(path)
        if not path.exists():
            continue
        print(f"Removing {path.relative_to(SRC.parent)}")
        if path.is_dir():
            shutil.rmtree(path)
        else:
            os.unlink(path)


def clean(*targets) -> None:
    """Rimuovi gli elementi creati durante la `build`.

    python compile.py clean *[TARGETS]
    python compile.py clean root log
    python compile.py clean all
    python compile.py clean
    """
    if not targets or "all" in targets:
        rm(
            *SRC.glob("*.c"),
            *SRC.glob("*.html"),
            *SRC.glob("*.so"),
            *SRC.glob("*.pyd"),
            SRC / "build",
        )
        return
    for target in targets:
        rm(
            SRC / f"{target}.c",
            SRC / f"{target}.html",
            *SRC.glob(f"{target}.*.so"),
            *SRC.glob(f"build/lib.*/{target}.*.so"),
        )


_SYS_FLAGS = dict(
    debug               = "d",
    inspect             = "i",
    interactive         = "i",
    isolated            = "I",
    optimize            = "O",
    dont_write_bytecode = "B",
    no_user_site        = "s",
    no_site             = "S",
    ignore_environment  = "E",
    verbose             = "v",
    bytes_warning       = "b",
    quiet               = "q",
    hash_randomization  = "R",
    dev_mode            = "X dev",
    utf8_mode           = "X utf8",
)


def _sys_flags() -> list[str]:
    """Get CLI arguments for `sys.flags` and `sys.warnoptions`."""
    return [
        *reduce(
            op.add,
            (
                f"-{opt*val}".split(" ") for flag, opt in _SYS_FLAGS.items()
                if (val := getattr(sys.flags, flag))
            )
        ),
        *(f"-W{opt}" for opt in sys.warnoptions)
    ]


RUN = r"""\
print(f'\n--> Importing $$')
import $$
func = getattr($$, 'main', getattr($$, 'test', None))
print(f'\n--> $$ has been imported from {$$.__file__}')
if func:
    print(f'--> Running $$.{func.__name__}()')
    func()
"""


def _run(code: str, args: list[str], additional_sys_flags: Sequence[str] = ()) -> int:
    # Run in subprocess
    if RUN_IN_SUBPROCESS:
        argv = [
            sys.executable,
            *{*_sys_flags(), *additional_sys_flags},
            "-c", code,
            *args,
        ]
        return subprocess.run(argv, check=False).returncode
    # Run in the same process
    sys.argv = args.copy()
    try:
        exec(code, {}, {})  # pylint: disable=exec-used
    except SystemExit as e:
        return e.code
    return 0


def run(*argv: str) -> int:
    """Compila ed esegui il modulo dato con gli argomenti dati.

    python *[OPZIONI PYTHON] compile.py run [PROGRAMMA] *[ARGOMENTI/OPZIONI PROGRAMMA]
    python -O compile.py run root -vv data.root
    """
    args = list(argv)
    target = ""
    for arg in args:
        if not arg.startswith("-"):
            target = arg
            break
    if not target:
        raise ValueError("A target must be specified!")
    build(target)
    os.chdir(SRC)
    index = args.index(target)
    args[index] = RUN.replace("$$", target)
    return _run(
        RUN.replace("$$", target),
        args[index + 1:],
        additional_sys_flags=args[:index],
    )


def help(cmd: str | None = None, /) -> None:
    """Get help for a given command.

    python compile.py help [COMMAND]
    python compile.py help commands
    """
    if cmd is None:
        print(__doc__)
        help("help")
    else:
        print(COMMANDS.get(cmd, help).__doc__)


def list_commands() -> None:
    """List the available commands.

    python compile.py commands
    """
    print(*COMMANDS, sep=" ")


COMMANDS = dict(
    run=run,
    build=build,
    clean=clean,
    list=list_targets,
    help=help,
    commands=list_commands,
)


def cli(argv: list[str]) -> int | None:
    """Interfaccia da riga di comando."""
    if len(argv) < 1:
        return help()
    first = argv.pop(0)
    if first in COMMANDS:
        cmd = COMMANDS[first]
    else:
        cmd = build
        argv = [first] + argv
    return cmd(*argv)


if __name__ == "__main__":
    sys.exit(cli(sys.argv[1:]) or 0)
