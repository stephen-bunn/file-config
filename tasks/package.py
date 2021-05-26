# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains Invoke task functions for package building and testing."""

import shutil
import webbrowser
from pathlib import Path

import invoke

from .utils import report


@invoke.task
def test(ctx, verbose=False):
    """Run package tests."""

    test_command = "pytest"
    report.info(ctx, "package.test", "running package tests")
    if verbose:
        test_command += " --verbose"
    ctx.run(test_command)


@invoke.task(pre=[test])
def coverage(ctx, view=False):
    """Build coverage report for test run."""

    reports_dirpath = Path(__file__).parent.parent.joinpath("htmlcov")
    if not reports_dirpath.is_dir():
        report.debug(
            ctx,
            "package.coverage",
            f"creating coverage report directory at {reports_dirpath!s}",
        )
        reports_dirpath.mkdir()

    report.info(ctx, "package.coverage", "building coverage report")
    ctx.run(f"coverage html -d {reports_dirpath.as_posix()!s}")

    if view:
        index_filepath = reports_dirpath.joinpath("index.html")
        report.debug(ctx, "package.coverage", f"opening report from {index_filepath!s}")
        webbrowser.open(f"file:{index_filepath!s}")


@invoke.task
def clean(ctx):
    """Clean previously built package artifacts."""

    egg_name = f"{ctx.package.name}.egg-info"
    report.info(ctx, "pacakge.clean", "removing build directories")
    for artifact in ("dist", "build", egg_name, f"src/{egg_name}"):
        artifact_dir = ctx.directory / artifact
        if artifact_dir.is_dir():
            report.debug(ctx, "package.clean", f"removing directory {artifact_dir!s}")
            ctx.run(f"rm -rf {artifact_dir!s}")


@invoke.task
def format(ctx):
    """Auto format package source files."""

    isort_command = f"isort {ctx.package.directory!s}"
    black_command = f"black {ctx.package.directory.parent!s}"

    report.info(ctx, "package.format", "sorting imports")
    ctx.run(isort_command)
    report.info(ctx, "package.format", "formatting code")
    ctx.run(black_command)


@invoke.task()
def requirements(ctx):
    """Generate requirements.txt from pyproject.toml."""

    report.info(
        ctx, "package.requirements", "generating requirements.txt from Poetry's lock"
    )
    ctx.run("poetry export -f requirements.txt > requirements.txt")


@invoke.task(pre=[clean, format])
def build(ctx):
    """Build pacakge source files."""

    report.info(ctx, "package.build", "building package")
    ctx.run("poetry build")


@invoke.task(pre=[build])
def check(ctx):
    """Check built package is valid."""

    check_command = f"twine check {ctx.directory!s}/dist/*"
    report.info(ctx, "package.check", "checking package")
    ctx.run(check_command)


@invoke.task
def stub(ctx):
    """Generate typing stubs for the package."""

    report.info(ctx, "package.stub", "generating typing stubs for package")
    ctx.run(
        f"stubgen --include-private --no-import "
        f"--output {ctx.directory.joinpath('stubs')!s} "
        f"{ctx.package.directory!s}"
    )


@invoke.task(pre=[stub])
def typecheck(ctx):
    """Run type checking with generated package stubs."""

    report.info(ctx, "package.typecheck", "typechecking package")
    ctx.run(f"mypy {ctx.package.directory!s}")
