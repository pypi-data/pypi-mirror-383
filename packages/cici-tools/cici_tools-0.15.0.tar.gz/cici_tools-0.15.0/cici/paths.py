# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Optional

from .constants import CONFIG_DIR_NAME


def get_cici_root_path(root_path: Optional[Path] = None) -> Path:
    if root_path is None:
        root_path = Path.cwd().absolute()
    return root_path


def get_cici_config_path(root_path: Optional[Path] = None) -> Path:
    return get_cici_root_path() / CONFIG_DIR_NAME


def get_cici_config_file_path(root_path: Optional[Path] = None) -> Path:
    return get_cici_config_path() / "config.yaml"


def get_cici_config_gitlab_ci_file_path(root_path: Optional[Path] = None) -> Path:
    return get_cici_config_path() / ".gitlab-ci.yml"


def get_cici_config_readme_template_path(root_path: Optional[Path] = None) -> Path:
    return get_cici_config_path() / "README.md.j2"


def get_pre_commit_hooks_path(root_path: Optional[Path] = None) -> Path:
    return get_cici_root_path() / ".pre-commit-hooks.yaml"


def get_readme_path(root_path: Optional[Path] = None) -> Path:
    return get_cici_root_path() / "README.md"
