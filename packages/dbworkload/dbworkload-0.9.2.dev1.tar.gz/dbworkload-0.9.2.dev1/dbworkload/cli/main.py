#!/usr/bin/python

import json
import logging
import os
import platform
import sys
from enum import Enum
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import pandas as pd
import typer
import yaml

import dbworkload.cli.util
import dbworkload.models.run
import dbworkload.utils.common
from dbworkload.cli.dep import EPILOG, ConnInfo, Param

from .. import __version__

logger = logging.getLogger("dbworkload")


class Driver(str, Enum):
    postgres = "postgres"
    mysql = "mysql"
    maria = "maria"
    oracle = "oracle"
    sqlserver = "sqlserver"
    mongo = "mongo"
    cassandra = "cassandra"
    spanner = "spanner"


app = typer.Typer(
    epilog=EPILOG,
    no_args_is_help=True,
    help=f"dbworkload v{__version__}: DBMS workload utility.",
)


app.add_typer(dbworkload.cli.util.app, name="util")

version: bool = typer.Option(True)


class LogLevel(str, Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"


@app.command(help="Run the workload.", epilog=EPILOG, no_args_is_help=True)
def run(
    workload_path: Optional[Path] = typer.Option(
        None,
        "--workload",
        "-w",
        help="Filepath to the workload module.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
    driver: Driver = typer.Option(
        None,
        help="DBMS driver.",
    ),
    uri: str = typer.Option(
        None,
        "--uri",
        help="The connection URI to the database.",
    ),
    procs: int = Param.Procs,
    args: str = typer.Option(
        None, help="JSON string, or filepath to a JSON/YAML file, to pass to Workload."
    ),
    concurrency: int = typer.Option(
        1, "-c", "--concurrency", help="Number of concurrent workers."
    ),
    ramp: int = typer.Option(0, "-r", "--ramp", help="Ramp up time in seconds."),
    iterations: int = typer.Option(
        None,
        "-i",
        "--iterations",
        help="Total number of iterations. Defaults to <ad infinitum>.",
        show_default=False,
    ),
    duration: int = typer.Option(
        None,
        "-d",
        "--duration",
        help="Duration in seconds. Defaults to <ad infinitum>.",
        show_default=False,
    ),
    max_rate: int = typer.Option(
        None,
        "--max-rate",
        show_default=False,
        help="Set the max-rate to have dbworkload manage concurrency. Defaults to None.",
    ),
    conn_duration: int = typer.Option(
        None,
        "-k",
        "--conn-duration",
        show_default=False,
        help="The number of seconds to keep database connection alive before restarting. Defaults to <ad infinitum>.",
    ),
    app_name: Optional[str] = typer.Option(
        None,
        "--app-name",
        "-a",
        help="The application name specified by the client. Defaults to <db-name>.",
        show_default=False,
    ),
    autocommit: bool = typer.Option(
        True,
        "--no-autocommit",
        show_default=False,
        help="Unset autocommit in the connections.",
    ),
    prom_port: int = typer.Option(
        26260, "-p", "--port", help="The port of the Prometheus server."
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        show_default=False,
        help="Disable printing intermediate stats.",
    ),
    save: bool = typer.Option(
        False,
        "--save",
        "-s",
        show_default=False,
        help="Save stats to CSV files.",
    ),
    schedule: str = typer.Option(
        None,
        "--schedule",
        help="schedule JSON string or filepath to the schedule file.",
    ),
    histogram_bins: str = typer.Option(
        "5,10,25,50,75,100,125,250,500,750,1000",
        "--bins",
        help="comma separated list of ints defining the histogram bins.",
    ),
    delay_stats: int = typer.Option(
        0, "--delay-stats", help="Start collecting stats after the speciied seconds."
    ),
    log_level: LogLevel = Param.LogLevel,
):
    logger.setLevel(log_level.upper())

    logger.debug("Executing run()")

    if not procs:
        procs = os.cpu_count()

    # check workload is a valid module and class
    workload = dbworkload.utils.common.import_class_at_runtime(workload_path)

    conn_info = ConnInfo()

    # check if the uri parameter is actually a URI
    parse_result = urlparse(uri)

    if parse_result.scheme:
        driver = dbworkload.utils.common.get_driver_from_scheme(parse_result.scheme)
        if driver is None:
            logger.error(
                f"Could not find a driver for URI scheme '{parse_result.scheme}'."
            )
            sys.exit(1)

        if get_app_name(driver):
            uri = dbworkload.utils.common.set_query_parameter(
                url=uri,
                param_name=get_app_name(driver),
                param_value=app_name if app_name else workload.__name__,
            )

        if driver == "postgres":
            conn_info.params["conninfo"] = uri

        elif driver == "mongo":
            conn_info.params["host"] = uri

    else:
        # if not, the uri is a string like
        # 'user=user1,password=password1,host=localhost,port=3306,database=bank'
        # so we split the key-value pairs
        for pair in uri.replace(" ", "").split(","):
            k, v = pair.split("=")
            if v.isdigit():
                v = int(v)
            conn_info.params[k] = v

        driver = driver.value

    if driver == "postgres":
        conn_info.params["autocommit"] = autocommit

    if driver in ["mysql", "maria"]:
        conn_info.params["autocommit"] = autocommit

        if "client_flags" in conn_info.params:
            try:
                from mysql.connector import ClientFlag
            except:
                logger.error("Could not import MySQL driver. Did you install it?")

            client_flags = []
            flags: list[str] = [
                x.replace("ClientFlag.", "")
                for x in conn_info.params["client_flags"].split(";")
            ]
            for f in flags:
                if f.startswith("-"):
                    if f[1:].isdigit():
                        client_flags.append(int(f))
                    else:
                        client_flags.append(-1 * getattr(ClientFlag, f[1:]))
                else:
                    if f.isdigit():
                        client_flags.append(int(f))
                    else:
                        client_flags.append(getattr(ClientFlag, f))

            conn_info.params["client_flags"] = client_flags

    if driver == "oracle":
        conn_info.extras["autocommit"] = autocommit

    args = load_args(args)

    histogram_bins = histogram_bins.split(",")
    schedule = load_schedule(schedule)

    dbworkload.models.run.run(
        concurrency,
        workload_path,
        prom_port,
        iterations,
        procs,
        ramp,
        conn_info,
        duration,
        conn_duration,
        max_rate,
        args,
        driver,
        quiet,
        save,
        schedule,
        histogram_bins,
        delay_stats,
        log_level.upper(),
    )


def get_app_name(driver: str):
    if driver == "postgres":
        return "application_name"
    elif driver == "mysql":
        return
    elif driver == "mongo":
        return "appName"
    elif driver == "maria":
        return
    elif driver == "oracle":
        return
    elif driver == "sqlserver":
        return
    elif driver == "cassandra":
        return


def load_args(args: str):
    # load args dict from file or string
    if args:
        if os.path.exists(args):
            with open(args, "r") as f:
                args = f.read()
                # parse into JSON if it's a JSON string
                try:
                    return json.load(args)
                except Exception as e:
                    pass
        else:
            args = yaml.safe_load(args)
            if isinstance(args, str):
                logger.error(
                    f"The value passed to '--args' is not a valid path to a JSON/YAML file, nor has no key:value pairs: '{args}'"
                )
                sys.exit(1)
            else:
                return args
    return {}


def load_schedule(schedule_path: str):
    if schedule_path:
        if os.path.exists(schedule_path):
            df = pd.read_csv(schedule_path, dtype="Int64", comment="#").fillna(0)
            # trasform ramp and duration columns from minutes to seconds
            df[["ramp", "duration"]] = df[["ramp", "duration"]] * 60

            return df.values.tolist()
        else:
            try:
                return json.loads(schedule_path)
            except:
                logger.error(f"couldn't decode {schedule_path} as JSON")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"dbworkload : {__version__}")
        typer.echo(f"Python     : {platform.python_version()}")
        raise typer.Exit()


@app.callback()
def version_option(
    _: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=_version_callback,
        help="Print the version and exit",
    ),
) -> None:
    pass


# this is only needed for mkdocs-click
click_app = typer.main.get_command(app)
