# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import pathlib

import invoke

from .utils import report


@invoke.task
def clean(ctx):
    """ Clean built docs.
    """

    clean_command = f"make clean"
    with ctx.cd(ctx.docs.directory.as_posix()):
        report.info(ctx, "docs.clean", "cleaning documentation artifacts")
        ctx.run(clean_command)


@invoke.task
def build_news(ctx, draft=False):
    """ Build towncrier newsfragments.
    """

    report.info(ctx, "docs.build-news", "building changelog from news fragments")
    build_command = f"towncrier --version {ctx.metadata['version']}"
    if draft:
        report.warn(
            ctx,
            "docs.build-news",
            "building changelog as draft (results are written to stdout)",
        )
        build_command += " --draft"
    ctx.run(build_command, hide=None)


@invoke.task(pre=[clean])
def build(ctx, output="html"):
    """ Build docs.
    """

    with ctx.cd(ctx.docs.directory.as_posix()):
        build_command = f"make {output}"
        report.info(ctx, "docs.build", f"building {output!r} documentation")
        ctx.run(build_command)
