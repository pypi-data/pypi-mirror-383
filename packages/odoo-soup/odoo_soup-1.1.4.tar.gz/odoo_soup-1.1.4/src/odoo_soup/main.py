import click
from .utils import (
    init,
    scan_log_files,
    print_list_tuple,
    d_print,
    has_custom_configs,
    list_versions,
    init_dirs,
    reset_config,
)
from .compiler import parse_config
from .converter import convert_to_sql
from . import config

from magicprompt import prompt
import subprocess
import os
import gzip
import shutil


@click.group()
def soup():
    pass


@soup.command()
def nuke():
    """
    Delete the 'odoo-soup' DB (deletes ALL imported log tables)
    """
    if click.confirm(
        "Are you sure? This will delete ALL imported logs within 'odoo-soup' DB"
    ):
        click.echo("-> Nuking 'odoo-soup'...")
        try:
            subprocess.run(
                "dropdb odoo-soup",
                shell=True,
                check=True,
                text=True,
            )
            click.echo("   Done!")
        except:
            raise Exception(
                "Could not drop 'odoo-soup'. It either doesn't exist or there are connections to it which must be closed."
            )


@soup.command()
def edit():
    """
    Open soup config in nano
    """
    init_dirs(False)
    click.edit(filename=config.CONFIG_PATH)


@soup.command()
def show():
    """
    Show soup config path
    """
    init_dirs(False)
    click.echo(config.CONFIG_PATH)


@soup.command()
def reset():
    """
    Reset soup config file
    """
    reset_config()


@soup.command()
@click.option(
    "--keep",
    is_flag=True,
    help="Keep the original file alongside compressed output",
)
@click.argument("file")
def zip(keep, file):
    """
    Convert a plaintext log to .gz for import
    """
    file_path = os.path.join(os.getcwd(), file)

    # Check that the file exists
    if os.path.exists(file_path):
        # Check that it is not .gz
        if file_path[-3:] == ".gz":
            raise TypeError(f"File {file_path} is already .gz archive")

        # Make the archive
        click.echo(f"-> Compressing {file}...")
        with open(file_path, "rb") as f:
            with gzip.open(f"{file_path}.gz", "wb") as f_out:
                shutil.copyfileobj(f, f_out)

        # Remove original by default
        if not keep:
            os.remove(file_path)

        click.echo(f"   Done: {file}.gz")

        return file_path + ".gz"

    else:
        raise FileNotFoundError(f"File {file_path} does not exist!")


@soup.command()
@click.option(
    "--keep",
    is_flag=True,
    help="Keep the original file alongside uncompressed output",
)
@click.argument("file")
def unzip(keep, file):
    """
    Convert a .gz log to plaintext
    """
    file_path = os.path.join(os.getcwd(), file)

    # Check that the file exists
    if os.path.exists(file_path):
        # Check that it is not .gz
        if file_path[-3:] == ".gz":
            # Make the archive
            click.echo(f"-> Decompressing {file}...")
            with gzip.open(file_path, "rb") as f:
                with open(file_path[:-3], "wb") as f_out:
                    shutil.copyfileobj(f, f_out)

            # Remove original by default
            if not keep:
                os.remove(file_path)

            click.echo(f"   Done: {file[:-3]}")

            return file_path[:-3]

        else:
            raise TypeError(f"File {file_path} is not a .gz archive")

    else:
        raise FileNotFoundError(f"File {file_path} does not exist!")


@soup.command()
@click.option(
    "--nozip",
    is_flag=True,
    help="Skip converting filtered file to .gz",
)
@click.argument("file")
@click.argument("database")
def filter(nozip, file, database):
    """
    Filter a SAAS log to a specific Odoo database
    """
    file_path = os.path.join(os.getcwd(), file)

    # Check that the file exists
    if os.path.exists(file_path):
        # If it is compressed, extract the file
        if file_path[-3:] == ".gz":
            file_path = unzip.callback(True, file)
            file = file[:-3]

        click.echo("-> Filtering...")
        r = subprocess.run(
            f"grep '{database}' {file_path} >> {file_path}.filtered",
            shell=True,
            text=True,
        )

        if r.returncode > 1:
            raise Exception("Could not filter that file. Idk bro.")

        # Zip the new filtered file for import
        if not nozip:
            zip.callback(False, file + ".filtered")

        else:
            click.echo(f"   Done: {file}.filtered")


# @click.option(
#     "--dirty",
#     is_flag=True,
#     help="Include ALL unconfigured line types as text records",
# )
@soup.command()
@click.argument("table")
def make(table):
    """
    Convert a .gz logfile to SQL table
    """

    # Init/check the dirs and db
    init(table)

    # Get the log files from CWD
    log_files = scan_log_files()

    click.clear()

    # USER SELECTS LOGFILE
    click.echo("Log files in current directory:\n")
    numFiles = print_list_tuple(log_files)

    resp = (
        prompt(
            "Select a logfile to convert",
            numOnly=1,
            clearAfterResponse=1,
            validators=[lambda x: 0 < int(x) <= numFiles],
        )
        - 1
    )
    click.clear()

    d_print(f"resp: {resp}")
    d_print(f"config: {config.get_config()}")

    # USER SELECTS CUSTOM CONFIG
    if has_custom_configs():
        options = list_versions()

        vers = prompt(
            "Choose a configuration (ENTER for default)",
            capPrompt=False,
            castAnswer=False,
            notEmpty=False,
            clearAfterResponse=1,
            validators=[lambda x: x in options or x == ""],
        )

        version = options.get(vers, "default")
    else:
        version = "default"

    # APP GO BRRR
    click.echo(f"Converting {log_files[resp][0]} to SQL table...\n")

    # Compile mapping
    config.set_mapping(parse_config(version))
    d_print(f"compiled mapping: {config.MAPPING}")

    # Convert to sql
    skipped, stats = convert_to_sql(log_files[resp][1])

    click.clear()
    click.echo(
        f"Success! Created table: {config.TABLE_NAME} in DB: odoo-soup ({int(stats['time'] * 1000) / 1000.0} s)\n"
    )

    d_print(
        f"File length: {stats['raw_length']} | Traceback/junk lines: {stats['junk_skipped']} | Imported log lines: {stats['table_len']}"
    )

    click.echo(
        "The following line types were skipped due to not being present in your config (sorted by freq):"
    )

    for s in skipped:
        click.echo(f"  {s}")

    click.echo(
        f"\nTotal lines skipped: {stats['log_lines_skipped']} ({100.0 - (int((stats['log_lines_skipped'] / (stats['table_len'] - stats['junk_skipped'])) * 10000) / 100.0)}% coverage)"
    )


if __name__ == "__main__":
    soup()
