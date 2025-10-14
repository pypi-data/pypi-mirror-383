# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import pytest
import ruamel.yaml

from cici.providers.gitlab.normalizers import (
    normalize_jobs_in_data,
    normalize_scalars,
    normalize_variables,
)
from cici.providers.gitlab.serializers import add_config_variables

#
#   Tests for normalize_scalar
#


@pytest.mark.parametrize(
    "input_yaml, output_yaml",
    [
        (
            "{}",
            {},
        ),
    ],
)
def test_normalize_scalar_ruamel(input_yaml, output_yaml):
    yaml = ruamel.yaml.YAML()
    ruamel_data = yaml.load(input_yaml)
    result = normalize_scalars(ruamel_data)
    assert output_yaml == result


@pytest.mark.parametrize(
    "input_yaml, output_yaml",
    [
        (
            '"test-key": "test-value"',
            {"test-key": "test-value"},
        ),
    ],
)
def test_normalize_scalar_dict(input_yaml, output_yaml):
    yaml = ruamel.yaml.YAML()
    ruamel_data = yaml.load(input_yaml)
    result = normalize_scalars(ruamel_data)
    assert output_yaml == result


@pytest.mark.parametrize(
    "input_yaml, output_yaml",
    [
        (
            'outer-test: {"inner-test-key": "inner-test-value"}',
            {"outer-test": {"inner-test-key": "inner-test-value"}},
        ),
    ],
)
def test_normalize_scalar_nested_dict(input_yaml, output_yaml):
    yaml = ruamel.yaml.YAML()
    ruamel_data = yaml.load(input_yaml)
    result = normalize_scalars(ruamel_data)
    assert output_yaml == result


@pytest.mark.parametrize(
    "input_yaml, output_yaml",
    [
        (
            """
            - one
            - two
            - 3
            """,
            ["one", "two", 3],
        ),
    ],
)
def test_normalize_scalar_list(input_yaml, output_yaml):
    yaml = ruamel.yaml.YAML()
    ruamel_data = yaml.load(input_yaml)
    result = normalize_scalars(ruamel_data)
    assert output_yaml == result


@pytest.mark.parametrize(
    "input_yaml, output_yaml",
    [
        (
            """
            -
              - a
              - b
            - c
            """,
            [["a", "b"], "c"],
        ),
    ],
)
def test_normalize_scalar_nested_list(input_yaml, output_yaml):
    yaml = ruamel.yaml.YAML()
    ruamel_data = yaml.load(input_yaml)
    result = normalize_scalars(ruamel_data)
    assert output_yaml == result


# ruamel.yaml's safe loader never returns tuples thus testing w/o ruamel YAML
@pytest.mark.parametrize(
    "input_obj, output",
    [
        # simple flat tuples
        ((1, 2, 3), (1, 2, 3)),
        (("a", "b", "c"), ("a", "b", "c")),
        # nested tuples
        (((1, 2), (3, 4)), ((1, 2), (3, 4))),
        ((("a", "b"), ("c", "d")), (("a", "b"), ("c", "d"))),
        # deeply nested tuple
        ((1, (2, (3, (4,)))), (1, (2, (3, (4,))))),
    ],
)
def test_normalize_scalar_tuple(input_obj, output):
    assert normalize_scalars(input_obj) == output


@pytest.mark.parametrize(
    "input_yaml, output",
    [
        (
            # ruamel DoubleQuotedScalarString object -> Python plain str
            'message: "test message"',
            {"message": "test message"},
        ),
        (
            # ruamel SingleQuotedScalarString -> Python plain str
            "message: 'test message'",
            {"message": "test message"},
        ),
        (
            # fancy ruamel objects -> normal str key
            '"testing message": hello!',
            {"testing message": "hello!"},
        ),
        (
            # ruamel FoldedScalarString (>) -> plain str
            "test message: >\n line1\n line2\n",
            {"test message": "line1 line2\n"},
        ),
        (
            # ruamel FoldedScalarString (>) nested -> plain str
            "items:\n  - >\n    line1\n    line2\n  - value2",
            {"items": ["line1 line2\n", "value2"]},
        ),
        (
            # ruamel LiteralScalarString (|) -> plain str with preserved newlines
            "test message: |\n line1\n line2\n",
            {"test message": "line1\nline2\n"},
        ),
        (
            # ruamel LiteralScalarString (|) nested -> plain str with preserved newlines
            "items:\n  - >\n    line1\n    line2\n  - value2",
            {"items": ["line1 line2\n", "value2"]},
        ),
        (
            # nested single quoted string in a list -> Python plain str
            "items:\n"
            "  - 'first'\n"
            "  - 'second'\n"
            "  - nested:\n"
            "      - 'third'\n",
            {"items": ["first", "second", {"nested": ["third"]}]},
        ),
    ],
)
def test_normalize_scalar_scalarstring(input_yaml, output):
    yaml = ruamel.yaml.YAML(typ="rt")
    ruamel_data = yaml.load(input_yaml)
    result = normalize_scalars(ruamel_data)
    assert output == result


