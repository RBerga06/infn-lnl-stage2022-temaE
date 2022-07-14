#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Un programma di utility che compila in Cython i moduli richiesti."""
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


def build(*targets: str) -> None:
    for target in targets:
        sources = [str(f.resolve()) for f in [SRC/f"{target}.py", SRC/f"{target}.pxd"] if f.exists()]
        if not sources:
            print(f"--> Skipping {target} (no sources found)")
            continue
        print(f"--> Building {target} ({', '.join(sources)})")
        cythonize(["-3i", *sources])


def rm(*paths: str | Path):
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
    rm(*SRC.glob("*.c"))
    rm(*SRC.glob("*.html"))
    rm(*SRC.glob("*.so"))
    rm(*SRC.glob("*.pyd"))
    rm(SRC/"build")


def run(*argv: str) -> int:
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
    args[index] = f"__import__('{target}').main()"
    args.insert(index, "-c")
    return subprocess.run(
        [sys.executable, *args],
    ).returncode


COMMANDS = dict(
    run=run,
    build=build,
    clean=clean
)


def cli(argv: list[str]) -> int | None:
    """Interfaccia da riga di comando."""
    if len(argv) < 1:
        raise ValueError("Please specify an argument.")
    first = argv.pop(0)
    if first in COMMANDS:
        cmd = COMMANDS[first]
    else:
        cmd = build
        argv = [first] + argv
    print(f"{cmd.__name__}({', '.join(argv)})")
    return cmd(*argv)


if __name__ == "__main__":
    sys.exit(cli(sys.argv[1:]) or 0)
