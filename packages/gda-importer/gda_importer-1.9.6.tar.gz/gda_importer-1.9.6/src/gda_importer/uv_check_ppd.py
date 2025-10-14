#!/bin/env python3

r"""Check whether UV config matches PPD config.

This standalone script is Geometric Data Analytics (c) 2024, available under AGPLv3,
regardless of the other contents of the package it was included with.
"""

import argparse
import logging
from importlib.metadata import PackageNotFoundError, version
from urllib.parse import quote

import toml
from packaging.requirements import SpecifierSet

from .models import PrivDep, make_token_vars, process_toml_dict

logging.basicConfig(format="%(levelname)s\t: %(message)s")
log = logging.getLogger(__package__)
log.setLevel(logging.WARNING)

description = (
    "Pull private python (pip) requirements using fallback GitLab authententicaton."
)

epilog = "See DEPENDENCIES.md and the example in private-deps.toml for more detail."


def checker(
    name: str,
    extras: list,
    dep: PrivDep,
    pyproject: dict,
    dofail: bool = True,
    url_name: bool = False,
    test_token: bool = False,
) -> bool:
    """Check whether the uv.tools entries in pyproject.toml match private-deps.toml."""
    try:
        uv_version = version("uv")
        uv_version_good = SpecifierSet(">=0.6.12")
        if uv_version not in uv_version_good:
            raise ValueError(
                f"uv version {uv_version} is not supported. Need {uv_version_good}"
            )
    except PackageNotFoundError:
        log.warning("uv is not installed.")

    extras_str = ""
    if extras is not None and len(extras) > 0:
        extras_str = "[" + ",".join(extras) + "]"

    url_path = quote(dep.gitlab_path, safe="")  # URLEncode the group and project name.
    fullurl = (
        f"https://{name}@{dep.gitlab_host}/api/v4/projects/{url_path}/packages/pypi/simple"
        if url_name
        else f"https://{dep.gitlab_host}/api/v4/projects/{url_path}/packages/pypi/simple"
    )
    fullver = SpecifierSet(dep.version_set)

    ideal_pyproject = f"""
# Your pyproject.toml to correspond with entry "{name}" should look like this:
[project]

dependencies = [
  "{name}{extras_str}{fullver}",
]

[tool.uv.sources]
{name} = {{ index = "{name}" }}

[[tool.uv.index]]
name = "{name}"
url = "{fullurl}"
explicit = true
"""
    log.info(ideal_pyproject)
    ideal = toml.loads(ideal_pyproject)

    # PPD. Make version comparison easier.
    if dofail and dep.version_set != str(fullver):
        raise ValueError(
            f"private-deps.toml should have version_set '{dep.version_set}' as '{fullver}'."
        )

    # Check the depependecies part.
    all_deps = pyproject["project"]["dependencies"]
    for option in pyproject["project"]["optional-dependencies"]:
        all_deps.extend(pyproject["project"]["optional-dependencies"][option])
    for entry in ideal["project"]["dependencies"]:
        if dofail and entry not in all_deps:
            raise ValueError(
                f'Private-dep "{entry}" must appear in dependencies or optional-dependencies.'
            )

    # Check sources
    if dofail and (
        "tool" not in pyproject
        or "uv" not in pyproject["tool"]
        or "sources" not in pyproject["tool"]["uv"]
    ):
        raise ValueError("pyprojec.toml requires section [tool.uv.sources]")
    for entry, value in ideal["tool"]["uv"]["sources"].items():
        if (
            dofail
            and dep.method == "wheel"
            and (
                entry not in pyproject["tool"]["uv"]["sources"]
                or pyproject["tool"]["uv"]["sources"][entry] != value
            )
        ):
            raise ValueError(
                f"pyproject.toml's [tool.uv.sources] should have entry '{name} = {{index = \"{name}\"}}'"
            )
        elif (
            dofail
            and dep.method == "source"
            and (
                entry not in pyproject["tool"]["uv"]["sources"]
                or "git" not in pyproject["tool"]["uv"]["sources"][entry]
            )
        ):
            raise ValueError(
                f"pyproject.toml's [tool.uv.sources] should have entry '{name} = {{git = \"{name}\" }}'"
                " and branch= or tag= or rev="
            )

    if dofail and "index" not in pyproject["tool"]["uv"]:
        raise ValueError("pyproject.toml requires sections [[tool.uv.index]]")

    for entry in ideal["tool"]["uv"]["index"]:
        if (
            dofail
            and dep.method == "wheel"
            and entry not in pyproject["tool"]["uv"]["index"]
        ):
            raise ValueError(f"""pyproject.toml should have entry
[[tool.uv.index]]
name = "{name}"
url = "{fullurl}"
explicit = true
""")

    if test_token:
        import os

        import requests

        _, uv_token = make_token_vars(name)
        if uv_token not in os.environ:
            raise ValueError(
                f"Token {uv_token} is not loaded yet in your env. Try '$(uv-check-ppd -e TOKEN)' to load it."
            )
        header = requests.head(fullurl, headers={"PRIVATE-TOKEN": os.environ[uv_token]})
        if header.status_code != requests.codes.ok:
            raise ValueError(
                f"Your token DOES NOT WORK for {name}. Please check {uv_token}"
            )
    return True


