# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains Invoke task functions for documentation building."""

import webbrowser
from urllib.request import pathname2url

import invoke

from .utils import report


@invoke.task
def clean(ctx):
    """Clean built docs."""

    with ctx.cd(ctx.docs.directory.as_posix()):
        report.info(ctx, "docs.clean", "cleaning documentation artifacts")
        ctx.run("make clean")


@invoke.task
def build_news(ctx, draft=False, yes=False):
    """Build towncrier newsfragments."""

    report.info(ctx, "docs.build-news", "building changelog from news fragments")
    build_command = f"towncrier --version {ctx.metadata['version']}"
    if draft:
        report.warn(
            ctx,
            "docs.build-news",
            "building changelog as draft (results are written to stdout)",
        )
        build_command += " --draft"
    elif yes:
        report.warn(
            ctx, "docs.build-news", "removing news files without user confirmation (-y)"
        )
        build_command += " --yes"
    ctx.run(build_command, hide=None)


@invoke.task()
def build(ctx, output="html"):
    """Build docs."""

    with ctx.cd(ctx.docs.directory.as_posix()):
        build_command = f"make {output}"
        report.info(ctx, "docs.build", f"building {output!r} documentation")
        ctx.run(build_command)


@invoke.task(pre=[build])
def view(ctx):
    """Build and view docs."""

    report.info(ctx, "docs.view", "viewing documentation")
    build_path = ctx.docs.directory / "build" / "html" / "index.html"
    build_path = pathname2url(build_path.as_posix())
    webbrowser.open(f"file:{build_path!s}")
