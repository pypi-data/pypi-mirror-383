# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import difflib
import filecmp
import os
import shutil
from contextlib import contextmanager
from pathlib import Path

import pytest

from cici.constants import BASE_DIR
from cici.main import main as cici

FIXTURES_DIR = BASE_DIR / ".." / "tests" / "fixtures"


@contextmanager
def pushd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


@pytest.mark.parametrize(
    "platform,name",
    [
        (
            "gitlab",
            "helm",
        ),
        (
            "gitlab",
            "terraform",
        ),
        (
            "gitlab",
            "reports",
        ),
        (
            "gitlab",
            "list-anchors",
        ),
        (
            "gitlab",
            "service-key",
        ),
        (
            "gitlab",
            "job-variables",
        ),
    ],
)
def test_end_to_end_bundle(platform, name, tmp_path):
    fixture_dir = FIXTURES_DIR / platform / name
    test_dir = tmp_path
    # test_dir = fixture_dir

    test_cici_dir = test_dir / ".cici"
    test_cici_dir.mkdir()

    files = [".cici/.gitlab-ci.yml", *[path.name for path in fixture_dir.glob("*.yml")]]
    cici_config_file = fixture_dir / ".cici" / "config.yaml"
    if cici_config_file.exists():
        files.append(".cici/config.yaml")
    for file in files:
        shutil.copyfile(fixture_dir / file, test_dir / file)
    with pushd(test_dir):
        print([path.name for path in Path.cwd().glob("*")])
        cici(["bundle"])

    for file in files:
        diff = list(
            difflib.unified_diff(
                open(fixture_dir / file).read().splitlines(keepends=True),
                open(test_dir / file).read().splitlines(keepends=True),
                fromfile=f"{file}, expected",
                tofile=f"{file}, actual",
            )
        )
        if diff:
            raise ValueError("outputs are different:\n{}".format("".join(diff)))


@pytest.mark.parametrize(
    "platform,name",
    [
        (
            "gitlab",
            "library-validator",
        ),
    ],
)
def test_end_to_end_readme(platform, name, tmp_path):
    fixture_dir = FIXTURES_DIR / platform / name
    test_dir = tmp_path

    test_cici_dir = test_dir / ".cici"
    test_cici_dir.mkdir()

    files = [".cici/README.md.j2", ".cici/config.yaml", "README.md"]
    for file in files:
        shutil.copyfile(fixture_dir / file, test_dir / file)
    with pushd(test_dir):
        print([path.name for path in Path.cwd().glob("*")])
        cici(["readme"])

    match, mismatch, errors = filecmp.cmpfiles(
        fixture_dir, test_dir, files, shallow=True
    )
    print(match, mismatch, errors)
