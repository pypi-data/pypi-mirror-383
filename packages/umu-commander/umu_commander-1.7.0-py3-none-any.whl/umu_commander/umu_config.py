import os
import subprocess
import tomllib
from pathlib import Path
from typing import Any

import tomli_w
from InquirerPy import inquirer

import umu_commander.configuration as config
from umu_commander import tracking
from umu_commander.classes import Element
from umu_commander.configuration import DLL_OVERRIDES_OPTIONS, LANG_OVERRIDES_OPTIONS
from umu_commander.proton import (
    collect_proton_versions,
    get_latest_umu_proton,
    refresh_proton_versions,
)
from umu_commander.util import build_choices


def select_prefix() -> str:
    default = Element(str(Path.cwd() / "prefix"), "Current directory")
    choices = build_choices([default, *config.DEFAULT_PREFIX_DIR.iterdir()], None)
    return str(inquirer.select("Select wine prefix:", choices, default).execute())


def select_proton() -> str:
    default = Element(str(get_latest_umu_proton()), "Latest UMU-Proton")
    choices = build_choices([default], collect_proton_versions(sort=True))
    return str(
        inquirer.select(
            "Select Proton version:", choices, Path.cwd() / "prefix"
        ).execute()
    )


def select_dll_override() -> str:
    choices = build_choices(DLL_OVERRIDES_OPTIONS, None)
    return "".join(
        [
            selection
            for selection in inquirer.checkbox(
                "Select DLLs to override:", choices
            ).execute()
        ]
    )


def select_lang() -> str:
    default = Element("", "No override")
    choices = build_choices([default, *LANG_OVERRIDES_OPTIONS], None)
    return inquirer.select("Select locale:", choices, default).execute()


def set_launch_args() -> list[str]:
    options: str = inquirer.text(
        "Enter executable options, separated by space:"
    ).execute()
    return [opt.strip() for opt in options.split(" ")]


def select_exe() -> str:
    files = [file for file in Path.cwd().iterdir() if file.is_file()]
    choices = build_choices(files, None)
    return str(inquirer.select("Select game executable:", choices).execute())


def create(params: dict[str, dict[str, Any]], interactive: bool):
    refresh_proton_versions()

    # Prefix selection
    if params.get("umu").get("prefix") is None:
        if interactive:
            params["umu"]["prefix"] = select_prefix()
        else:
            params["umu"]["prefix"] = str(Path.cwd() / "prefix")

    # Proton selection
    if params.get("umu").get("proton") is None:
        if interactive:
            params["umu"]["proton"] = select_proton()
        else:
            params["umu"]["proton"] = str(get_latest_umu_proton())

    selected_umu_latest: bool = params["umu"]["proton"] == str(get_latest_umu_proton())

    # Select DLL overrides
    if interactive:
        params["env"]["WINEDLLOVERRIDES"] = select_dll_override()
        print(params["env"]["WINEDLLOVERRIDES"])

    # Set language locale
    if interactive:
        if (lang := select_lang()) != "":
            params["env"]["LANG"] = lang

    # Input executable launch args
    if interactive:
        params["umu"]["launch_args"] = set_launch_args()

    # Select executable name
    if params["umu"].get("exe") is None:
        params["umu"]["exe"] = select_exe()

    try:
        with open(config.UMU_CONFIG_NAME, "wb") as file:
            tomli_w.dump(params, file)

        print(f"Configuration file {config.UMU_CONFIG_NAME} created at {os.getcwd()}.")
        print(f"Use by running umu-commander run.")
        if not selected_umu_latest:
            tracking.track(
                Path(params["umu"]["proton"], Path(params["umu"]["exe"])).parent,
                refresh_versions=False,
            )
    except:
        print("Could not create configuration file.")


def run():
    if not config.UMU_CONFIG_NAME.exists():
        print("No umu config in current directory.")
        return

    with open(config.UMU_CONFIG_NAME, "rb") as toml_file:
        toml_conf = tomllib.load(toml_file)

        prefix_path = Path(toml_conf["umu"]["prefix"])
        if not prefix_path.exists():
            prefix_path.mkdir()

        os.environ.update(toml_conf.get("env", {}))
        subprocess.run(
            args=["umu-run", "--config", config.UMU_CONFIG_NAME],
            env=os.environ,
        )
