# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List, Optional, Union

import msgspec
from msgspec import field

from .constants import (
    CachePolicies,
    DeploymentTiers,
    EnvActions,
    RetryMax,
    RetryWhen,
    WhenChoices,
)


class AllowFailure(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    exit_codes: Union[int, list[int]] = field(default_factory=list)


class CoverageReport(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    coverage_format: str
    path: str


class ArtifactReports(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    coverage_report: Optional[CoverageReport] = None
    junit: Union[str, list[str]] = field(default_factory=list)
    terraform: str = ""
    container_scanning: str = ""


class Artifacts(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    name: str = ""
    exclude: List[str] = field(default_factory=list)
    expire_in: str = ""
    expose_as: str = ""
    public: bool = True
    paths: List[str] = field(default_factory=list)
    reports: Optional[ArtifactReports] = None
    untracked: bool = False
    when: WhenChoices = WhenChoices.ON_SUCCESS


class CacheKey(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    files: List[str] = field(default_factory=list)
    prefix: str = ""


class Cache(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    key: Union[str, CacheKey] = ""
    paths: List[str] = field(default_factory=list)
    untracked: bool = False
    unprotect: bool = False
    when: WhenChoices = WhenChoices.ON_SUCCESS
    policy: CachePolicies = CachePolicies.PULL_PUSH
    fallback_keys: List[str] = field(default_factory=list)


class EnvironmentKubernetes(
    msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True
):
    namespace: str = ""


class Environment(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    name: str
    url: str = ""
    on_stop: str = ""
    action: EnvActions = EnvActions.START
    auto_stop_in: str = ""
    kubernetes: Optional[EnvironmentKubernetes] = None
    deployment_tier: Optional[DeploymentTiers] = None


class Hooks(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    pre_get_sources_script: Union[str, list[Union[str, list[str]]]] = field(
        default_factory=list
    )


class IDToken(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    aud: Union[str, list[str]] = field(default_factory=list)


class Image(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True, tag="image"):
    name: str
    entrypoint: Union[str, list[str]] = field(default_factory=list)
    pull_policy: Union[str, list[str]] = field(default_factory=list)


class IncludeLocal(
    msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True, tag="local"
):
    local: str


class IncludeProject(
    msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True, tag="project"
):
    project: str
    ref: Optional[str] = None
    file: Union[str, list[str]] = field(default_factory=list)


class IncludeRemote(
    msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True, tag="remote"
):
    remote: str


class IncludeTemplate(
    msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True, tag="template"
):
    template: str


class RuleChanges(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    compare_to: str
    paths = List[str]


class Rule(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    if_: Optional[str] = msgspec.field(default=None, name="if")
    when: str = ""
    changes: Union[List[str], RuleChanges] = field(default_factory=list)
    exists: List[str] = field(default_factory=list)
    allow_feature: bool = False
    needs: Optional[Union[List[str], Dict[str, str]]] = None
    variables: Dict[str, str] = field(default_factory=dict)


class Retry(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    max: RetryMax = RetryMax.ZERO
    when: Union[RetryWhen, list[RetryWhen]] = RetryWhen.ALWAYS


class Variable(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    description: Optional[str] = None
    value: Optional[str] = None
    options: Optional[list[str]] = None
    expand: bool = True


class Service(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    name: str
    entrypoint: Optional[Union[str, list[str]]] = None
    command: Optional[Union[str, list[str]]] = None
    variables: Dict[str, Union[str, Variable]] = field(default_factory=dict)
    alias: Optional[str] = None
    pull_policy: Union[str, list[str]] = field(default_factory=list)


class Job(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    extends: Union[str, list[str]] = []
    stage: Optional[str] = None
    image: Optional[Union[str, Image]] = None
    services: List[Union[str, Service]] = field(default_factory=list)
    variables: Dict[str, Union[str, Variable]] = field(default_factory=dict)
    before_script: Union[str, list[Union[str, list[str]]]] = field(default_factory=list)
    script: Union[str, list[Union[str, list[str]]]] = field(default_factory=list)
    after_script: Union[str, list[Union[str, list[str]]]] = field(default_factory=list)
    allow_failure: Union[bool, AllowFailure] = False
    artifacts: Optional[Artifacts] = None
    coverage: str = ""
    cache: Optional[Cache] = None
    dependencies: Optional[list] = None
    environment: Union[str, Environment] = ""
    hooks: Optional[Hooks] = None
    id_tokens: Dict[str, IDToken] = field(default_factory=dict)
    interruptible: bool = False
    needs: Optional[list[str]] = None
    retry: Union[int, Retry] = 0
    resource_group: str = ""
    rules: List[Rule] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class Workflow(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    name: Optional[str] = None
    rules: List[Rule] = field(default_factory=list)


class Default(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    after_script: Union[str, list[Union[str, list[str]]]] = field(default_factory=list)
    artifacts: Optional[Artifacts] = None
    before_script: Union[str, list[Union[str, list[str]]]] = field(default_factory=list)
    cache: Optional[Cache] = None
    hooks: Optional[Hooks] = None
    image: Optional[Union[str, Image]] = None
    interruptible: bool = False
    retry: Union[int, Retry] = 0
    tags: List[str] = field(default_factory=list)


class File(msgspec.Struct, omit_defaults=True, frozen=True, kw_only=True):
    jobs: Dict[str, Job] = field(default_factory=dict)
    stages: List[str] = field(default_factory=list)
    include: Union[
        str, List[Union[IncludeLocal, IncludeProject, IncludeRemote, IncludeTemplate]]
    ] = msgspec.field(default_factory=list)
    workflow: Optional[Workflow] = None
    variables: Dict[str, Union[str, Variable]] = field(default_factory=dict)
    extras: Dict[str, Any] = field(default_factory=dict)