@pytest.mark.parametrize(
    "input_obj, output",
    [
        (
            # Stages untouched
            {"stages": ["build", "test"]},
            {"stages": ["build", "test"]},
        ),
        (
            # empty jobs list becomes dict
            {"jobs": []},
            {"jobs": {}},
        ),
        (
            # jobs as list of dicts become merged dict
            {
                "jobs": [
                    {"job1": {"script": "echo hello"}},
                    {"job2": {"script": "echo later"}},
                ]
            },
            {
                "jobs": {
                    "job1": {"script": "echo hello"},
                    "job2": {"script": "echo later"},
                }
            },
        ),
        (
            # jobs already a dict remain unchanged
            {"jobs": {"job1": {"script": "echo hello"}}},
            {"jobs": {"job1": {"script": "echo hello"}}},
        ),
    ],
)
def test_normalize_jobs_in_data(input_obj, output):
    assert normalize_jobs_in_data(input_obj) == output


@pytest.mark.parametrize(
    "input_yaml, expected",
    [
        # plain string var normalized to {"value": "..."}
        (
            """
            variables:
              SIMPLE_VAR: "hello"
            """,
            {"variables": {"SIMPLE_VAR": {"value": "hello"}}},
        ),
        # dict with value + description preserved as-is
        (
            """
            variables:
              MY_VAR:
                description: "Some description"
                value: "123"
            """,
            {
                "variables": {
                    "MY_VAR": {"description": "Some description", "value": "123"}
                }
            },
        ),
        # dict with only description should auto-add empty value
        (
            """
            variables:
              BAD_VAR:
                description: "Missing value"
            """,
            {"variables": {"BAD_VAR": {"description": "Missing value", "value": ""}}},
        ),
        # completely empty var should not become {}
        (
            """
            variables:
              EMPTY_VAR: {}
            """,
            {"variables": {"EMPTY_VAR": {"value": ""}}},
        ),
    ],
)
def test_normalize_variables_cases(input_yaml, expected):
    yaml = ruamel.yaml.YAML(typ="safe")
    ruamel_data = yaml.load(input_yaml)
    result = normalize_variables(ruamel_data)
    assert result == expected


@pytest.mark.parametrize(
    "config_vars, expected",
    [
        (
            {
                "OPENTOFU_MODULE_VERSION": {
                    "brief": "Opentofu module version.",
                    "default": "${CI_COMMIT_TAG}",
                },
                "OPENTOFU_MODULE_NAME": {
                    "brief": "Opentofu module project name.",
                    "default": "${CI_PROJECT_NAME}",
                },
                "OPENTOFU_MODULE_DIR": {
                    "brief": "Opentofu module project directory.",
                    "default": "${CI_PROJECT_DIR}",
                },
            },
            # Expected normalized output
            {
                "OPENTOFU_MODULE_VERSION": {
                    "description": "Opentofu module version.",
                    "value": "${CI_COMMIT_TAG}",
                },
                "OPENTOFU_MODULE_NAME": {
                    "description": "Opentofu module project name.",
                    "value": "${CI_PROJECT_NAME}",
                },
                "OPENTOFU_MODULE_DIR": {
                    "description": "Opentofu module project directory.",
                    "value": "${CI_PROJECT_DIR}",
                },
            },
        ),
    ],
)
def test_add_and_normalize_variables_from_config(config_vars, expected):
    data = {"stages": ["test"], "variables": {}}

    # make a cici_config_file like object with variables in it
    class MockConfig:
        def __init__(self, vars_dict):
            self.variables = vars_dict

    mock_conif = MockConfig(config_vars)

    # do the part when config merged with vars and then normalize
    merged_stuff = add_config_variables(data, mock_conif)
    normalized = normalize_variables(merged_stuff)

    # top level variables should have description + value and not be {} (empty)
    for k, v in expected.items():
        assert k in normalized["variables"], f"{k} missing in nomralized output"
        assert "description" in normalized["variables"][k]
        assert "value" in normalized["variables"][k]
        assert normalized["variables"][k] == v
