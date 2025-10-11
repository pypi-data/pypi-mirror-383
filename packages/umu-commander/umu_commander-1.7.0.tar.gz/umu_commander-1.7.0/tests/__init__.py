import os
import shutil
import sys
from pathlib import Path

TESTING_DIR: Path = Path(os.curdir + "testing").absolute()
PROTON_DIR_1: Path = Path(TESTING_DIR / "proton_dir_1")
PROTON_DIR_2: Path = Path(TESTING_DIR / "proton_dir_2")
USER_DIR: Path = Path(TESTING_DIR / "user_dir")

PROTON_BIG: Path = PROTON_DIR_1 / "UMU_Proton_10"
PROTON_SMALL: Path = PROTON_DIR_1 / "UMU_Proton_1"

sys.path.insert(1, os.path.join(os.path.abspath(os.curdir), "src"))


def teardown():
    shutil.rmtree(TESTING_DIR)


def setup():
    if TESTING_DIR.exists():
        teardown()

    TESTING_DIR.mkdir()
    PROTON_DIR_1.mkdir()
    PROTON_BIG.mkdir()
    PROTON_SMALL.mkdir()
    PROTON_DIR_2.mkdir()
    USER_DIR.mkdir()
