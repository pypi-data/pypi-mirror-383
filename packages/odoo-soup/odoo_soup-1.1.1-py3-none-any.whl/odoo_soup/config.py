import click
import os
import tomllib
from .models import create_log_model
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from datetime import datetime


BASE = declarative_base()

# Identify paths
APP_DIR = click.get_app_dir("odoo_soup")
CONFIG_PATH = os.path.join(APP_DIR, "soups.toml")


CONFIG = None
DEBUG = False
TABLE_MODEL = None
TABLE_NAME = None
MAPPING = None
ENGINE = create_engine("postgresql:///odoo-soup")


def load_config(path: str) -> dict:
    with open(path, "rb") as f:
        # click.echo(f"Parsing config at {path}...")
        try:
            config = tomllib.load(f)
            return config
        except:
            raise Exception(
                f"Error parsing {path}. Verify that there are no configuration typos"
            )


# For lazyloading stuff
def get_config() -> dict:
    global CONFIG

    if CONFIG is None:
        CONFIG = load_config(CONFIG_PATH)

    return CONFIG


def set_table_name(name):
    global TABLE_NAME
    TABLE_NAME = name


def set_mapping(mapping):
    global MAPPING
    MAPPING = mapping


def get_mapping():
    global MAPPING
    return MAPPING


def get_table_model():
    global TABLE_MODEL

    if TABLE_MODEL is None:
        TABLE_MODEL = create_log_model(TABLE_NAME, BASE)

    return TABLE_MODEL


TYPES = {
    "date": datetime,
    "level": str,
    "origin": str,
    "ip": str,
    "http": str,
    "route": str,
    "code": int,
    "time": float,
    "user": str,
    "object": str,
    "records": str,
    "text": str,
}
