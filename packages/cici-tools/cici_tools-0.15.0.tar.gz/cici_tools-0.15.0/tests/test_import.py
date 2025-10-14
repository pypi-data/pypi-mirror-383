# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "cici",
        "cici._version",
        "cici.__main__",
        "cici.cli",
        "cici.cli.bundle",
        "cici.cli.readme",
        "cici.cli.schema",
        "cici.cli.update",
        "cici.config",
        "cici.config.project",
        "cici.config.project.models",
        "cici.config.project.serializers",
        "cici.config.user",
        "cici.constants",
        "cici.main",
        "cici.providers.gitlab.serializers",
        "cici.providers.gitlab.constants",
        "cici.providers.gitlab.utils",
        "cici.providers.gitlab.models",
        "cici.providers.gitlab",
        "cici.providers",
        "cici.schema",
        "cici.templates",
        "cici.utils",
    ],
)
def test_import_module(module_name):
    importlib.import_module(module_name)
