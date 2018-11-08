# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import pathlib
import subprocess

import parver
from towncrier._builder import find_fragments, render_fragments, split_fragments
from towncrier._settings import load_config


def get_previous_version(ctx):
    tags = [
        tag.strip()
        for tag in subprocess.check_output(["git", "tag"], encoding="ascii").split("\n")
    ]
    try:
        version = max(parver.Version.parse(ver).normalize() for ver in tags if ver)
    except ValueError:
        version = parver.Version.parse("0.0.0")
    return version


def get_tag_content(ctx):
    config = load_config(ctx.directory.as_posix())
    definitions = config["types"]

    (fragments, fragment_filenames) = find_fragments(
        pathlib.Path(config["directory"]).absolute(),
        config["sections"],
        None,
        definitions,
    )

    return render_fragments(
        pathlib.Path(config["template"]).read_text(encoding="utf-8"),
        config["issue_format"],
        split_fragments(fragments, definitions),
        definitions,
        config["underlines"][1:],
        False,  # don't add newlines to wrapped text
    )


def get_artifact_paths(ctx):
    artifact_glob = f"{ctx.metadata['name'].replace('name', '[-_]')}-*"
    return [
        ctx.directory.joinpath(_) for _ in (ctx.directory / "dist").glob(artifact_glob)
    ]
