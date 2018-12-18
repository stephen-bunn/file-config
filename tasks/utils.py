# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import getpass
import pathlib
import subprocess

import parver
import colorama
from towncrier._builder import find_fragments, split_fragments, render_fragments
from towncrier._settings import load_config

colorama.init()
fg = colorama.Fore
bg = colorama.Back
sty = colorama.Style
reset = colorama.Style.RESET_ALL


class report(object):

    fg = colorama.Fore
    bg = colorama.Back
    sty = colorama.Style
    reset = colorama.Style.RESET_ALL
    level_colors = dict(
        info=dict(task=[sty.BRIGHT, fg.CYAN], text=[fg.BLUE]),
        debug=dict(task=[sty.BRIGHT], text=[sty.DIM]),
        warning=dict(task=[sty.BRIGHT, fg.YELLOW], text=[sty.DIM, fg.WHITE]),
        error=dict(task=[sty.BRIGHT, fg.RED], text=[fg.RED]),
        success=dict(task=[sty.BRIGHT, fg.GREEN], text=[sty.BRIGHT, fg.WHITE]),
    )

    @classmethod
    def _get_text(cls, ctx, level, task_name, text):
        task_style = "".join(cls.level_colors.get(level, {}).get("task", [fg.GREEN]))
        text_style = "".join(cls.level_colors.get(level, {}).get("text", [fg.CYAN]))

        return (
            f"{task_style}[{task_name}]{reset}"
            f" {sty.DIM}...{sty.RESET_ALL} "
            f"{text_style}{text}{reset}"
        )

    @classmethod
    def info(cls, ctx, task_name, text):
        print(cls._get_text(ctx, "info", task_name, text))

    @classmethod
    def debug(cls, ctx, task_name, text):
        print(cls._get_text(ctx, "debug", task_name, text))

    @classmethod
    def warning(cls, ctx, task_name, text):
        print(cls._get_text(ctx, "warning", task_name, text))

    @classmethod
    def warn(cls, ctx, task_name, text):
        cls.warning(ctx, task_name, text)

    @classmethod
    def error(cls, ctx, task_name, text):
        print(cls._get_text(ctx, "error", task_name, text))

    @classmethod
    def success(cls, ctx, task_name, text):
        print(cls._get_text(ctx, "success", task_name, text))


def get_previous_version(ctx):
    tags = [
        tag.strip()
        for tag in subprocess.check_output(["git", "tag"], encoding="ascii").split("\n")
    ]
    try:
        version = max(parver.Version.parse(ver).normalize() for ver in tags if ver)
    except (ValueError, subprocess.CalledProcessError):
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
    return [ctx.directory.joinpath(_) for _ in (ctx.directory / "dist").iterdir()]


def get_username_password(
    ctx, username_label: str = "Username: ", password_label: str = "Password: "
):
    while True:
        username = input(report._get_text(ctx, "success", "publish", username_label))
        if len(username) <= 0:
            continue
        password = getpass.getpass(
            report._get_text(ctx, "success", "publish", password_label)
        )
        if len(password) <= 0:
            continue
        return (username, password)
