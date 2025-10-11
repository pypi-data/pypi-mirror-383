# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Daniel Schmidt

import importlib.util
import logging
import os
import subprocess  # nosec B404
from pathlib import Path
from typing import Any

from ruamel import yaml

logger = logging.getLogger(__name__)


class VaultTag(yaml.YAMLObject):
    yaml_tag = "!vault"

    def __init__(self, v: str):
        self.value = v

    def __repr__(self) -> str:
        spec = importlib.util.find_spec("nac_yaml.ansible_vault")
        if spec:
            if "ANSIBLE_VAULT_ID" in os.environ:
                vault_id = os.environ["ANSIBLE_VAULT_ID"] + "@" + str(spec.origin)
            else:
                vault_id = str(spec.origin)
            t = subprocess.check_output(  # nosec B603, B607
                [
                    "ansible-vault",
                    "decrypt",
                    "--vault-id",
                    vault_id,
                ],
                input=self.value.encode(),
            )
            return t.decode()
        return ""

    @classmethod
    def from_yaml(cls, loader: Any, node: Any) -> str:
        return str(cls(node.value))


class EnvTag(yaml.YAMLObject):
    yaml_tag = "!env"

    def __init__(self, v: str):
        self.value = v

    def __repr__(self) -> str:
        env = os.getenv(self.value)
        if env is None:
            return ""
        return env

    @classmethod
    def from_yaml(cls, loader: Any, node: Any) -> str:
        return str(cls(node.value))


def load_yaml_files(paths: list[Path], deduplicate: bool = True) -> dict[str, Any]:
    """Load all yaml files from a provided directory."""

    def _load_file(file_path: Path, data: dict[str, Any]) -> None:
        with open(file_path) as file:
            if file_path.suffix in [".yaml", ".yml"]:
                data_yaml = file.read()
                y = yaml.YAML()
                y.preserve_quotes = True
                y.register_class(VaultTag)
                y.register_class(EnvTag)
                dict = y.load(data_yaml)
                merge_dict(dict, data)

    result: dict[str, Any] = {}
    for path in paths:
        if os.path.isfile(path):
            _load_file(path, result)
        else:
            for dir, _subdir, files in os.walk(path):
                for filename in files:
                    try:
                        _load_file(Path(dir, filename), result)
                    except:  # noqa: E722
                        logger.warning(f"Could not load file: {filename}")
    if deduplicate:
        result = deduplicate_list_items(result)
    return result


def merge_list_item(source_item: Any, destination: list[Any]) -> None:
    """Merge item into list."""
    if isinstance(source_item, dict):
        # check if we have an item in destination with matching primitives
        for dest_item in destination:
            match = True
            comparison = False
            unique_source = False
            unique_dest = False
            for k, v in source_item.items():
                if isinstance(v, dict) or isinstance(v, list):
                    continue
                if k not in dest_item:
                    unique_source = True
                    continue
                comparison = True
                if v != dest_item[k]:
                    match = False
            for k, v in dest_item.items():
                if isinstance(v, dict) or isinstance(v, list):
                    continue
                if k not in source_item:
                    unique_dest = True
                    continue
                comparison = True
                if v != source_item[k]:
                    match = False
            if comparison and match and not (unique_source and unique_dest):
                merge_dict(source_item, dest_item)
                return
    destination.append(source_item)


def merge_dict(source: dict[str, Any], destination: dict[str, Any]) -> dict[str, Any]:
    """Merge two nested dict/list structures."""
    if not source:
        return destination
    for key, value in source.items():
        if key not in destination or destination[key] is None:
            destination[key] = value
        elif isinstance(value, dict):
            if isinstance(destination[key], dict):
                merge_dict(value, destination[key])
        elif isinstance(value, list):
            if isinstance(destination[key], list):
                destination[key] += value
        elif value is not None:
            destination[key] = value
    return destination


def deduplicate_list_items(data: dict[str, Any]) -> dict[str, Any]:
    """Deduplicate list items."""
    for key, value in data.items():
        if isinstance(value, dict):
            deduplicate_list_items(value)
        elif isinstance(value, list):
            deduplicated_list: list[Any] = []
            for i in value:
                merge_list_item(i, deduplicated_list)
            for i in deduplicated_list:
                if isinstance(i, dict):
                    deduplicate_list_items(i)
            data[key] = deduplicated_list
    return data


def write_yaml_file(data: dict[str, Any], path: Path) -> None:
    try:
        with open(path, "w") as fh:
            y = yaml.YAML()
            y.explicit_start = True
            y.default_flow_style = False
            y.indent(mapping=2, sequence=4, offset=2)
            y.dump(data, fh)
    except:  # noqa: E722
        logger.error(f"Cannot write file: {path}")
