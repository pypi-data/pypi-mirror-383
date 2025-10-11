from collections.abc import Iterable
from pathlib import Path

from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from umu_commander import VERSION
from umu_commander import database as db
from umu_commander.classes import Element


def count_users(proton_dir: Path, proton_ver: Path) -> str:
    return (
        f"({len(db.get(proton_dir, proton_ver))})"
        if proton_ver in db.get(proton_dir)
        else "(-)"
    )


def build_choices(
    elements: Iterable[Path | Element] | None,
    groups: dict[Path | Element, Iterable[Path | Element]] | None,
    *,
    count_elements: bool = False,
) -> list[Separator | Choice | str]:
    if elements is None:
        elements = []

    if groups is None:
        groups = {}

    choices: list[Choice | Separator] = [Choice(el, name=el.name) for el in elements]
    if len(choices) > 0:
        choices.append(Separator(""))

    for group, elements in groups.items():
        choices.extend(
            [
                Separator(f"In: {group}"),
                *[
                    Choice(
                        el,
                        name=(
                            el.name
                            if not count_elements
                            else f"{el.name} {count_users(group, el)}"
                        ),
                    )
                    for el in elements
                ],
                Separator(""),
            ]
        )

    return choices


def print_help():
    print(
        f"umu-commander {VERSION}",
        "Interactive CLI tool to augment umu-launcher as well as help you manage its Proton versions.",
        "",
        "For details, usage, and more, see the README.md file, or visit https://github.com/Mpaxlamitsounas/umu-commander.",
        sep="\n",
    )
