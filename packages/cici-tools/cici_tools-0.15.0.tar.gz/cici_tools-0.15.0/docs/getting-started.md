# Getting started

All **cici** configuration is managed by the `.cici` config directory. The
contents of this directory are part of your project and should be committed to
version control.

## The cici config file

cici's primary driver is the cici config file, located at `.cici/config.yaml`.
This file defines all available pipeline targets and how to configure them for
the target CI/CD system.

```sh
mkdir -p .cici
touch .cici/config.yaml
```

Here is a minimal example from the [`pages`
component](https://gitlab.com/saferatday0/library/pages):

```yaml
name: pages

repo_url: https://gitlab.com/saferatday0/library/pages

gitlab_project_path: saferatday0/library/pages

brief: >-
  Publish static sites to GitLab Pages.

description: |-
  GitLab Pages is a static site hosting service that allows you to publish
  websites directly from your GitLab repositories. It automatically builds
  and deploys static sites from your code using GitLab CI/CD pipelines,
  supporting popular static site generators like Jekyll, Hugo, Gatsby, and
  plain HTML/CSS/JavaScript.

  Key features include free hosting for public repositories, custom domain
  support, HTTPS encryption, and seamless integration with GitLab’s version
  control workflow. It’s commonly used for project documentation, personal
  blogs, portfolio sites, and company websites that don’t require server-side
  processing.

  This pipeline publishes the contents of a `public` directory to [GitLab
  Pages](https://docs.gitlab.com/ee/user/project/pages/#how-it-works) on the
  default branch. This ensures that documentation is always being built, but only
  published when desired.

  View the example site: https://saferatday0.gitlab.io/library/pages/

targets:
  - name: pages
    brief: >-
      Publish the contents of a `public` directory to
      [GitLab Pages](https://docs.gitlab.com/ee/user/project/pages/#how-it-works)
    groups:
      - documentation
```

More examples can be found in the [saferatday0
library](https://gitlab.com/saferatday0/library) such as:

- [saferatday0/library/container](https://gitlab.com/saferatday0/library/container/-/blob/main/.cici/config.yaml)
- [saferatday0/library/mkdocs](https://gitlab.com/saferatday0/library/mkdocs/-/blob/main/.cici/config.yaml)
- [saferatday0/library/python](https://gitlab.com/saferatday0/library/python/-/blob/main/.cici/config.yaml)

Read on to learn how to write your own.

## Component metadata

Some information about the component project is necessary for cici to function
correctly. All components require these fields.

```yaml
# .cici/config.yaml
name: example

repo_url: https://gitlab.com/example/example

gitlab_project_path: example/example

brief: >-
  Foo bar the bazz utility.

description: |-
  The fizzy buzzy lorem ipsum converts bar to bazz. Use this cool utility to
  do software things.
```

## Pipeline targets

```yaml
# ...
targets:
  - name: example-bazz
    brief: >-
      Run the bazz utility on the project
  # more targets ...
```

## Pipeline variables

```yaml
# ...
variables:
  EXAMPLE_BAZZ_OPTIONS:
    default: "-o option1"
    brief: Bar bazz utility options.
    description: |-
      Here is a lot more information about the example-bazz pipeline. This
      pipeline has been featured in several major films and has received
      accolades from the academy.
    examples:
      - value: -o option2 --verbose

  # more variables ...
```

## Supplemental GitLab CI file

At present, cici still relies on some native GitLab CI/CD syntax to render final
pipelines. This couples cici to GitLab at present, and we are working to remove
this requirement.

This file is located at `.cici/.gitlab-ci.yml`. Here is a minimal example from
the [`pages` component](https://gitlab.com/saferatday0/library/pages):

```yaml
# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

stages:
  - test
  - build
  - deploy

workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "push" && $CI_OPEN_MERGE_REQUESTS
      when: never
    - when: always

pages:
  stage: deploy
  image: "${CONTAINER_PROXY}busybox"
  variables:
    GIT_DEPTH: "1"
    GIT_STRATEGY: "none"
  cache: {}
  script: [":"]
  artifacts:
    paths:
      - public/
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

Fields in `.cici/config.yaml` take precedence over redundant fields in
`.cici/gitlab-ci.yml`.

More examples can be found in the [saferatday0
library](https://gitlab.com/saferatday0/library) such as:

- [detect-secrets](https://gitlab.com/saferatday0/library/detect-secrets/-/blob/main/.cici/.gitlab-ci.yml)
- [prettier](https://gitlab.com/saferatday0/library/prettier/-/blob/main/.cici/.gitlab-ci.yml)
- [python](https://gitlab.com/saferatday0/library/python/-/blob/main/.cici/.gitlab-ci.yml)
