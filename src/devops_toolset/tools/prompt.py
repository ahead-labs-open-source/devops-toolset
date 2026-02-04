"""Minimal prompting helpers.

This module replaces the previous dependency on `clint.textui.prompt`.
It is intentionally small, dependency-free, and safe to import in CI.
"""

from __future__ import annotations

import sys


def yn(question: str, default: bool | None = True) -> bool:
    """Ask a yes/no question and return the user's answer.

    Args:
        question: Prompt text.
        default: Value used when running non-interactively or when the user
            presses Enter without typing an answer. If None, the user will be
            prompted until a valid answer is provided (interactive only).

    Returns:
        True for yes, False for no.
    """

    if not sys.stdin or not sys.stdin.isatty():
        return bool(default)

    if default is True:
        suffix = " [Y/n]"
    elif default is False:
        suffix = " [y/N]"
    else:
        suffix = " [y/n]"

    while True:
        answer = input(f"{question}{suffix} ").strip().lower()

        if not answer:
            if default is None:
                continue
            return bool(default)

        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False

        print("Please answer 'y' or 'n'.")
