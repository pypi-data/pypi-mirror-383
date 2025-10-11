import importlib
import os
import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from umu_commander.classes import Element

CONFIG_DIR: Path = Path.home() / ".config"
CONFIG_NAME: Path = Path("umu-commander.toml")


PROTON_PATHS: tuple[Path, ...] = (
    Path.home() / ".local/share/Steam/compatibilitytools.d/",
    Path.home() / ".local/share/umu/compatibilitytools",
)
UMU_PROTON_PATH: Path = Path(Path.home() / ".local/share/Steam/compatibilitytools.d")

DB_NAME: Path = Path("tracking.json")
DB_DIR: Path = Path.home() / ".local/share/umu/compatibilitytools"
UMU_CONFIG_NAME: Path = Path("umu-config.toml")
DEFAULT_PREFIX_DIR: Path = Path.home() / ".local/share/wineprefixes/"
DLL_OVERRIDES_OPTIONS: tuple[Element, ...] = (
    Element("winhttp.dll=n,b;", "winhttp for BepInEx"),
)
LANG_OVERRIDES_OPTIONS: tuple[Element, ...] = (Element("ja_JP.UTF8", "Japanese"),)

module = importlib.import_module(__name__)


def load():
    with open(os.path.join(CONFIG_DIR, CONFIG_NAME), "rb") as conf_file:
        toml_conf = tomllib.load(conf_file)

        # Proton dirs translation
        setattr(
            module,
            "PROTON_PATHS",
            (Path(proton_dir) for proton_dir in toml_conf["PROTON_PATHS"]),
        )
        del toml_conf["PROTON_PATHS"]

        # DLL/LANG Override translation
        for key in ["DLL", "LANG"]:
            setattr(
                module,
                f"{key}_OVERRIDES_OPTIONS",
                (
                    Element(value, name)
                    for name, value in toml_conf[f"{key}_OVERRIDES_OPTIONS"].items()
                ),
            )
            del toml_conf[f"{key}_OVERRIDES_OPTIONS"]

        for key, value in toml_conf.items():
            setattr(module, key, Path(value))


def _get_attributes() -> dict[str, Any]:
    attributes: dict[str, Any] = {}
    for key in dir(module):
        value = getattr(module, key)
        if not key.startswith("_") and not callable(value) and key.upper() == key:
            attributes[key] = value

    return attributes


def dump():
    if not os.path.exists(CONFIG_DIR):
        os.mkdir(CONFIG_DIR)

    with open(os.path.join(CONFIG_DIR, CONFIG_NAME), "wb") as conf_file:
        toml_conf = _get_attributes()
        del toml_conf["CONFIG_DIR"]
        del toml_conf["CONFIG_NAME"]

        for key, value in toml_conf.items():
            match key:
                case "PROTON_PATHS":
                    toml_conf[key] = [str(proton_dir) for proton_dir in PROTON_PATHS]

                case "DLL_OVERRIDES_OPTIONS" | "LANG_OVERRIDES_OPTIONS":
                    toml_conf[key] = {
                        override.name: override for override in getattr(module, key)
                    }

                case _:
                    toml_conf[key] = str(value)

        tomli_w.dump(toml_conf, conf_file)
