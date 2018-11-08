# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import re
import shutil

import invoke
import parver

from .utils import report, get_previous_version


@invoke.task
def clean(ctx):
    """ Clean previously built package artifacts.
    """

    clean_command = "python setup.py clean"
    report.info(ctx, "package.clean", "cleaning up built package artifacts")
    ctx.run(clean_command)

    egg_name = f"{ctx.metadata['package_name']}.egg-info"
    report.info(ctx, "pacakge.clean", "removing build directories")
    for artifact in ("dist", "build", egg_name, f"src/{egg_name}"):
        artifact_dir = ctx.directory / artifact
        if artifact_dir.is_dir():
            report.debug(ctx, "package.clean", f"removing directory {artifact_dir!r}")
            ctx.run(f"rm -rf {artifact_dir!s}")


@invoke.task
def format(ctx):
    """ Auto format package source files.
    """

    isort_command = f"isort -rc {ctx.package.directory!s}"
    black_command = f"black {ctx.package.directory.parent!s}"

    report.info(ctx, "package.format", "sorting imports")
    ctx.run(isort_command)
    report.info(ctx, "package.format", "formatting code")
    ctx.run(black_command)


@invoke.task(pre=[clean, format])
def build(ctx):
    """ Build pacakge source files.
    """

    build_command = "python setup.py sdist bdist_wheel"
    report.info(ctx, "package.build", "building package")
    ctx.run(build_command)


@invoke.task
def version(ctx, version=None, force=False):
    """ Specify a new version for the package.

    .. important:: If no version is specified, will take the most recent parsable git
        tag and bump the patch number.

    :param str version: The new version of the package.
    :param bool force: If True, skips version check
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
        if not force and version <= previous_version:
            error_message = (
                f"version {version!s} is <= to previous version {previous_version!s}"
            )
            report.error(ctx, "package.version", error_message)
            raise ValueError(error_message)
    else:
        version = previous_version.bump_release(len(previous_version.release) - 1)

    report.info(ctx, "package.version", f"updating version to {version!s}")
    for (path, replacements) in updates.items():
        if path.is_file():
            content = path.read_text()
            for (pattern, sub) in replacements:
                report.debug(
                    ctx,
                    "package.version",
                    f"applying replacement ({pattern!r}, {sub!r}) to {path!s}",
                )
                content = re.sub(pattern, sub.format(version=version), content, re.M)
            path.write_text(content)
