# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.9.6] - 2025-10-13

- Allow python 3.14

## [1.9.5] - 2025-05-14

- Allow python 3.13

## [1.9.4] - 2025-04-17

- Check that uv is sufficiently new.

## [1.9.2] - 2025-02-17

- Fix `uv-check-ppd -e` variable handling.

## [1.9.1] - 2025-02-17

- PyPI packaging bugfix.

## [1.9.0] - 2025-02-17

- Remove `token_var` option from private-deps, since we *must* use `UV_INDEX_PACKAGE_NAME_PASSWORD` for compatibility.
- Fix broken pydantic v1 validator.

## [1.8.1] - 2025-01-27

- Add `--test_token` to `uv-check-ppd` to verify that private tokens work.

## [1.8.0] - 2025-01-22

- Add `--url_name` to support testing the URL in the keyring case.

## [1.7.1] - 2025-01-22

- Add "--username" option to override usernames.

## [1.6.3] - 2025-01-21

- Add "--nofail" option to skip checks on `uv-check-ppd`.

## [1.6.0] - 2025-01-21

- Fix username matching in `uv-check-ppd`.
- Improve `--keyring` to easily duplicate keyring entries

## [1.5.0] - 2024-12-20

- Require keying.
- Add `--keyring` option to `uv-check-ppd`.
- Improve `--export` to be more usable.

## [1.4.1] - 2024-12-19

- Provide `--export` option to `uv-check-ppd` for injecting tokens into environment.

## [1.4.0] - 2024-12-18

- Provide new tool `uv-check-ppd` to check whether pyproject.toml and
  private-deps.toml are consistent with uv.
- Add formatting to `--dry_run` output to more easily create shell script.
- Quote-escape the command output for `--dry_run` and strip on execution.
- Add tests.

## [1.3.2] - 2024-11-07

- Support both Pydantic 1 and Pydantic 2.

## [1.3.1] - 2024-10-24

- Add `--uvpip` option to make `uv pip install` commands.
- Include placeholder for future `method=uv.tool` stanza.

## [1.3.0] - 2024-10-22

- Attempt to use keyring in pull-private-deps.
- Provide clearer error on fallback with no tokens.
- Note `uv` in ppinfo.

## [1.2.2] - 2024-10-17

- Fix docker tag.
- Avoid showing tokens with `--dry_run`

## [1.2.1] - 2024-10-16

- Update docs.

## [1.2.0] - 2024-10-16

- Validate toml configuration using Pydantic model
- Support multiple installation methods

## [1.1.0] - 2024-10-09

- Clean up docs for public release.

## [1.0.2] - 2024-10-09

- Various pipeline bugfixes.

## [1.0.0] - 2024-10-08

- Imported previous versions with working local pipeline.

## [0.0.0] - 2024-10-07

- Initialized project using [GDA-Cookiecutter](https://gitlab.geomdata.com/geomdata/gda-cookiecutter)
