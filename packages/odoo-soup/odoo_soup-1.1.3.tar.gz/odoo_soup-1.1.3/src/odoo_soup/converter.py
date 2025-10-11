from datetime import datetime
from .config import BASE, get_mapping, ENGINE, TYPES, get_table_model
from .utils import show_cursor, hide_cursor
from sqlalchemy.orm import sessionmaker
import gzip
import click
import os
import click_spinner
import time


def check_date(date: str):
    try:
        format = "%Y-%m-%d %H:%M:%S"
        date = datetime.strptime(date, format)
        return date
    except:
        return None


def condense(skipped) -> list[str]:
    freqMap = {}

    # Map frequencies of skipped lines
    for s in skipped:
        freqMap[s] = freqMap.get(s, 0) + 1

    # Sort the dict
    sort = sorted(freqMap.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    pretty = []

    # Make the frequencies pretty
    for k, v in sort:
        pretty.append(f"{k} -> ({v})")

    return pretty


def apply_trim(str, field, lineType=None):
    # Again, type will have to be done blindly
    if field == "type":
        sS, sE = (
            get_mapping()["default"]["type"]["sliceStart"],
            get_mapping()["default"]["type"]["sliceEnd"],
        )
    else:
        sS, sE = (
            get_mapping()[lineType]["fields"][field]["sliceStart"],
            get_mapping()[lineType]["fields"][field]["sliceEnd"],
        )

    # There should always be slice start, be it 0 or something specific
    if sS is None and sE is None:
        return str
    if sE is None or sE == 0:
        return str[sS:]
    return str[sS:sE]


def from_line(split_line, field, lineType=None):
    # type needs to be generic determined for any line
    if field == "type":
        # print(get_mapping())
        raw = split_line[get_mapping()["default"]["type"]["index"]]
        return apply_trim(raw, field)

    f = get_mapping()[lineType]["fields"].get(field)
    if f:
        try:
            raw = split_line[f["index"]]
            raw = apply_trim(raw, field, lineType)
            # Cast the contents to the expected type for sql
            raw = TYPES[field](raw)
            return raw
        except:
            return None


def process_line(line: str) -> tuple:
    line = line.strip()

    skeletor = {
        "date": None,
        "level": None,
        "origin": None,
        "ip": None,
        "http": None,
        "route": None,
        "code": None,
        "time": None,
        "user": None,
        "object": None,
        "records": None,
        "text": None,
    }

    # Line should be completely skipped if doesnt start with a date
    date = check_date(line.split(",")[0])
    if not date:
        return (2, None)

    skeletor["date"] = date

    spl = line.split(" ")

    # Determine line type
    lineType = from_line(spl, "type")

    if lineType not in set(get_mapping().keys()):
        return (1, lineType)

    # Based on type, assign all the values to the skeleton

    # Based on type, populate the skeleton
    for k in skeletor:
        # Already assigned date
        if k != "date":
            skeletor[k] = from_line(spl, k, lineType)

    # Add in the type and raw text
    skeletor["type"] = get_mapping()[lineType]["alias"]
    skeletor["text"] = " ".join(spl[get_mapping()["default"]["type"]["index"] + 1 :])

    # If origin is ? in the log, make it null
    if skeletor["origin"] == "?":
        skeletor["origin"] = None

    return (0, skeletor)


def convert_to_sql(full_file_path: str):
    start = time.perf_counter()

    # Set up sql conn
    model = get_table_model()
    BASE.metadata.create_all(ENGINE)
    Session = sessionmaker(bind=ENGINE)
    session = Session()

    # Lines to import
    logLines = []
    skipped = []

    # Calc some stats to show user
    stats = {}
    stats["junk_skipped"] = 0

    # Read the selected file

    hide_cursor()
    with gzip.open(full_file_path, "rt") as f:
        with click_spinner.spinner():
            click.echo(
                f"> Reading log file ({os.path.getsize(full_file_path) / 1000000} MB) ",
                nl=False,
            )
            lc = len(f.readlines())
            stats["raw_length"] = lc

            f.seek(0)
        click.echo("\n   Done!")
        with click.progressbar(
            f, label=f"-> Processing raw log lines ({lc})", length=lc
        ) as bar:
            for line in bar:
                status, processed = process_line(line)

                # If processing exits with 1 status, that means the type of the logline was skipped.
                if status == 1:
                    skipped.append(processed)
                    continue
                if status == 2:
                    # 2 is total skip
                    stats["junk_skipped"] = stats.get("junk_skipped", 0) + 1
                    continue

                # Add to the loglines if there were no errors
                logLines.append(processed)

        stats["log_lines_skipped"] = len(skipped)
        # Print out the lines that were skipped based on TYPE
        skipped = condense(skipped)

    logs = []
    with click.progressbar(
        logLines,
        label=f"-> Creating log line objects ({len(logLines)})",
        length=len(logLines),
    ) as ll:
        for l in ll:
            logs.append(model(**l))

    stats["table_len"] = len(logs)

    hide_cursor()
    click.echo("-> Writing to DB ", nl=False)
    with click_spinner.spinner():
        session.add_all(logs)
        session.commit()
    click.echo("\n   Done!")

    show_cursor()
    end = time.perf_counter()
    stats["time"] = end - start
    return (skipped, stats)
