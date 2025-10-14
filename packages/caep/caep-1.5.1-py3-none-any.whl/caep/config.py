#!/usr/bin/env python

"""

config module, supports loading config from ini, environment and arguments

The configuration presedence are (from lowest to highest):
    1. argparse default
    3. ini file
    3. environment variable
    4. command line argument

# Config

Arguments are parsed in two phases. First, it will look for the
argument --config argument which can be used to specify an
alternative location for the ini file. If not --config argument
is given it will look for an ini file in the following locations
(~/.config has presedence):

- ~/.config/<CONFIG_ID>/<CONFIG_FILE_NAME>
  (or directory specified by XDG_CONFIG_HOME)
- /etc/<CONFIG_FILE_NAME>

The ini file can contain a "[DEFAULT]" section that will be used
for all configurations. In addition it can have a section that
corresponds with <SECTION_NAME> that for specific cofiguration,
that will over overide config from DEFAULT

# Environment variables

The configuration step will also look for environment variables
in uppercase and with "-" replaced with "_". For the example below
it will lookup the following environment
variables:

    - $NUMBER
    - $BOOL
    - $STR_ARG

Example:

>>> parser = argparse.ArgumentParser("test argparse")
>>> parser.add_argument('--number', type=int, default=1)
>>> parser.add_argument('--bool', action='store_true')
>>> parser.add_argument('--str-arg')
>>> args = config.handle_args(
        parser,
        <CONFIG_ID>,
        <CONFIG_FILE_NAME>,
        <SECTION_NAME>)

"""

import argparse
import configparser
import os
import warnings
from functools import partialmethod
from pathlib import Path
from typing import Any, Literal, Optional

from . import xdg

# Monkeypatch ArgumentParser to not allow abbrevations as those will make it
# hard to mix and match options on commandline, env and ini files
argparse.ArgumentParser.__init__ = partialmethod(  # type: ignore
    argparse.ArgumentParser.__init__, allow_abbrev=False
)


class ArgumentError(Exception):
    pass


class SectionNotFound(Exception):
    pass


class NotSupported(Exception):
    pass


def find_default_ini(ini_id: str, ini_filename: str) -> Optional[str]:
    """
    Look for default ini files in /etc and ~/.config
    """

    # Order to search for confiuration files
    locations = [
        xdg.get_config_dir(ini_id) / ini_filename,
        Path("/etc") / ini_filename,
    ]

    ini_files = [loc for loc in locations if loc.is_file()]

    if not ini_files:
        return None

    with ini_files[0].open() as f:
        return f.read()


def get_early_parser() -> argparse.ArgumentParser:
    """
    return ArgumentParser for early arguments
    """
    early_parser = argparse.ArgumentParser(
        description="configfile parser", add_help=False
    )
    early_parser.add_argument(
        "--config",
        dest="config",
        type=argparse.FileType("r", encoding="UTF-8"),
        default=None,
        nargs="+",
        help="change default configuration location",
    )

    return early_parser


def load_ini(
    config_id: Optional[str],
    config_name: Optional[str],
    opts: Optional[list[str]] = None,
) -> tuple[Optional[configparser.ConfigParser], list[str]]:
    """
    return config, remainder_argv

    config_id and config_name will be used to locate the default config like this,
    if they are specified:
        - ~/.config/<CONFIG_ID>/<CONFIG_FILE_NAME>
        - /etc/<CONFIG_FILE_NAME>
    """

    early_parser = get_early_parser()
    args, remainder_argv = early_parser.parse_known_args(opts)

    config = []

    if args.config:
        config = [cfg_file.read() for cfg_file in args.config]

    # No config file specified on command line, attempt to find
    # in default locations
    else:
        if config_id and config_name:
            config = [find_default_ini(config_id, config_name)]

    if config:
        cp = configparser.ConfigParser()
        for cfg in config:
            cp.read_string(cfg)
        return cp, remainder_argv

    return None, remainder_argv


def get_env(key: str) -> dict[str, str]:
    """
    Get environment variable based on key
    (uppercase and replace "-" with "_")
    """
    env_key = key.replace("-", "_").upper()

    if env_key in os.environ:
        return {key: os.environ[env_key]}
    return {}