def main():
    """Run CLI."""
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-t",
        "--toml",
        type=str,
        default="private-deps.toml",
        help="Path to private deps TOML file.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase LogLevel verbosity, up to 3 times.",
    )
    parser.add_argument(
        "-p",
        "--pypt",
        type=str,
        default="pyproject.toml",
        help="Path to pyproject.toml file.",
    )

    parser.add_argument(
        "-N", "--nofail", action="store_true", help="Do not fail on check."
    )

    parser.add_argument(
        "-U", "--url_name", action="store_true", help="Require name in URL."
    )

    parser.add_argument(
        "-e", "--export", type=str, help="Output variable names to export into scripts."
    )

    parser.add_argument(
        "-T",
        "--test_token",
        action="store_true",
        help="Test that the authentication token works!",
    )

    parser.add_argument(
        "-k",
        "--keyring",
        type=str,
        help=(
            "Duplicate an entry in keyring, e.g. from a Personal Access Token.  "
            "Use as '-k username' of existing entry with the same hostname."
        ),
    )

    parser.add_argument(
        "-u",
        "--username",
        type=str,
        help="Override username for --export.",
    )

    args = parser.parse_args()

    assert args.verbose <= 2, "More than 2 `-v`'s is meaningless."
    log.setLevel(30 - 10 * args.verbose)
    log.info(f"Processing {args.toml}")
    # if args.method is not None:
    #    log.warning(f"Overriding methods with -m {args.method}")
    packages = process_toml_dict(toml.load(args.toml))
    pyproject = toml.load(args.pypt)
    for name, data in packages.items():
        checker(
            name,
            data["extras"],
            data["dep"],
            pyproject=pyproject,
            dofail=not args.nofail,
            url_name=args.url_name,
            test_token=args.test_token,
        )
        if args.export:
            uv_user_token, uv_pass_token = make_token_vars(name)
            export_username = args.username if args.username else name
            print(f"export {uv_user_token}={export_username}")
            print(f"export {uv_pass_token}={args.export}")
        if args.keyring:
            import keyring

            keyring_hostname = data["dep"].gitlab_host
            keyring_username = args.keyring
            keyring_password = keyring.get_password(keyring_hostname, keyring_username)
            if not keyring_password:
                log.error(f"No keyring entry at {keyring_hostname} {keyring_username}")
                exit(1)
            log.warning(
                f"Copying keyring entry {keyring_hostname} {keyring_username} -> {name}"
            )
            keyring.set_password(keyring_hostname, name, keyring_password)


if __name__ == "__main__":
    main()
