import json
from collections import defaultdict
from pathlib import Path

import umu_commander.configuration as config

_db: defaultdict[Path, defaultdict[Path, list[Path]]] = defaultdict(
    lambda: defaultdict(list)
)


def load():
    global _db

    if not config.DB_DIR.exists():
        config.DB_DIR.mkdir()

    with open(config.DB_DIR / config.DB_NAME, "rt") as db_file:
        db: dict[Path, dict[Path, list[Path]]] = {}
        for proton_dir, proton_vers in json.load(db_file).items():
            proton_dir = Path(proton_dir)
            db[proton_dir] = {}
            for proton_ver, proton_users in proton_vers.items():
                proton_ver = proton_dir / proton_ver
                db[proton_dir][proton_ver] = [Path(user) for user in proton_users]
        # noinspection PyTypeChecker
        _db.update(db)


def dump():
    if not config.DB_DIR.exists():
        config.DB_DIR.mkdir()

    db: dict[str, dict[str, list[str]]] = {}
    for proton_dir, proton_vers in _db.items():
        proton_dir = str(proton_dir)
        db[proton_dir] = {}
        for proton_ver, proton_users in proton_vers.items():
            proton_ver = proton_ver.name
            db[proton_dir][proton_ver] = [str(user) for user in proton_users]

    with open(config.DB_DIR / config.DB_NAME, "wt") as db_file:
        # noinspection PyTypeChecker
        json.dump(db, db_file, indent="\t")


def get(
    proton_dir: Path = None, proton_ver: Path = None
) -> dict[Path, dict[Path, list[Path]]] | dict[Path, list[Path]] | list[Path]:
    global _db

    if proton_dir is None and proton_ver is None:
        return _db

    if proton_ver is None:
        return _db[proton_dir]

    if proton_ver not in _db[proton_dir]:
        _db[proton_dir][proton_ver] = []

    return _db[proton_dir][proton_ver]


def _reset():
    global _db
    _db = defaultdict(lambda: defaultdict(list))
