#!/usr/bin/env python3
# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import argparse
import json
import sys

import markdown
from jinja2 import Environment


def to_markdown(text):
    return markdown.markdown(text)


def get_ref_name(ref):
    return ref.split("/")[-1]


def get_ref_struct(schema, ref):
    return schema["$defs"][get_ref_name(ref)]


def render_header(level, text):
    return "{} {}".format("#" * level, text)


def clean_docstring(text):
    indent = 0
    lines = text.splitlines()
    if len(lines) > 1:
        index = 0
        while index < len(lines) and lines[index].replace(" ", "").replace("\t", ""):
            index += 1
            continue
        index -= 1
        indent = len(lines[index]) - len(lines[index].lstrip())

    newlines = [lines[0]]
    for line in lines[1:]:
        newlines.append(line[indent:].rstrip())
    return "\n".join(newlines)


def render_ref_link(ref):
    target = get_ref_name(ref)
    return "[{}](#{})".format(target, target.lower())


def render_ref_link_html(ref):
    target = get_ref_name(ref)
    return '<a href="#{}">{}</a>'.format(target.lower(), target)


def render_property_default(propertydata):
    default = propertydata.get("default", "")
    return default


def render_property_type(propertydata):
    propertytype = propertydata.get("type", "string")
    if propertytype == "array":
        if "type" in propertydata["items"]:
            reftype = propertydata["items"]["type"]
        elif "$ref" in propertydata["items"]:
            reftype = render_ref_link_html(propertydata["items"]["$ref"])
        else:
            raise NotImplementedError("no item type defined")
        return reftype + " " + propertytype
    elif propertydata.get("anyOf"):
        anyof = propertydata.get("anyOf")
        reftype = next(of["type"] for of in anyof if "type" in of and "$ref" not in of)
        refref = next(of["$ref"] for of in anyof if "$ref" in of and "type" not in of)
        reflink = render_ref_link_html(refref)
        if reftype == "null":
            return reflink
        else:
            raise NotImplementedError("not sure how to handle anyOf")
    return propertytype


TABLE_TEMPLATE = """
<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    {% for property in properties -%}
    <tr>
      <td><strong><code>{{ property.field }}</code></strong>{% if property.required -%}*{% endif -%}
        {% if property.type -%}<br/><em>{{ property.type }}</em>{% endif -%}
        {% if property.deprecated -%}<br/><em>(deprecated)</em>{% endif -%}
      </td>
      <td>
        {% if property.default -%}<code>{{ property.default }}</code>{% endif -%}
      </td>
      <td>
        {{ property.description | markdown -}}
        {% for example in property.examples -%}
        <pre><code>{{ example }}</code></pre>
        {% endfor -%}
      </td>
    </tr>
    {% endfor -%}
  </tbody>
</table>
"""


def render_property_table(struct):
    env = Environment()
    env.filters["markdown"] = to_markdown
    template = env.from_string(TABLE_TEMPLATE)
    properties = []
    for propertyname, propertydata in struct["properties"].items():
        default = render_property_default(propertydata)
        properties.append(
            {
                "field": propertyname,
                "type": render_property_type(propertydata),
                "default": str(default) if str(default) else "",
                "description": propertydata.get("description", ""),
                "examples": propertydata.get("examples", ""),
                "required": not str(default),
                "deprecated": propertydata.get("deprecated", False),
            }
        )

    return template.render(properties=properties)


def render_struct_blocks(struct, header_level):
    blocks = []
    if "description" in struct:
        blocks.append(clean_docstring(struct["description"]))
    blocks.append(render_property_table(struct))
    return blocks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType("r"))
    parser.add_argument(
        "-o", "--output-file", type=argparse.FileType("w"), default=sys.stdout
    )
    parser.add_argument("-p", "--package-path")
    parser.add_argument("-l", "--header-level", type=int, metavar="NUM", default=1)
    parser.add_argument("-t", "--title")
    parser.add_argument("-d", "--description")
    args = parser.parse_args()

    schema = json.load(args.input_file)

    blocks = []

    if args.title:
        blocks.append(render_header(args.header_level, args.title))

    if args.description:
        blocks.append(args.description)

    first_name = get_ref_name(schema["$ref"])
    first_struct = schema["$defs"].pop(first_name)

    blocks.extend(
        [
            render_header(args.header_level + 1, first_name),
            *render_struct_blocks(first_struct, args.header_level),
        ]
    )

    for structname, struct in sorted(schema["$defs"].items()):
        blocks.extend(
            [
                render_header(args.header_level + 1, struct["title"]),
                *render_struct_blocks(struct, args.header_level + 1),
            ]
        )

    args.output_file.write("\n\n".join(blocks) + "\n")


if __name__ == "__main__":
    main()
