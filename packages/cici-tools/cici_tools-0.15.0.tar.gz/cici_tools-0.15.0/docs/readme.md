# README generation

cici supports the generation of project READMEs from its configuration via the
`cici readme` command.

## `cici readme` command

!!! warning

    This command **WILL** overwrite your `README.md` file.

```sh
cici readme
```

## Setup

=== "GitLab CI/CD include"

    ```yaml
    # .gitlab-ci.yml
    include:
      - project: saferatday0/cici
        file:
          - cici-readme.yml
    ```

    Run `cici update` to pin to a stable version.

=== "pre-commit hook"

    ```yaml
    # .pre-commit-config.yaml
    repos:
      - repo: https://gitlab.com/saferatday0/cici
        rev: ""
        hooks:
          - id: cici-readme
    ```

    Run `pre-commit autoupdate` to pin to a stable version.

## Template customization

To customize the output, copy the default README template to
`.cici/README.md.j2` and modify as needed:

```jinja
# {{ name }} component

{%- include "brief.md.j2" %}
{%- include "description.md.j2" %}

{%- include "groups.md.j2" %}

{%- include "targets.md.j2" %}

{%- include "variables.md.j2" %}
```
