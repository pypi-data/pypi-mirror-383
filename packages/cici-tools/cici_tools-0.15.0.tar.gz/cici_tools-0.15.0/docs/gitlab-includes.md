# GitLab CI/CD Includes

cici supports rendering GitLab CI/CD include files. This is the mechanism in
GitLab that predated GitLab CI/CD Components for sharing CI/CD code between
projects.

This is the only supported output format at present.

## How it works

cici renders out YAML files in the top-level repository directory. Each file
will be prefixed with the component name:

```console
$ ls -1 python-*.yml
python-autoflake.yml
python-black.yml
python-build-sdist.yml
python-build-wheel.yml
python-deptry.yml
python-docformatter.yml
python-import-linter.yml
python-isort.yml
python-mypy.yml
python-pyroma.yml
python-pytest.yml
python-twine-upload-pypi-oidc.yml
python-twine-upload-pypi-token.yml
python-twine-upload.yml
python-vulture.yml
```

Each YAML file is a GitLab CI/CD file that includes no other file references and
will not overwrite other included files. This allows them to be included as
needed to construct more complex pipelines from component parts.
