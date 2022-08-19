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
from pytest import MonkeyPatch


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


def mpl_test(stem: str) -> Callable[[_F], _F]:
    def mocked_show():
        plt.savefig(f"result_images/{stem}.png")

    def decorator(f: _F) -> _F:
        @wraps(f)
        @chdir(Path(__file__).parent)
        @image_comparison(
            baseline_images=[stem],
            extensions=["png"],
        )
        @wraps(f)
        def func(*args, **kwargs):
            with MonkeyPatch.context() as monkeypatch:
                monkeypatch.setattr(plt, "show", mocked_show)
                return f(*args, **kwargs)
        return cast(_F, func)
    return decorator


def pytest_sessionstart():
    """Initialize tests."""
    fix_sys_path()
