#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Un programma di utility che compila in Cython i moduli richiesti.

    python compile.py [COMMAND] [ARGUMENTS]
    python compile.py help
    python compile.py commands
"""
import os
from pathlib import Path
import sys
from typing import NoReturn
import subprocess
import shutil


CYTHON_VERSION = "3.0.0a10"

def _cython_dep_error() -> NoReturn:
    print(f"""\
ERROR: No compatible Cython version found.

Please install this Cython version:
    pip install Cython={CYTHON_VERSION}
""", file=sys.stderr)
    sys.exit(1)

try:
    import cython
    from Cython.Build.Cythonize import main as cythonize
except ModuleNotFoundError:
    _cython_dep_error()
else:
    if cython.__version__ != CYTHON_VERSION:
        _cython_dep_error()


SRC = Path(__file__).parent/"src"
TARGETS = [f.stem for f in SRC.glob("*.py")]
PYTHON_FRAMES: bool = True


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
        if not target in TARGETS:
            continue
        sources = [str(f.resolve()) for f in [SRC/f"{target}.py", SRC/f"{target}.pxd"] if f.exists()]
        print(f"--> Building {target} ({', '.join(sources)})")
        try:
            args = [
                "-3ia",
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


def clean() -> None:
    """Rimuovi gli elementi creati durante la `build`.

    python compile.py clean
    """
    rm(
        *SRC.glob("*.c"),
        *SRC.glob("*.html"),
        *SRC.glob("*.so"),
        *SRC.glob("*.pyd"),
        SRC/"build",
    )


def run(*argv: str) -> int:
    """Compila ed esegui il modulo dato con gli argomenti dati.

    python compile.py run *[OPZIONI PYTHON] [PROGRAMMA] *[ARGOMENTI/OPZIONI PROGRAMMA]
    python compile.py run -O root -vv data.root
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
    args[index] = (
        f"import {target}; "
        f"func = getattr({target}, 'main', getattr({target}, 'test', lambda: None)); "
        f"print('-->', 'Running', '{target}.' + func.__name__ + '()', 'from', {target}.__file__); "
        f"func()"
    )
    args.insert(index, "-c")
    args.insert(0, sys.executable)
    print(f"--> Running {target}")
    return subprocess.run(args, check=False).returncode


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
