# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import re
import shutil

import invoke
import parver

from .utils import get_previous_version


@invoke.task
def clean(ctx):
    """ Clean previously built package artifacts.
    """

    clean_command = "python setup.py clean"
    print(f"[package.clean] ... run {clean_command!r}")
    ctx.run(clean_command, hide=ctx.hide)

    for artifact in ("dist", "build", f"{ctx.metadata['name']}.egg-info"):
        artifact_dir = ctx.directory / artifact
        if artifact_dir.is_dir():
            print(f"[package.clean] ... removing {artifact_dir!s}")
            shutil.rmtree(str(artifact_dir))


@invoke.task
def format(ctx):
    """ Auto format package source files.
    """

    isort_command = f"isort -rc {ctx.package.directory!s}"
    black_command = f"black {ctx.package.directory.parent!s}"

    print(f"[package.format] ... run {isort_command!r}")
    ctx.run(isort_command, hide=ctx.hide)
    print(f"[package.format] ... run {black_command!r}")
    ctx.run(black_command, hide=ctx.hide)


@invoke.task(pre=[clean, format])
def build(ctx):
    """ Build pacakge source files.
    """

    build_command = "python setup.py sdist bdist_wheel"
    print(f"[package.build] ... run {build_command!s}")
    ctx.run(build_command, hide=ctx.hide)


@invoke.task
def version(ctx, version=None):
    """ Specify a new version for the package.

    .. important:: If no version is specified, will take the most recent parsable git
        tag and bump the patch number.

    :param str version: The new version of the package.
    """

    # define replacement strategies for files where the version needs to be in sync
    updates = {
        ctx.directory.joinpath("setup.cfg"): [
            (r"(version\s?=\s?)(.*)", "\\g<1>{version}")
        ],
        ctx.package.directory.joinpath("__version__.py"): [
            (r"(__version__\s?=\s?)(.*)", '\\g<1>"{version}"')
        ],
    }

    previous_version = get_previous_version(ctx)
    if isinstance(version, str):
        version = parver.Version.parse(version)
        if version <= previous_version:
            raise ValueError(
                f"version {version!s} is <= to previous version {previous_version!s}"
            )
    else:
        version = previous_version.bump_release(len(previous_version.release) - 1)

    print(f"[package.version] ... updating version to {version!s}")
    for (path, replacements) in updates.items():
        if path.is_file():
            content = path.read_text()
            for (pattern, sub) in replacements:
                print(
                    f"[package.version] ... applying replacement "
                    f"({pattern!r}, {sub!r}) to {path!s}"
                )
                content = re.sub(pattern, sub.format(version=version), content, re.M)
            path.write_text(content)
