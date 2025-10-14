# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import argparse
import json
import sys

import msgspec
from ruamel.yaml import YAML

from ..config.project import models as cici_config


def get_schema_type(schema_name: str) -> type[cici_config.File]:
    return {
        "cici-config": cici_config.File,
    }[schema_name]


def write_schema_file(schema, output_file, output_format):
    if output_format == "json":
        json.dump(schema, output_file, indent=2)
    elif output_format == "yaml":
        yaml = YAML(typ="safe")
        yaml.default_flow_style = False
        yaml.dump(schema, output_file)
    else:
        raise NotImplementedError("this is not a supported output format")


def schema_command(parser, args):
    schema_type = get_schema_type(args.schema_name)
    schema = msgspec.json.schema(schema_type)
    write_schema_file(
        schema=schema, output_file=args.output_file, output_format=args.output_format
    )


def schema_parser(subparsers):
    parser = subparsers.add_parser("schema", help="generate json schema")
    parser.add_argument(
        "-s",
        "--schema",
        dest="schema_name",
        choices=["cici-config"],
        default="cici-config",
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="output_format",
        choices=["json", "yaml"],
        default="json",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        type=argparse.FileType("w"),
        default=sys.stdout,
    )
    parser.set_defaults(func=schema_command)
    return parser
