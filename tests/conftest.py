#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests configuration."""
from __future__ import annotations
from functools import wraps

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, TypeVar, cast
import matplotlib.pyplot as plt
from matplotlib.testing.decorators import image_comparison
import pytest


def fix_sys_path():
    """Fix `sys.path`."""
    path = str(Path(__file__).parent.parent/"src")
    if path not in sys.path:
        sys.path.append(path)


@contextmanager
def sys_argv(argv: list[str]) -> Iterator[list[str]]:
    """Patch sys.argv."""
    orig = sys.argv.copy()
    sys.argv = argv.copy()
    try:
        yield argv
    finally:
        sys.argv = orig.copy()


@contextmanager
def chdir(path: Path) -> Iterator[Path]:
    """`chdir(path)` as a contextmanager."""
    orig = Path.cwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(orig)


_F = TypeVar("_F", bound=Callable[..., Any])


class _mpl_mocked_show:
    def __init__(self):
        self.figure = None

    def __call__(self):
        self.figure = plt.gcf()


def mpl_test(filename: str | None = None) -> Callable[[_F], _F]:
    figure = None

    def mocked_show():
        nonlocal figure
        figure = plt.gcf()

    def decorator(f: _F) -> _F:
        @wraps(f)
        @pytest.mark.mpl_image_compare(baseline_dir="images/baseline", filename=filename)
        @wraps(f)
        def func(*args, **kwargs):
            with pytest.MonkeyPatch.context() as mp:
                mp.setattr(plt, "show", mocked_show)
                f(*args, **kwargs)
                return figure
        return cast(_F, func)

    return decorator


def pytest_sessionstart():
    """Initialize tests."""
    fix_sys_path()
