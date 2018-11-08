# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import pathlib
import configparser

import invoke
import parver

from . import docs, package
from .utils import get_previous_version, get_tag_content, get_artifact_paths

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

# parse setup.cfg to gather metadata info (reduce redundancy of static info)
config = configparser.ConfigParser()
config.read(BASE_DIR.joinpath("setup.cfg").as_posix())

try:
    metadata = config["metadata"]
except KeyError:
    raise KeyError(
        f"cannot run invoke tasks if setup.cfg is missing [metadata] section"
    )


@invoke.task(post=[docs.build, package.build])
def build(ctx):
    """ Build the project.
    """

    print(f"[build] ... building project {ctx.directory!s}")


@invoke.task(post=[package.clean, docs.clean])
def clean(ctx):
    """ Clean the project.
    """

    print(f"[clean] ... cleaning project {ctx.directory!s}")


@invoke.task(pre=[clean, build])
def publish(ctx, test=False):
    """ Publish the project.

    :param bool test: Publishes to PyPi test server (defaults to False)
    """

    previous_version = get_previous_version(ctx)
    current_version = parver.Version.parse(metadata["version"])

    if current_version <= previous_version:
        raise ValueError(
            f"current version ({current_version!s}) is <= to previous version "
            f"({previous_version!s}), use 'package.version' to update current version"
        )

    print(f"[publish] ... publishing project {ctx.directory!s}")
    git_ammend_command = f"git commit -am 'Release {current_version!s}'"
    print(f"[publish] ... run {git_ammend_command!r}")
    # ctx.run(git_ammend_command, hide=ctx.hide)

    tag_content = get_tag_content(ctx).replace('"', '\\"')
    git_tag_command = (
        f'git tag -a "{current_version!s}" -m '
        f'"Version {current_version!s}\n\n{tag_content}"'
    )
    print(f"[publish] ... run {git_tag_command!r}")
    # ctx.run(git_tag_command, hide=ctx.hide)

    artifact_paths = [f"{_.as_posix()!r}" for _ in get_artifact_paths(ctx)]
    publish_command = f"twine upload {' '.join(artifact_paths)}"
    if test:
        publish_command += " --repository 'https://test.pypi.org/legacy/'"
    print(f"[publish] ... run {publish_command!r}")

    # get user to confirm publish
    try:
        input(
            f"[publish] ... about to publish, [ENTER] to confirm, [CTRL-C] to abort: "
        )
    except KeyboardInterrupt:
        print("[publish] ... aborting publish")
        # TODO: cleanup git stuff

    # ctx.run(publish_command, hide=ctx.hide)

    git_push_command = "git push --tags"
    print(f"[publish] ... run {git_push_command!r}")
    # ctx.run(git_push_command, hide=ctx.hide)


namespace = invoke.Collection(build, clean, publish, docs, package)
package_name = metadata["name"].replace("-", "_")
namespace.configure(
    {
        "metadata": metadata,
        "directory": BASE_DIR,
        "hide": None,
        "package": {"directory": BASE_DIR / "src" / package_name},
        "docs": {"directory": BASE_DIR / "docs"},
    }
)
