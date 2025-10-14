# Automatic pipeline updates

## `cici update` command

Update to the latest GitLab CI/CD `include` versions available.

```sh
cici update
```

```console
$ cici update
updated saferatday0/library/python to 0.5.1
updated saferatday0/library/gitlab from 0.1.0 to 0.2.2
```

cici currently checks the following files for version updates:

- `.gitlab-ci.yml`

## Setup

=== "GitLab CI/CD include"

    ```yaml
    # .gitlab-ci.yml
    include:
      - project: saferatday0/cici
        file:
          - cici-update.yml
    ```

    Run `cici update` to pin to a stable version.

=== "pre-commit hook"

    ```yaml
    # .pre-commit-config.yaml
    repos:
      - repo: https://gitlab.com/saferatday0/cici
        rev: ""
        hooks:
          - id: cici-update
    ```

    Run `pre-commit autoupdate` to pin to a stable version.
