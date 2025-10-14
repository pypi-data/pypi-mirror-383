# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Union

from ruamel.yaml.scalarstring import ScalarString


# Recursivley convert ruamel ScalarStrng objects into plain str """
# So that when ruamel.yaml gives us fancy objects like LiteralScalarString('foo'),
# they will be turned into plain "foo" which msgspec can handle
# test this frst, test for each of the ifs and make sure the nesting is right.
# do simplest tests first, so one that is empty etc. Need to verify.
def normalize_scalars(obj):
    if isinstance(obj, ScalarString):
        return str(obj)
    elif isinstance(obj, dict):
        return {normalize_scalars(k): normalize_scalars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_scalars(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(normalize_scalars(i) for i in obj)
    else:
        return obj


# bridge between raw YAML and ruamels quirky Python objects
# and the strict Job/File models
def normalize_all(data: dict) -> dict:
    # Apply all normalizations for comparisons
    return normalize_variables(normalize_jobs_in_data(data))


def normalize_variables(data: dict, *, inside_job: bool = False) -> dict:
    # Normalize variables: keep top-level structured, flatten job-level
    # inside_job is going to tell me if i am currently in a job definition or not
    if not isinstance(data, dict):
        return data

    # Detect job-level context to know top-level or job-level
    # if the dictionary has a stage: key, it is certainly a GitLab job definition
    # if the dictionary has a script: section it too means we are inside a job
    # once we know we are inside a job, the flag stays true yay
    is_job_block = (
        "stage" in data
        or "script" in data
        or "image" in data
        or "before_script" in data
    )
    inside_job = inside_job or is_job_block

    if "variables" in data and isinstance(data["variables"], dict):
        normalized: dict[str, Union[str, dict[str, Any]]] = {}
        for key, val in data["variables"].items():

            # ----------- TOP-LEVEL VARIABLES -----------
            # inside_job = False
            if not inside_job:
                if isinstance(val, dict):
                    new_val = {}
                    # Map brief -> description
                    if "brief" in val:
                        new_val["description"] = val["brief"]
                    elif "description" in val:
                        new_val["description"] = val["description"]
                    # Map default -> value
                    if "default" in val:
                        new_val["value"] = val["default"]
                    elif "value" in val:
                        new_val["value"] = val["value"]
                    # Ensure a value key always exists
                    new_val.setdefault("value", "")
                    normalized[key] = new_val
                elif isinstance(val, str):
                    normalized[key] = {"value": val}
                else:
                    normalized[key] = {"value": str(val)}

            # ----------- JOB-LEVEL VARIABLES -----------
            # inside_job = True
            else:
                # For jobs, we always flatten to simple key:value
                if isinstance(val, dict):
                    # If it has a "value" field, unwrap it
                    if "value" in val:
                        normalized[key] = val["value"]
                    elif "default" in val:
                        normalized[key] = val["default"]
                    else:
                        # Convert dicts to a string if nothing matches
                        normalized[key] = str(val)
                else:
                    normalized[key] = val
        data["variables"] = normalized

    # ----------- Recursive traversal -----------
    # walk throuogh the entire YAML tree not just the top level dictionary
    for k, v in list(data.items()):
        if isinstance(v, dict):
            data[k] = normalize_variables(v, inside_job=inside_job)
        elif isinstance(v, list):
            data[k] = [
                (
                    normalize_variables(i, inside_job=inside_job)
                    if isinstance(i, dict)
                    else i
                )
                for i in v
            ]
    return data


def normalize_jobs_in_data(data: dict) -> dict:
    # Ensure jobs is always a dict, not a list of dicts
    if "jobs" in data and isinstance(data["jobs"], list):
        merged = {}
        for item in data["jobs"]:
            if isinstance(item, dict):
                merged.update(item)
        data["jobs"] = merged
    return data
