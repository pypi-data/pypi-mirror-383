import re
import subprocess
from collections.abc import Iterable
from pathlib import Path

import umu_commander.configuration as config


def _natural_sort_proton_ver_key(p: Path, _nsre=re.compile(r"(\d+)")):
    s: str = p.name
    return [int(text) if text.isdigit() else text for text in _nsre.split(s)]


def refresh_proton_versions():
    print("Updating umu Proton.")
    umu_update_process = subprocess.run(
        ["umu-run", '""'],
        env={"PROTONPATH": "UMU-Latest", "UMU_LOG": "debug"},
        capture_output=True,
        text=True,
    )

    for line in umu_update_process.stderr.split("\n"):
        if "PROTONPATH" in line and "/" in line:
            try:
                left: int = line.rfind("/") + 1
                print(f"Latest UMU-Proton: {line[left:len(line) - 1]}.")
            except ValueError:
                print("Could not fetch latest UMU-Proton.")

            break


def collect_proton_versions(sort: bool = False) -> dict[Path, Iterable[Path]]:
    versions: dict[Path, Iterable[Path]] = {}
    for proton_dir in config.PROTON_PATHS:
        dir_versions = [version for version in proton_dir.iterdir() if version.is_dir()]
        if len(dir_versions) == 0:
            continue
        else:
            versions[proton_dir] = dir_versions

        if sort:
            versions[proton_dir] = sorted(
                versions[proton_dir], key=_natural_sort_proton_ver_key, reverse=True
            )

    return versions


def get_latest_umu_proton() -> Path | None:
    umu_proton_versions: list[Path] = [
        config.UMU_PROTON_PATH / proton_ver
        for proton_ver in config.UMU_PROTON_PATH.iterdir()
        if "UMU" in proton_ver.name and (config.UMU_PROTON_PATH / proton_ver).is_dir()
    ]

    if len(umu_proton_versions) == 0:
        return None

    umu_proton_versions = sorted(
        umu_proton_versions, key=_natural_sort_proton_ver_key, reverse=True
    )

    return umu_proton_versions[0]
