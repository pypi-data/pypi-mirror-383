#!/usr/bin/env python


import argparse
import re
import sys
from typing import Any, Literal, Optional, TypeVar, cast

import pydantic
from pydantic import BaseModel, ValidationError

import caep

PYDANTIC_MAJOR_VERSION = pydantic.__version__.split(".")[0]

DEFAULT_SPLIT = ","

DEFAULT_KV_SPLIT = ":"

# Map of pydantic schema types to python types
TYPE_MAPPING: dict[str, type] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
}

# Type of BaseModel Subclasses
BaseModelType = TypeVar("BaseModelType", bound=BaseModel)


class SchemaError(Exception):
    pass


class FieldError(Exception):
    pass


class ArrayInfo(BaseModel):
    array_type: type
    split: str = DEFAULT_SPLIT


class DictInfo(BaseModel):
    dict_type: type
    split: str = DEFAULT_SPLIT
    kv_split: str = DEFAULT_KV_SPLIT


Arrays = dict[str, ArrayInfo]
Dicts = dict[str, DictInfo]


def escape_split(
    value: str, split: str = DEFAULT_SPLIT, maxsplit: int = 0
) -> list[str]:
    """
    Helper method to split on specified field
    (unless field is escaped with backslash)
    """

    return [
        re.sub(r"(?<!\\)\\", "", v)
        for v in re.split(rf"(?<!\\){split}", value, maxsplit=maxsplit)
    ]


def split_dict(
    value: Optional[str], dict_info: DictInfo, field: Optional[str] = None
) -> dict[str, Any]:
    """
    Split string into dictionary

    Arguments:
        value: str      - Value to split
        array: DictInfo - Config object that specifies the type
                          and the value to split items and
                          key/values on
    """
    d: dict[str, Any] = {}

    if value is None or not value.strip():
        d = {}

    else:
        # Split on specified field, unless they are escaped
        for items in escape_split(value, dict_info.split):
            try:
                # Split key val on first occurence of specified split value
                key, val = escape_split(items, dict_info.kv_split, maxsplit=2)
            except ValueError as e:
                raise FieldError(
                    f"Unable to split {items} by `{dict_info.kv_split}`"
                ) from e

            d[key.strip()] = dict_info.dict_type(val.strip())

    return d


def split_list(value: str, array: ArrayInfo, field: Optional[str] = None) -> list[Any]:
    """
    Split string into list

    Arguments:
        value: str       - Value to split
        array: ArrayInfo - Config object that specifies the type
                           and the value to split on
    """
    if value is None or not value.strip():
        lst = []
    else:
        # Split by configured split value, unless it is escaped
        lst = [array.array_type(v.strip()) for v in escape_split(value, array.split)]

    return lst


def split_arguments(
    args: argparse.Namespace, arrays: Arrays, dicts: Dicts
) -> dict[str, Any]:
    """
    Loop over argument/values and split by configured split value for dicts and arrays

    Supports escaped values which not be part of the split operation

    Arguments:

        args: argparse.Namespace - Argparse namespace
        arrays: dict[str, ArrayInfo] - Dictionary with field name as key
                                       and ArrayInfo (type + split) as value
        dicts: dict[str, ArrayInfo] -  Dictionary with field name as key
                                       and DictInfo (type + split/kv_split) as value
    """
    args_with_list_split = {}

    for field, value in vars(args).items():
        if field in arrays and not isinstance(value, (set, list)):
            value = split_list(value, arrays[field], field)

        elif field in dicts and not isinstance(value, dict):
            value = split_dict(value, dicts[field], field)

        args_with_list_split[field] = value

    return args_with_list_split


