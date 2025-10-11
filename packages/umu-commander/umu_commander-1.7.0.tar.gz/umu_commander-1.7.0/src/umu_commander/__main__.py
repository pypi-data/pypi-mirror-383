import sys
from json import JSONDecodeError
from pathlib import Path

from InquirerPy.exceptions import InvalidArgument

from umu_commander import configuration as config
from umu_commander import database as db
from umu_commander import tracking, umu_config
from umu_commander.classes import ExitCode
from umu_commander.configuration import CONFIG_DIR, CONFIG_NAME
from umu_commander.util import print_help


def init() -> ExitCode:
    try:
        config.load()

    except (JSONDecodeError, KeyError):
        config_path: Path = CONFIG_DIR / CONFIG_NAME
        config_path_old: Path = CONFIG_DIR / (str(CONFIG_NAME) + ".old")

        print(f"Config file at {config_path} could not be read.")

        if not config_path_old.exists():
            print(f"Config file renamed to {config_path_old}.")
            config_path.rename(config_path_old)

        return ExitCode.DECODING_ERROR

    except FileNotFoundError:
        config.dump()

    try:
        db.load()

    except JSONDecodeError:
        db_path: Path = config.DB_DIR / config.DB_NAME
        db_path_old: Path = config.DB_DIR / (str(config.DB_NAME) + ".old")

        print(f"Tracking file at {db_path} could not be read.")

        if not db_path_old.exists():
            db_path.rename(db_path_old)
            print(f"DB file renamed to {db_path_old}.")

    except FileNotFoundError:
        pass

    return ExitCode.SUCCESS


def main() -> int:
    if (return_code := init()) != ExitCode.SUCCESS:
        return return_code.value

    try:
        match sys.argv[1]:
            case "track":
                tracking.track(),
            case "untrack":
                tracking.untrack(),
            case "users":
                tracking.users(),
            case "delete":
                tracking.delete(),
            case "create":
                umu_config.create({"umu": {}, "env": {}}, True),
            case "run":
                umu_config.run(),
            case _:
                print("Unrecognised verb.")
                print_help()
                return ExitCode.INVALID_SELECTION.value

    except IndexError:
        print_help()
        return ExitCode.SUCCESS.value

    except InvalidArgument:
        print("No choices to select from.")
        return ExitCode.INVALID_SELECTION.value

    else:
        return ExitCode.SUCCESS.value

    finally:
        tracking.untrack_unlinked()
        db.dump()


if __name__ == "__main__":
    exit(main())
