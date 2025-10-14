# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import io
import typing
from pathlib import Path
from typing import Optional

import msgspec
import ruamel.yaml
from msgspec import ValidationError
from msgspec.structs import replace
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

from cici.providers.gitlab.normalizers import (
    normalize_jobs_in_data,
    normalize_scalars,
    normalize_variables,
)

from ...config.project import models as cici_config
from . import models
from . import models as gitlab
from .utils import get_job_names
from .yaml_style import always_double_quoted, style_scalars

# decoders/encoders for msgspec
decoder = msgspec.json.Decoder(type=models.File)
encoder = msgspec.json.Encoder()


# turn plain dict into gitlab.File using msgspec
def decode_file(data: dict) -> gitlab.File:
    return decoder.decode(encoder.encode(data))


# Raumel cannot walk msgspec.Structs
# This helper is final dump step so ruamel.yaml can serialize
def to_dict(obj):
    encoded = msgspec.json.encode(obj)
    return msgspec.json.decode(encoded)


def expand_job_extends(jobs: dict[str, gitlab.Job], job: gitlab.Job) -> gitlab.Job:
    # If the job does not use 'extends', return it unchanged
    if not job.extends:
        return job

    # extends can be a single string or a list
    # normalize to a list so we can iterate
    extends = job.extends if isinstance(job.extends, list) else [job.extends]

    # empty dict that will accumulate parent fields
    merged: dict = {}

    # for each parent job listed in extends:
    for extend in extends:
        # recursively expand the parent first so fit the parent also has 'extends' it gets resolved too
        parent_job = expand_job_extends(jobs, jobs[extend])
        # convert expanded parent struct into plain dict to easily merge its fields
        parent_dict = to_dict(parent_job)
        # Add parent fields to accumulator (later parents should override earlier ones if conflicts)
        merged.update(parent_dict)

    # convert child job into a dict
    child_dict = to_dict(job)

    # Overlay the childs fields on top of the merged parent dict
    # but skip values that are empty so we dont wipe away necessart parent defaults
    for k, v in child_dict.items():
        if v in (None, "", [], {}, False):
            continue

        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            # merge child into parent but child wins on conflicts
            merged[k] = {**merged[k], **v}
        else:
            merged[k] = v

    # remove extends key since its resolved now
    merged.pop("extends", None)

    # Rebuild fresh msgspec job struct from the merged dict
    return gitlab.Job(**merged)


def expand_jobs(file_struct: gitlab.File) -> gitlab.File:
    patched_jobs = {}
    for job_name, job in file_struct.jobs.items():
        expanded_job = expand_job_extends(file_struct.jobs, job)
        patched_jobs[job_name] = expanded_job
    return replace(file_struct, jobs=patched_jobs)


def pack_jobs(data: dict) -> dict:
    if not isinstance(data, dict):
        return data

    job_names = get_job_names(data)
    jobs = {}

    # get all job definitions
    for job_name in sorted(list(job_names)):
        job_def = data[job_name]
        if not job_def:
            continue

        # validate hidden jobs if they start with '.'
        if job_name.startswith("."):
            try:
                # validate if job is valid
                msgspec.json.Decoder(type=models.Job).decode(
                    msgspec.json.Encoder().encode(job_def)
                )
                jobs[job_name] = job_def
            except ValidationError:
                # skip hidden jobs that are not valid
                continue
        else:
            jobs[job_name] = job_def

        # remove job entry from top level
        data.pop(job_name, None)

    data["jobs"] = jobs

    # make sure variables, stages, and workflow remain top level
    return data


def unpack_jobs(data: dict) -> dict:
    if "jobs" in data:
        for name, job in list(data["jobs"].items()):
            data[name] = job
        del data["jobs"]

    return data


# make sure each variable dict includes 'name' field
def inject_variable_names(
    variables: dict[str, typing.Union[str, dict]],
) -> dict[str, dict]:
    patched = {}
    for key, value in variables.items():
        if isinstance(value, str):
            value = {"value": value}
        if not isinstance(value, dict):
            raise TypeError(f"Expected dict for variable {key}, got {type(value)}")
        value.setdefault("name", key)  # inject only in dict, not struct
        patched[key] = value

    return patched