def build_parser(  # noqa: C901
    fields: dict[str, dict[str, Any]],
    description: str,
    epilog: Optional[str],
) -> tuple[argparse.ArgumentParser, Arrays, Dicts]:
    """

    Build argument parser based on pydantic fields

    Return ArgumentParser and fields that are defined as arrays

    """

    # Map of all fields that are defined as arrays
    arrays: Arrays = {}

    # Map of all fields that are defined as objects (dicts)
    dicts: Dicts = {}

    # Add epilog to --help output
    if epilog:
        parser = argparse.ArgumentParser(
            description,
            epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(description)

    # Example internal data structure for pydantic fields that we parse
    # {
    #   "enabled": {
    # 	    "default": false,
    # 	    "description": "Boolean with default value",
    # 	    "title": "Enabled",
    # 	    "type": "boolean"
    #   },
    #   "flag1": {
    # 	    "default": true,
    # 	    "description": "Boolean with default value",
    # 	    "title": "Flag1",
    # 	    "type": "boolean"
    #   },
    #   "str_arg": {
    # 	    "description": "Required String Argument",
    # 	    "title": "Str Arg",
    # 	    "type": "string"
    #   },
    #   "strlist": {
    # 	    "description": "Comma separated list of strings",
    # 	    "items": {
    # 	          "type": "string"
    # 	    },
    # 	    "split": ",",
    # 	    "title": "Strlist",
    # 	    "type": "array"
    #   },
    #     "dict_arg": {
    #     "title": "Dict Arg",
    #     "description": "Dict ",
    #     "default": {},
    #     "kv_split": ":",
    #     "split": ",",
    #     "type": "object",
    #     "additionalProperties": {
    #         "type": "string"
    #     }
    # }

    # Loop over all pydantic schema fields
    for field, schema in fields.items():
        # for lists, dicts and sets we will use the default (str), but
        # for other types we will raise an error if field_type is not specified
        field_type: type = str
        default = schema.get("default")

        # In pydantic 2.0+ some fields are represented with anyOf, like this:
        #
        # "path": {
        #     "anyOf": [
        #         {
        #             "format": "path",
        #             "type": "string"
        #         },
        #         {
        #             "type": "null"
        #         }
        #     ],
        #     "description": "Path",
        #     "title": "Path"
        #

        for types in schema.get("anyOf", []):
            if types.get("type") != "null":
                schema.update(**types)

        if "type" not in schema:
            raise FieldError(
                "No type specified, recursive models are not supported: "
                f"{field}: {schema}"
            )

        if schema["type"] == "array":
            array_type = TYPE_MAPPING.get(schema["items"]["type"])

            if not array_type:
                raise FieldError(
                    f"Unsupported pydantic type for array field {field}: {schema}"
                )

            arrays[field] = ArrayInfo(
                array_type=array_type,
                split=schema.get("split", DEFAULT_SPLIT),
            )

            # For arrays (lists, sets etc), we parse as str in caep and split values by
            # configured split value later
            field_type = str

        elif schema["type"] == "object":
            dict_type = TYPE_MAPPING.get(schema["additionalProperties"]["type"])

            if not dict_type:
                raise FieldError(
                    f"Unsupported pydantic type for dict field {field}: {schema}"
                )

            dicts[field] = DictInfo(
                dict_type=dict_type,
                split=schema.get("split", DEFAULT_SPLIT),
                kv_split=schema.get("kv_split", DEFAULT_KV_SPLIT),
            )

        else:
            if schema["type"] not in TYPE_MAPPING:
                raise FieldError(
                    f"Unsupported pydantic type for field {field}: {schema}"
                )

            field_type = TYPE_MAPPING[schema["type"]]

        parser_args: dict[str, Any] = {}

        if field_type is bool:
            if default in (False, None):
                parser_args["action"] = "store_true"

                # Explicit set default value as False
                if default is None:
                    default = False
            elif default is True:
                parser_args["action"] = "store_false"
            else:
                raise FieldError(
                    f"bools only support defaults of False/None/True {field}: {schema}"
                )
        else:
            parser_args = {"type": field_type}

        parser.add_argument(
            f"--{field.replace('_', '-')}",
            help=schema.get("description", "No help provided"),
            default=default,
            **parser_args,
        )

    return parser, arrays, dicts


def load(
    model: type[BaseModelType],
    description: str,
    config_id: Optional[str] = None,
    config_file_name: Optional[str] = None,
    section_name: Optional[str] = None,
    alias: bool = False,
    opts: Optional[list[str]] = None,
    raise_on_validation_error: bool = False,
    exit_on_validation_error: bool = True,
    epilog: Optional[str] = None,
    unknown_config_key: Literal["ignore", "warning", "error"] = "warning",
) -> BaseModelType:
    """

    Load ceap config as derived from pydantic model

    Arguments:

        model: BaseModelType            - Pydantic Model
        description: str                - Argparse description to show on --help
        config_id                       - CAEP config id
        config_file_name                - CAEP config file name
        section_name: str               - CAEP section name from config
        alias: bool                     - Use alias for pydantic schema
        opts: Optional[List[str]]       - Send option to caep (usefull for
                                          testing command line options)
        raise_on_validation_error: bool - Reraise validation errors from pydantic
        exit_on_validation_error: bool  - Exit and print help on validation error
        epilog: str                     - Add epilog text to --help output

    Returns parsed model

    """

    # Get all pydantic fields
    # In pydantix 1.x we use the `schema()` method, but this is replaced with
    # `model_json_schema` in pydantic 2.x.

    if PYDANTIC_MAJOR_VERSION == "2":
        fields = model.model_json_schema(alias).get("properties")
    else:
        fields = model.schema(alias).get("properties")

    if not fields:
        raise SchemaError(f"Unable to get properties from schema {model}")

    # Build argument parser based on pydantic fields
    parser, arrays, dicts = build_parser(fields, description, epilog)

    try:
        args = split_arguments(
            args=caep.config.handle_args(
                parser,
                config_id,
                config_file_name,
                section_name,
                opts=opts,
                unknown_config_key=unknown_config_key,
            ),
            arrays=arrays,
            dicts=dicts,
        )
    except ValueError as e:
        if raise_on_validation_error:
            raise
        print(e)

        parser.print_help()
        sys.exit(2)

    try:
        return model(**args)
    except ValidationError as e:
        if raise_on_validation_error:
            raise
        else:
            # ValidationError(model='Arguments',
            #                  errors=[{'loc': ('str_arg',),
            #                          'msg': 'none is not an allowed value',
            #                          'type': 'type_error.none.not_allowed'}])

            for error in e.errors():
                argument = cast(str, error.get("loc", [])[0]).replace("_", "-")
                msg = error.get("msg")

                print(f"{msg} for --{argument}\n")

            parser.print_help()
            sys.exit(1)
