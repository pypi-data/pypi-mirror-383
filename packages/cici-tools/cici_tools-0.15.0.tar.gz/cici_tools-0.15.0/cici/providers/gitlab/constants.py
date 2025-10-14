# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from enum import Enum


class WhenChoices(str, Enum):
    ALWAYS = "always"
    ACCESS = "access"
    DEVELOPMENT = "development"
    IF_NOT_PRESENT = "if-not-present"
    NEVER = "never"
    ON_SUCCESS = "on_success"
    ON_FAILURE = "on_failure"
    OTHER = "other"
    PREPARE = "prepare"
    PRODUCTION = "production"
    PULL = "pull"
    PULL_PUSH = "pull-push"
    PUSH = "push"
    STAGING = "staging"
    START = "start"
    STOP = "stop"
    TESTING = "testing"
    VERIFY = "verify"


class CachePolicies(str, Enum):
    PULL = "pull"
    PUSH = "push"
    PULL_PUSH = "pull-push"


class DeploymentTiers(str, Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    TESTING = "testing"
    DEVELOPMENT = "development"
    OTHER = "other"


class EnvActions(str, Enum):
    START = "start"
    PREPARE = "prepare"
    STOP = "stop"
    VERIFY = "verify"
    ACCESS = "access"


class PullPolicies(str, Enum):
    ALWAYS = "always"
    IF_NOT_PRESENT = "if-not-present"
    NEVER = "never"


class RetryMax(int, Enum):
    ZERO = 0
    ONE = 1
    TWO = 2


class RetryWhen(str, Enum):
    ALWAYS = "always"
    UNKNOWN_FAILURE = "unknown_failure"
    SCRIPT_FAILURE = "stript_failure"
    API_FAILURE = "api_failure"
    STUCK_OR_TIMEOUT_FAILURE = "stuck_or_timeout_failure"
    RUNNER_SYSTEM_FAILURE = "runner_system_failure"
    RUNNER_UNSUPPORTED = "runner_unsupported"
    STALE_SCHEDULE = "stale_schedule"
    JOB_EXECUTION_TIMEOUT = "job_execution_timeout"
    ARCHIVED_FAILURE = "archived_failure"
    UNMET_PREREQUISITES = "umet_prerequisites"
    SCHEDULER_FAILURE = "scheduler_failure"
    DATA_INTEGRITY_FAILURE = "data_integrity_failure"


CI_FILE = ".gitlab-ci.yml"