def add_config_variables(data: dict, cici_config_file) -> dict:
    # merge variables from cici_config_file into the top-level YAML variables block
    # also maps brief -> description and `default` -> `value`.

    if not cici_config_file or not hasattr(cici_config_file, "variables"):
        return data

    config_vars = getattr(cici_config_file, "variables", {})

    if not isinstance(config_vars, dict):
        return data

    # make sure top level variable exists
    if "variables" not in data or not isinstance(data["variables"], dict):
        data["variables"] = {}

    for name, variable in config_vars.items():
        # convert msgspec.Struct -> dict
        if hasattr(variable, "__struct__") or hasattr(variable, "__annotations__"):
            variable = msgspec.to_builtins(variable)
        # verify variable info is in the dict
        if not isinstance(variable, dict):
            continue

        # map brief -> description and default -> value
        description = variable.get("brief") or variable.get("description") or ""

        value = variable.get("default") or variable.get("value") or ""

        # merged_stuff = {
        #     "description": description,
        #     "value": value,
        # }
        merged_stuff = {}
        # only keep description if it contains stuff
        if description:
            merged_stuff["description"] = description
        merged_stuff["value"] = value

        # Now merge into top level variables but don't clobber existing keys unless empty
        if name not in data["variables"]:
            data["variables"][name] = merged_stuff
        else:
            existing = data["variables"][name]
            if not isinstance(existing, dict):
                existing = {"value": str(existing)}

            existing.setdefault("description", description)
            existing.setdefault("value", value)
            data["variables"][name] = existing

    return data


def inject_container_into_job(
    file_struct: gitlab.File,
    cici_config_file: Optional[cici_config.File] = None,
) -> gitlab.File:
    # return a new file struct with containers injected into matching jobs
    if not cici_config_file:
        return file_struct

    # Build a brand new dict (copy of jobs)
    patched_jobs: dict[str, gitlab.Job] = {}

    for name, job in file_struct.jobs.items():
        # find matching target by name
        target = next(
            (target for target in cici_config_file.targets if target.name == name),
            None,
        )

        if target and target.container:
            # overwrite image with container info from config
            patched_jobs[name] = replace(
                job,
                image={
                    "name": target.container.image,
                    "entrypoint": target.container.entrypoint,
                },
            )
        else:
            # no container override then keep original job
            patched_jobs[name] = job

    # return new File struct with updated jobs
    return replace(file_struct, jobs=patched_jobs)


# Parse YAML, Normalize variables, patch jobs and decode
def loads(
    text: str, cici_config_file: typing.Optional[cici_config.File] = None
) -> gitlab.File:
    yaml = ruamel.yaml.YAML()
    data = yaml.load(text)

    # 1. Normalize scalars
    data = normalize_scalars(data)

    # 2. merge top-level config variables
    if cici_config_file:
        data = add_config_variables(data, cici_config_file=cici_config_file)

    # DEBUG
    # print("CONFIG FILE TYPE:", type(cici_config_file))
    # print("CONFIG FILE CONTENT:", getattr(cici_config_file, "variables", None))

    # 4. normalize jobs
    data = normalize_jobs_in_data(data)

    # 5. normalize variables format
    data = normalize_variables(data)

    # 6. inject variable names
    if "variables" in data:
        data["variables"] = inject_variable_names(data["variables"])

    # 7. pack the jobs
    data = pack_jobs(data)

    # DEBUG
    # print("Keys at top level before decode:", data.keys())
    # print("Variables at top level:", data.get("variables"))

    # 8. decode into msgspec struct
    file_struct = decode_file(data)

    # 9. expand extends and anchors
    file_struct = expand_jobs(file_struct)

    # 10. inject container defaults
    return inject_container_into_job(file_struct, cici_config_file)


# convert struct back to dict, apply container injection + YAML dump
def load(
    file: typing.Union[str, Path],
    cici_config_file: typing.Optional[cici_config.File] = None,
) -> gitlab.File:
    return loads(open(file).read(), cici_config_file=cici_config_file)


def dumps(
    file: gitlab.File, cici_config_file: typing.Optional[cici_config.File] = None
) -> str:
    output = io.StringIO()
    dump(file, output, cici_config_file)
    return output.getvalue()


def dump(
    file: gitlab.File,
    stream: typing.IO,
    cici_config_file: Optional[cici_config.File] = None,
):

    if cici_config_file:
        file = inject_container_into_job(file, cici_config_file)

    data = msgspec.to_builtins(file)
    data = unpack_jobs(data)
    data = style_scalars(data)

    # user round trip mode to preserve ruamel scalar styles (FoldedScalarString etc)
    yaml = ruamel.yaml.YAML(typ="rt")
    yaml.default_flow_style = False
    yaml.explicit_start = False
    yaml.preserve_quotes = True  # respect the quotes set in style_scalars()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 1000  # prevent unwanted line wrapping
    # makes sure ruamel.yml to always emit double quoted strings """"
    yaml.representer.add_representer(DoubleQuotedScalarString, always_double_quoted)

    # blocks = [{key: value} for key, value in data.items()]
    blocks = [
        ruamel.yaml.comments.CommentedMap({key: value}) for key, value in data.items()
    ]
    fragments = []
    for block in blocks:
        text = io.StringIO()
        yaml.dump(block, text)
        # yaml.dump(data, stream)
        fragments.append(text.getvalue().rstrip())
    stream.write("\n\n".join(fragments) + "\n")
