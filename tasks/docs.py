# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import pathlib

import invoke


@invoke.task
def clean(ctx):
    """ Clean built docs.
    """

    clean_command = f"make clean"
    with ctx.cd(ctx.docs.directory.as_posix()):
        print(f"[docs.clean] ... run {clean_command!r}")
        ctx.run(clean_command, hide=ctx.hide)


@invoke.task
def build_news(ctx, draft=False):
    """ Build towncrier newsfragments.
    """

    build_command = f"towncrier --version {ctx.metadata['version']}"
    if draft:
        build_command += " --draft"
    print(f"[docs.build-news] ... run {build_command!r}")
    ctx.run(build_command, hide=None)


@invoke.task(pre=[clean, build_news])
def build(ctx, output="html"):
    """ Build docs.
    """

    with ctx.cd(ctx.docs.directory.as_posix()):
        build_command = f"make {output}"
        print(f"[docs.build] ... run {build_command!r}")
        ctx.run(build_command, hide=ctx.hide)
