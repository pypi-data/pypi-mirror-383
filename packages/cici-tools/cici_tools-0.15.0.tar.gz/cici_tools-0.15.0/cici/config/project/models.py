# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Annotated, Dict, List, Optional

import msgspec
from msgspec import Meta


class PreCommitHookTarget(msgspec.Struct, frozen=True, kw_only=True):
    """Custom name for a pre-commit hook target."""

    name: Annotated[str, Meta(description="Name of pre-commit hook.")]


class GitLabIncludeTarget(msgspec.Struct, frozen=True, kw_only=True):
    """Custom name for a GitLab CI/CD Include target."""

    name: Annotated[str, Meta(description="Name of GitLab include target.")]


class Group(msgspec.Struct, frozen=True, kw_only=True):
    """A logical set of pipeline targets."""

    name: Annotated[str, Meta(description="Name of this group.")]
    brief: Annotated[
        str,
        Meta(
            description="Short, one-line description of this group. Supports Markdown."
        ),
    ] = ""
    description: Annotated[
        str,
        Meta(
            description="Multi-line, long-form description of this group. Supports Markdown."
        ),
    ] = ""


class Container(msgspec.Struct, frozen=True, kw_only=True):
    """Container runtime configuration for this target."""

    image: Annotated[str, Meta(description="Container image to use for this target.")]
    entrypoint: Annotated[
        List[str], Meta(description="Container entrypoint to use for this target.")
    ] = msgspec.field(default_factory=list)


class Target(msgspec.Struct, frozen=True, kw_only=True):
    """Defines a target pipeline to be generated."""

    name: Annotated[
        str,
        Meta(
            description="Name of a pipeline target. All lower-case, hyphen-separated (`kebab-case`) is expected."
        ),
    ]
    brief: Annotated[
        str,
        Meta(
            description="Short, one-line description of a pipeline target. Supports Markdown."
        ),
    ] = ""
    description: Annotated[
        str,
        Meta(
            description="Multi-line, long-form description of a pipeline target. Supports Markdown."
        ),
    ] = ""

    groups: Annotated[
        List[str],
        Meta(
            description="Denote a logical grouping of pipeline targets.",
        ),
    ] = msgspec.field(default_factory=list)
    tags: Annotated[
        List[str],
        Meta(description="Tags for curating jobs according to their purpose."),
    ] = msgspec.field(default_factory=list)

    container: Annotated[
        Optional[Container],
        Meta(description="Container runtime configuration for this pipeline target."),
    ] = None
    precommit_hook: Annotated[
        Optional[PreCommitHookTarget],
        Meta(
            description="Configuration for the pre-commit hook.",
            extra_json_schema=dict(deprecated=True),
        ),
    ] = None
    gitlab_include: Annotated[
        Optional[GitLabIncludeTarget],
        Meta(
            description="Configuration for the GitLab CI/CD include.",
            extra_json_schema=dict(deprecated=True),
        ),
    ] = None


class VariableExample(msgspec.Struct, frozen=True, kw_only=True):
    """An example of how the provided variable should be used."""

    value: Annotated[str, Meta(description="Example value for the variable.")]
    brief: Annotated[
        str, Meta(description="Short, one-line description of a variable example.")
    ] = ""


class Variable(msgspec.Struct, frozen=True, kw_only=True):
    """Defines a variable to be consumed by the target."""

    name: Annotated[
        str, Meta(description="Name of a variable.", examples=["PYTHON_VERSION"])
    ]
    brief: Annotated[
        str,
        Meta(
            description="Short, one-line description of a variable. Supports Markdown."
        ),
    ] = ""
    default: Annotated[str, Meta(description="Default value for this variable.")] = ""
    description: Annotated[
        str,
        Meta(
            description="Multi-line, long-form description of this variable. Support Markdown."
        ),
    ] = ""
    required: Annotated[
        bool, Meta(description="Is this variable required to use the pipeline?")
    ] = False
    examples: Annotated[
        List[VariableExample],
        Meta(description="List of examples to demonstrate this variable."),
    ] = msgspec.field(default_factory=list)


class File(msgspec.Struct, frozen=True, kw_only=True):
    """Top-level cici configuration object."""

    name: Annotated[
        str,
        Meta(
            description="Name of the component. All lower-case, hyphen-separated expected.",
            examples=["crosstool-ng"],
        ),
    ]

    repo_url: Annotated[
        str,
        Meta(
            description="Web URL for the source repository for this component.",
            examples=["https://gitlab.com/saferatday0/library/cxx"],
        ),
    ] = ""

    gitlab_project_path: Annotated[
        str,
        Meta(
            description="Full project path for this component on Gitlab.",
            examples=["saferatday0/library/python"],
            extra_json_schema=dict(deprecated=True),
        ),
    ] = ""

    brief: Annotated[
        str,
        Meta(
            description="Short, one-line description of a component. Supports Markdown."
        ),
    ] = ""
    description: Annotated[
        str,
        Meta(description="Multi-line description of a component. Supports Markdown."),
    ] = ""

    groups: Annotated[List[Group], Meta(description="List of groups to declare.")] = (
        msgspec.field(default_factory=list)
    )
    targets: Annotated[
        List[Target], Meta(description="List of pipeline targets to declare.")
    ] = msgspec.field(default_factory=list)
    variables: Annotated[
        Dict[str, Variable],
        Meta(description="Dictionary of input variables to declare."),
    ] = msgspec.field(default_factory=dict)