def get_default(action: argparse.Action, section: dict[str, Any], key: str) -> Any:
    """
    Find default value for an option. This will only be used if an
    argument is not specified at the command line. The defaults will
    be found in this order (from lowest to highest):
        1. argparse default
        3. ini file
        3. environment variable

    """
    default = action.default
    env = get_env(key)

    # environment has higher presedence than config section
    if key in env:
        default = env[key]
    elif key in section:
        default = section[key]

    # if not env or section, keep default from argparse

    # parse true/yes as True and false/no as False for
    # action="store_true" and action="store_false"
    if action.const in (True, False) and isinstance(default, str):
        if default.lower() in ("true", "yes"):
            default = True
        elif default.lower() in ("false", "no"):
            default = False

    if action.nargs in (argparse.ZERO_OR_MORE, argparse.ONE_OR_MORE):
        if isinstance(default, str):
            default = default.split()
        elif isinstance(default, list):
            pass
        else:
            raise ValueError("Not string or list in nargs")

    # If argument type is set and default is not None, enforce type
    # Eg, for this argument specification
    # parser.add_argument('--int-arg', type=int)
    # --int-arg 2
    # will give you int(2)
    # If --int-arg is omitted, it will use None
    if (
        action.type is not None
        and default is not None
        # If default is specified as list, set or dict, do not enforce type
        and not isinstance(default, (list, set, dict))
    ):
        default = action.type(default)  # type: ignore

    return default


def all_defaults(
    parser: argparse.ArgumentParser, config: dict[str, Any]
) -> dict[str, Any]:
    """Get defaults based on presedence"""

    defaults = {}

    # Loop over parser groups / actions
    # Unfortunately we can only do this in protected members..
    # pylint: disable=protected-access
    for g in parser._action_groups:
        for action in g._actions:
            if action.required:
                opt = "".join(action.option_strings)
                raise NotSupported(
                    f'"required" argument is not supported (found in option {opt}). '
                    + "Set to false and test after it has been parsed by handle_args()"
                )
            for option_string in action.option_strings:
                if option_string.startswith("--"):
                    key = option_string[2:]

                    defaults[action.dest] = get_default(action, config, key)

    return defaults


def underscore_keys_to_dash(d: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of the dictionary with underscore in the keys replace by dash"""
    return {key.replace("_", "-"): value for key, value in d.items()}


def check_and_handle_invalid_config_key(
    unknown_config_key: Literal["ignore", "warning", "error"],
    args: argparse.Namespace,
    config: list[str],
    config_id: Optional[str],
    config_name: Optional[str],
    section_name: Optional[str],
) -> None:
    """check that all config arguments are nown and handle them acordingly,

    based on `unknown_config_key`:

    `ignore`  - do nothing
    `warning` - emit warning
    `error`   - raise ValueError

    """
    if unknown_config_key == "ignore":
        return

    parser_options = args.__dict__.keys()
    for key in config:
        if key.replace("-", "_") not in parser_options:
            config_str = f"{config_id}/{config_name}"
            if section_name:
                config_str += f"[{section_name}]"
            message = f"Unknown option {key} found in configuration {config_str}"

            if unknown_config_key == "warning":
                warnings.warn(message, RuntimeWarning, stacklevel=1)
            elif unknown_config_key == "error":
                raise ValueError(message)
            else:
                # This should not happen
                raise ArgumentError(
                    f"Illegal argument for unknown_config_key: {unknown_config_key}"
                )


def handle_args(
    parser: argparse.ArgumentParser,
    config_id: Optional[str],
    config_name: Optional[str],
    section_name: Optional[str],
    opts: Optional[list[str]] = None,
    unknown_config_key: Literal["ignore", "warning", "error"] = "warning",
) -> argparse.Namespace:
    """
    parses and sets up the command line argument system above
    with config file parsing.

    config_id and config_name will be used to locate the default config like this:
        - ~/.config/<CONFIG_ID>/<CONFIG_FILE_NAME>
        - /etc/<CONFIG_FILE_NAME>

    config_id, config_name and section_name is optional and without them
    configuration will not be loaded from an ini-file.

    ArgumentError is raised if some but none all of config_id, config_name and
    section_name is specified.
    """

    config_opts = [config_id, config_name]

    if any(config_opts) and not all(config_opts):
        raise ArgumentError(
            "If one of  config_id or config_name is specified you must specify both"
        )

    # Load from ini
    cp, remainder_argv = load_ini(config_id, config_name, opts=opts)

    if cp and section_name:
        # Add (empty) section. In this way we can still access
        # the DEFAULT section
        if not cp.has_section(section_name):
            cp.add_section(section_name)
        config = underscore_keys_to_dash(dict(cp[section_name]))
    elif cp and cp.defaults():
        config = underscore_keys_to_dash(dict(cp.defaults()))
    else:
        config = {}

    parser.set_defaults(**all_defaults(parser, config))

    args = parser.parse_args(remainder_argv)

    check_and_handle_invalid_config_key(
        unknown_config_key,
        args,
        list(config.keys()),
        config_id,
        config_name,
        section_name,
    )

    return args
