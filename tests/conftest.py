#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests configuration."""
from __future__ import annotations
from dataclasses import dataclass, field
from functools import wraps
import inspect

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, TypeVar, cast
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
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


if sys.version_info >= (3, 10):
    dataclass = dataclass(slots=True)


@dataclass
class MPLTest:
    """Test matplotlib output."""

    figures: list[Figure] = field(init=False, default_factory=list)

    def collects(self, reset: bool = True) -> Callable[[_F], _F]:
        """Collect figures from function."""
        def mocked_show():
            self.figures.append(plt.gcf())
            plt.close()
        def decorator(f: _F) -> _F:
            @wraps(f)
            def func(*args, **kwargs):
                with pytest.MonkeyPatch.context() as mp:
                    mp.setattr(plt, "show", mocked_show)
                    if reset:
                        self.figures.clear()
                    out = f(*args, **kwargs)
                    if isinstance(out, Figure):
                        self.figures.append(out)
                    return out
            return cast(_F, func)
        return decorator

    def tests(self, index: int, filename: str | None = None) -> Callable[[_F], _F]:
        """Test figure `index` after the given function."""
        def decorator(f: _F) -> _F:
            @pytest.mark.mpl_image_compare(baseline_dir="images/baseline", filename=filename)
            @wraps(f)
            def func(*args, **kwargs):
                out = f(*args, **kwargs)
                if not isinstance(out, Figure):
                    out = self.figures[index]
                return out
            return cast(_F, func)
        return decorator

    def test(self, index: int, filename: str | None = None, auto_def: bool = False) -> Callable[[], None]:
        """Create a test function for figure `index`."""
        @self.tests(index=index, filename=filename)
        def test(*_):
            pass
        test.__name__ = f"test_mpl_figure_{index}"
        if auto_def:
            inspect.stack()[1].frame.f_locals[test.__name__] = test
        return test


def pytest_sessionstart():
    """Initialize tests."""
    fix_sys_path()
