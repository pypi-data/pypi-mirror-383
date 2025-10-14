# Installation

cici is made available in various ways depending on the required use case.

## pip

Requires Python 3.9 or newer. cici is tested on [currently supported versions of
Python](https://devguide.python.org/versions/).

```sh
pip install cici-tools
```

The installation can be verified with `cici --version`.

```sh
cici --version
```

## docker

A version of cici packaged as Docker container is available.

```sh
docker pull registry.gitlab.com/saferatday0/cici
```

cici is the entrypoint for the container by default. The installation can be
verified by adding the `--version` flag.

```sh
docker run --rm -ti registry.gitlab.com/saferatday0/cici --version
```

## GitLab CI/CD includes

cici tools can be used as GitLab CI/CD pipelines:

```yaml
# .gitlab-ci.yml
repos:
  - project: saferatday0/cici
    file:
      - cici-bundle.yml
      - cici-readme.yml
      - cici-update.yml
```

## Pre-commit hooks

cici tools are available as pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://gitlab.com/saferatday0/cici
    rev: ""
    hooks:
      - id: cici-bundle
      - id: cici-readme
      - id: cici-update
```
