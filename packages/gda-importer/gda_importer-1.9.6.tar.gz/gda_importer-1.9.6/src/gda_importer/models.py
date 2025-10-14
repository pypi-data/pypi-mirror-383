"""Validation model for a Private Dependency."""

import logging
import re
from typing import Literal

import pydantic
from packaging.requirements import SpecifierSet
from packaging.version import InvalidVersion, Version

if pydantic.version.VERSION.startswith("1."):
    from pydantic import BaseModel, ConfigDict, root_validator
elif pydantic.version.VERSION.startswith("2."):
    from pydantic import BaseModel, ConfigDict, model_validator
else:
    raise ImportError("Unsupported Pydantic version")

log = logging.getLogger(__package__)

# regex from PEP-345
# See https://packaging.python.org/en/latest/specifications/dependency-specifiers/#names
name_extras_re = re.compile(
    r"^(?P<name>[A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])($|\[(?P<extras>.*)\]$)",
    flags=re.IGNORECASE,
)


def parse_name_and_extras(name_and_extras):
    """Parse name and extras."""
    re_match = name_extras_re.match(name_and_extras)
    if re_match is None:
        raise ValueError(
            f"The header '{name_and_extras}' is not a valid as 'package-name[extras]'."
        )
    name = re_match.group("name")
    extras = re_match.group("extras")
    if extras is not None:
        extras = extras.split(",")
    return name, extras


def make_token_vars(name):
    """Produce a UV-compatible USERNAME and PASSWORD name for exporting variables."""
    name_flat = name.upper().replace("-", "_").replace(".", "_")
    uv_token_base = f"UV_INDEX_{name_flat}_"
    return uv_token_base + "USERNAME", uv_token_base + "PASSWORD"


def spec_meets_version(method: str, gitlab_spec: str | None, version_set: str | None):
    """Check whether a force_src, gitlab_spec, and version_set are compatible. Raises exceptions."""
    if version_set is None:
        version_set = ""
    pip_set = SpecifierSet(version_set)
    if method in ["source"]:
        if gitlab_spec is None or pip_set:
            raise ValueError(
                f"The method='{method}' prohibits a version_set (got '{pip_set}')"
                f" and requires a gitlab_spec (got {gitlab_spec})."
            )
        else:
            return True
    else:
        if gitlab_spec is None:
            return True
        else:
            try:
                # This allows the leading 'v'
                # https://peps.python.org/pep-0440/#preceding-v-character
                version = Version(gitlab_spec)
                if version in pip_set:
                    if version_set:
                        logging.warning(
                            f"gitlab_spec '{gitlab_spec}' is compatible with version_set '{pip_set}', "
                            "but it is unwise to use both."
                        )
                    return True
                else:
                    raise ValueError(
                        "Version implied by gitlab_spec "
                        "is not included in the version_set."
                    )
            except (InvalidVersion, TypeError):
                raise ValueError(
                    f"gitlab_spec '{gitlab_spec}' does not represent a release number. "
                    "The version_set cannot be checked. "
                    "This requires method='source'. "
                    "Be wary of dependency drift on branches. "
                )
    raise ValueError("Unknown Case")  # should never reach.


class PrivDep(BaseModel):
    """Validation model for a Private Dependency."""

    gitlab_host: str
    gitlab_path: str
    gitlab_spec: str | None = None
    version_set: str = ""
    always_pull: bool = False
    no_deps: bool = False
    method: Literal[
        "clone",
        "docker",
        "local",
        "source",
        "wheel",
    ] = "wheel"
    model_config = ConfigDict(extra="allow")

    if pydantic.version.VERSION.startswith("1."):

        @root_validator(pre=False)
        def check_release_vs_version(cls, inputs):
            """Check that release and version are consistent. Check that the method is set correctly."""
            assert (
                "force_src" not in inputs
            ), "The 'force_src' option is no longer supported. Use method='source' instead."
            spec_meets_version(
                inputs.get("method"),
                inputs.get("gitlab_spec"),
                inputs.get("version_set"),
            )
            return inputs

    elif pydantic.version.VERSION.startswith("2."):

        @model_validator(mode="after")
        def check_release_vs_version(self):
            """Check that release and version are consistent. Check that the method is set correctly."""
            assert (
                "force_src" not in self.__pydantic_extra__
            ), "The 'force_src' option is no longer supported. Use method='source' instead."
            spec_meets_version(self.method, self.gitlab_spec, self.version_set)
            return self


def process_toml_dict(toml_dict: dict):
    """Process a toml dict into a useful dictionary."""
    dependencies = {}
    for name_and_extras, spec_dict in toml_dict.items():
        name, extras = parse_name_and_extras(name_and_extras)
        log.info(f"Processing '{name}' with extras {extras}")
        if pydantic.version.VERSION.startswith("1."):
            dep = PrivDep.parse_obj(spec_dict)
            log.debug(dep.json())
        elif pydantic.version.VERSION.startswith("2."):
            dep = PrivDep.model_validate(spec_dict)
            log.debug(dep.model_dump_json())

        dependencies[name] = {"extras": extras, "dep": dep}
    return dependencies
