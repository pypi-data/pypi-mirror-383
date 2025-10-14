# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0


import re
from pathlib import Path
from typing import Any, Optional, Union

import msgspec
import ruamel.yaml
from msgspec.structs import replace

from . import models as cici_config

decoder = msgspec.json.Decoder(type=cici_config.File)
image_fqdn_regex = re.compile(r"^[\w\.-]+/")


def inject_variable_names(variables: dict[str, dict]) -> dict[str, dict]:
    # make sure each variable has its 'name' field set from its key
    patched = {}
    for key, value in variables.items():
        # if value is None or not a dict, treat it as empty dict
        if not isinstance(value, dict):
            value = {}
        # only add name if missing
        value.setdefault("name", key)
        patched[key] = value
    return patched


def patch_image(image: str, container_proxy: str = "${CONTAINER_PROXY}") -> str:
    """Patch in $CONTAINER_PROXY to image unless the following are true:

    A: Does the image URL contain ${CONTAINER_PROXY} (the literal string)
    B: Is the image URL a fully-qualified container URL?
    C: Does the image already start with a variable?
    """

    if not image:
        return image
    if container_proxy in image:
        return image

    if image_fqdn_regex.match(image):
        return image

    if image.startswith("$"):
        return image

    return f"{container_proxy}{image}"


def loads(
    text: str,
    gitlab_ci_jobs: Optional[dict[str, Any]] = None,
    precommit_hooks: Optional[dict[str, Any]] = None,
) -> cici_config.File:
    # parse YAML into fully-typed File object
    if gitlab_ci_jobs is None:
        gitlab_ci_jobs = {}
    if precommit_hooks is None:
        precommit_hooks = {}

    yaml = ruamel.yaml.YAML(typ="safe")
    data = yaml.load(text)
    # verify targets exists even if empty
    data.setdefault("targets", [])

    # Inject precommit/gitlab includes into each target
    for target in data["targets"]:
        if target["name"] in precommit_hooks:
            target["precommit_hook"] = {"name": target["name"]}
        if target["name"] in gitlab_ci_jobs:
            target["gitlab_include"] = {"name": target["name"]}

    if "variables" in data:
        data["variables"] = inject_variable_names(data["variables"])

    # decode into file_struct
    file_struct = decoder.decode(msgspec.json.encode(data))

    # post process to patch CONTAINER_PROXY to container images
    patched_targets = []
    for target in file_struct.targets:
        if target.container is not None:
            patched_container = replace(
                target.container,
                image=patch_image(target.container.image),
            )
            patched_targets.append(replace(target, container=patched_container))
        else:
            patched_targets.append(target)

    return replace(file_struct, targets=patched_targets)


def load(
    file: Union[str, Path],
    gitlab_ci_jobs: Optional[dict[str, Any]] = None,
    precommit_hooks: Optional[dict[str, Any]] = None,
) -> cici_config.File:
    return loads(
        open(file).read(),
        gitlab_ci_jobs=gitlab_ci_jobs,
        precommit_hooks=precommit_hooks,
    )
