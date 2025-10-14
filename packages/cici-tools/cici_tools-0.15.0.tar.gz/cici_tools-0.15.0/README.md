# saferatday0 cici

<!-- BADGIE TIME -->

[![pipeline status](https://img.shields.io/gitlab/pipeline-status/saferatday0/cici?branch=main)](https://gitlab.com/saferatday0/cici/-/commits/main)
[![coverage report](https://img.shields.io/gitlab/pipeline-coverage/saferatday0/cici?branch=main)](https://gitlab.com/saferatday0/cici/-/commits/main)
[![latest release](https://img.shields.io/gitlab/v/release/saferatday0/cici)](https://gitlab.com/saferatday0/cici/-/releases)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)

<!-- END BADGIE TIME -->

**cici**, short for **Continuous Integration Catalog
Interface**, is a framework and toolkit for managing the integration and
lifecycle of packaged CI/CD components in a software delivery pipeline.

cici enables the efficient sharing of CI/CD code in an organization, and
eliminates a major source of friction that otherwise leads to poor adoption of
automation and DevOps practices.

cici is a foundational component of [saferatday0](https://saferatday0.dev) and
powers the [saferatday0 library](https://gitlab.com/saferatday0/library).

## Installation

```sh
pip install cici-tools
```

## Usage

### `cici bundle`

Flatten `extends` keywords to make zero-dependency GitLab CI/CD files.

```bash
cici bundle
```

```console
$ cici bundle
⚡ python-autoflake.yml
⚡ python-black.yml
⚡ python-build-sdist.yml
⚡ python-build-wheel.yml
⚡ python-import-linter.yml
⚡ python-isort.yml
⚡ python-mypy.yml
⚡ python-pyroma.yml
⚡ python-pytest.yml
⚡ python-setuptools-bdist-wheel.yml
⚡ python-setuptools-sdist.yml
⚡ python-twine-upload.yml
⚡ python-vulture.yml
```

### `cici readme`

Generate a README for your pipeline project:

```bash
cici readme
```

To customize the output, copy the default README template to `README.md.j2` in
your project root and modify:

```j2
# {{ name }} pipeline

{%- include "brief.md.j2" %}
{%- include "description.md.j2" %}

{%- include "groups.md.j2" %}

{%- include "targets.md.j2" %}

{%- include "variables.md.j2" %}
```

### `cici update`

Update to the latest GitLab CI/CD `include` versions available.

```bash
cici update
```

```console
$ cici update
updated saferatday0/library/python to 0.5.1
updated saferatday0/library/gitlab from 0.1.0 to 0.2.2
```

## License

Copyright 2025 UL Research Institutes.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
