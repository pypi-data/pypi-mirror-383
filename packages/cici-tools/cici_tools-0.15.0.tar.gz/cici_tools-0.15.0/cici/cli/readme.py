# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Any

import markdown
import msgspec
from jinja2 import Environment, FileSystemLoader
from ruamel.yaml import YAML

from ..config.project.serializers import load as load_cici_config
from ..constants import TEMPLATE_DIR
from ..paths import (
    get_cici_config_file_path,
    get_cici_config_gitlab_ci_file_path,
    get_cici_config_readme_template_path,
    get_pre_commit_hooks_path,
)
from ..providers.gitlab.utils import get_job_names


def to_markdown(text):
    return markdown.markdown(text)


def get_yaml_data(filename):
    yaml = YAML(typ="safe")
    return yaml.load(open(filename))


def get_gitlab_ci_jobs(gitlab_ci_file) -> dict[str, Any]:
    try:
        data = get_yaml_data(gitlab_ci_file)
    except FileNotFoundError:
        return {}
    return {job: data[job] for job in get_job_names(data) if not job.startswith(".")}


def get_precommit_hooks(precommit_hooks_file) -> dict[str, Any]:
    try:
        data = get_yaml_data(precommit_hooks_file)
    except FileNotFoundError:
        return {}
    return {hook["id"]: hook for hook in data}


def readme_command(parser, args):
    environment = Environment(
        loader=FileSystemLoader(
            [
                get_cici_config_file_path(),
                TEMPLATE_DIR,
            ]
        ),
    )
    environment.filters["markdown"] = to_markdown

    template = environment.get_template("README.md.j2")

    gitlab_ci_jobs = get_gitlab_ci_jobs(get_cici_config_gitlab_ci_file_path())
    precommit_hooks = get_precommit_hooks(get_pre_commit_hooks_path())

    config = load_cici_config(
        args.config_file, gitlab_ci_jobs=gitlab_ci_jobs, precommit_hooks=precommit_hooks
    )

    with open(args.output_file, "w") as handle:
        handle.write(
            template.render(
                **json.loads(msgspec.json.encode(config)),
            ).rstrip()
            + "\n"  # guarantee single line ending EOF
        )


def readme_parser(subparsers):
    parser = subparsers.add_parser("readme", help="generate pipeline readme")
    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        default=get_cici_config_readme_template_path(),
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config_file",
        default=get_cici_config_file_path(),
    )
    parser.set_defaults(func=readme_command)
    return parser
