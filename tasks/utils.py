# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains Invoke utilities."""

import colorama
from towncrier._builder import find_fragments, split_fragments, render_fragments
from towncrier._settings import load_config

colorama.init()
fg = colorama.Fore
bg = colorama.Back
sty = colorama.Style
reset = colorama.Style.RESET_ALL


class report(object):
    """Quick-n-dirty console reporting."""

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
        """Log an info-level console message."""

        print(cls._get_text(ctx, "info", task_name, text))

    @classmethod
    def debug(cls, ctx, task_name, text):
        """Log an debug-level console message."""

        print(cls._get_text(ctx, "debug", task_name, text))

    @classmethod
    def warning(cls, ctx, task_name, text):
        """Log an warning-level console message."""

        print(cls._get_text(ctx, "warning", task_name, text))

    @classmethod
    def warn(cls, ctx, task_name, text):
        """Log an warning-level console message."""

        cls.warning(ctx, task_name, text)

    @classmethod
    def error(cls, ctx, task_name, text):
        """Log an error-level console message."""

        print(cls._get_text(ctx, "error", task_name, text))

    @classmethod
    def success(cls, ctx, task_name, text):
        """Log an success-level console message."""

        print(cls._get_text(ctx, "success", task_name, text))
