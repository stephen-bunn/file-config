# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains Invoke task functions for source checks and linters."""

import invoke

from .utils import report


def _build_linter_task(command, verbose=False):
    return command + (" --verbose" if verbose else "")


@invoke.task
def flake8(ctx, verbose=False):
    """Run Flake8 tool against source."""

    report.info(ctx, "linter.flake8", "running Flake8 check")
    ctx.run(_build_linter_task("flake8 src/* tests/*", verbose=verbose))


@invoke.task
def black(ctx, verbose=False):
    """Run Black tool check against source."""

    report.info(ctx, "linter.black", "running Black check")
    ctx.run(_build_linter_task("black --check src/* tests/*", verbose=verbose))


@invoke.task
def isort(ctx, verbose=False):
    """Run ISort tool check against source."""

    report.info(ctx, "linter.isort", "running ISort check")
    ctx.run(_build_linter_task("isort --check-only src/ tests/", verbose=verbose))


@invoke.task
def mypy(ctx, verbose=False):
    """Run MyPy tool check against source."""

    report.info(ctx, "linter.mypy", "running MyPy check")
    ctx.run(_build_linter_task("mypy src tests", verbose=verbose))
