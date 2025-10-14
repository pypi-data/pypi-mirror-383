from .config import CONFIG_PATH, APP_DIR, set_table_name, DEBUG, get_config
import click
import os
import shutil
import importlib.resources
from datetime import datetime
import subprocess


def d_print(string: str) -> None:
    # Print if debug mode enabled

    if DEBUG:
        click.echo(f"DEBUG: {string}")


def hide_cursor():
    print("\033[?25l", end="")


def show_cursor():
    print("\033[?25h", end="")


def has_custom_configs() -> bool:
    if get_config():
        d_print(f"config len: {len(get_config())}")
        return len(get_config()) > 1
    else:
        raise Exception("Config not found!")


def list_versions():
    # Clean this up later whatever
    config_map = {}
    i = 1
    if len(get_config()) > 1:
        print(f"({len(get_config()) - 1}) custom configs detected:")
        for v in get_config():
            if v != "default":
                config_map[str(i)] = v
                print(f"  {i}:  {v}")
                i += 1
        return config_map

    return None


def reset_config():
    # Check if config exists yet
    os.makedirs(APP_DIR, exist_ok=True)

    if os.path.exists(APP_DIR) and os.path.exists(CONFIG_PATH):
        default_config = importlib.resources.files("odoo_soup").joinpath(
            "default_soups.toml"
        )

        with importlib.resources.as_file(default_config) as conf:
            shutil.copyfile(conf, CONFIG_PATH)

        click.echo(f"Replaced {CONFIG_PATH}")

    else:
        # If theres no config file there just make one instead
        init_dirs(False)


def init_dirs(show=True):
    # Make app dir
    os.makedirs(APP_DIR, exist_ok=True)

    # Check if config exists yet
    if os.path.exists(APP_DIR) and os.path.exists(CONFIG_PATH):
        if show:
            click.echo(f"-> Using config file: {CONFIG_PATH}")

    else:
        if show:
            click.echo(f"No config file found at {CONFIG_PATH}, creating now...")

        default_config = importlib.resources.files("odoo_soup").joinpath(
            "default_soups.toml"
        )

        with importlib.resources.as_file(default_config) as conf:
            shutil.copyfile(conf, CONFIG_PATH)

        click.echo(f"Created {CONFIG_PATH}")


def db_exists():
    r = subprocess.run(
        "psql -lqt | cut -d \\| -f 1 | grep -qw 'odoo-soup'",
        shell=True,
        check=False,
        capture_output=True,
        text=True,
    )
    return not r.returncode


def create_db():
    click.echo("-> Database 'odoo-soup' does not exist. Creating it now...")
    subprocess.run(
        "createdb odoo-soup",
        shell=True,
        check=True,
        text=True,
    )


def init(table):
    # Init/check config and app dir in place
    init_dirs()

    # Forward tablename arg to config
    set_table_name(table)

    # Check if the odoo-soup db is made
    if not db_exists():
        create_db()


def scan_log_files() -> list[str]:
    # Read through the provided directory
    # Find any .gz files
    files = []

    for entry in os.scandir(os.getcwd()):
        if entry.is_file():
            # Identify if it is of a type we care about
            ext = entry.name.split(".")
            ext = ext[len(ext) - 1]

            if ext == "gz":
                # Add name and path to files list
                files.append((entry.name, entry.path))

    # Break if there were no files found
    if not len(files):
        raise FileNotFoundError(
            "No .gz logfiles were found in CWD! Make sure you run this in the folder where your logs are"
        )
    return files


def print_list_tuple(lt: list[tuple]) -> int:
    # Prints a list of numbered options and returns length
    for i in range(len(lt)):
        click.echo(f"  {i + 1}: {lt[i][0]}")

    click.echo()
    return len(lt)
