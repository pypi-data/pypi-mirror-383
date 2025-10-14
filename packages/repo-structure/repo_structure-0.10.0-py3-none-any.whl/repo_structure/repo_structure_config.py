"""Library functions for repo structure config parsing."""

import copy
import pprint
import re
from dataclasses import dataclass, field
from typing import TextIO, Any

from ruamel import yaml as YAML
from jsonschema import validate, ValidationError, SchemaError

from .repo_structure_lib import (
    map_dir_to_rel_dir,
    RepoEntry,
    ConfigurationParseError,
    StructureRuleError,
    DirectoryMap,
    StructureRuleList,
    StructureRuleMap,
    BUILTIN_DIRECTORY_RULES,
    TemplateError,
)
from .repo_structure_schema import get_json_schema


@dataclass
class ConfigurationData:
    """Stores configuration data."""

    structure_rules: StructureRuleMap = field(default_factory=dict)
    directory_map: DirectoryMap = field(default_factory=dict)
    configuration_file_name: str = ""
    structure_rule_descriptions: dict[str, str] = field(default_factory=dict)
    directory_descriptions: dict[str, str] = field(default_factory=dict)

    def get_structure_rule_description(self, rule_name: str) -> str:
        """Get the description for a structure rule."""
        return self.structure_rule_descriptions.get(rule_name, "")

    def get_directory_description(self, directory: str) -> str:
        """Get the description for a directory."""
        return self.directory_descriptions.get(directory, "")


class Configuration:
    """Repo Structure configuration class."""

    def __init__(
        self,
        config_file: str,
        param1_is_yaml_string: bool = False,
        schema: dict[Any, Any] | None = None,
        verbose: bool = False,
    ):
        """Create new configuration object.

        Args:
              config_file (str): Path to the configuration file or configuration string.
              param1_is_yaml_string (bool): If true interprets config_file as contents not path.
              schema (dict[Any, Any]): An optional JSON schema file for schema verification.

        Exceptions:
            StructureRuleError: Raised for errors in structure rules.
            RepoStructureTemplateError: Raised for errors in repository structure templates.
            ConfigurationParseError: Raised for errors during the configuration parsing process.
        """
        if verbose:
            print("Loading configuration")
        if param1_is_yaml_string:
            yaml_dict = _load_repo_structure_yamls(config_file)
        else:
            yaml_dict = _load_repo_structure_yaml(config_file)

        if not yaml_dict:
            raise ConfigurationParseError

        if not schema:
            schema = get_json_schema()

        try:
            validate(instance=yaml_dict, schema=schema)
        except ValidationError as e:
            raise ConfigurationParseError(f"Bad config: {e.message}") from e
        except SchemaError as e:
            raise ConfigurationParseError(f"Bad schema: {e.message}") from e
        if verbose:
            print("Configuration validated successfully")

        if verbose:
            print("Parsing configuration data")

        structure_rules, structure_rule_descriptions = _parse_structure_rules(
            yaml_dict.get("structure_rules", {})
        )
        directory_map, directory_descriptions = _parse_directory_map(
            yaml_dict.get("directory_map", {})
        )

        self.config = ConfigurationData(
            structure_rules=structure_rules,
            directory_map=directory_map,
            structure_rule_descriptions=structure_rule_descriptions,
            directory_descriptions=directory_descriptions,
        )
        # Template parsing is expanded in-place and added as structure rules to the directory_map
        _parse_templates_to_configuration(
            yaml_dict.get("templates", {}),
            yaml_dict.get("directory_map", {}),
            self,
        )
        self._validate_directory_map_use_rules()

        if not param1_is_yaml_string:
            if config_file in self.config.structure_rules:
                raise ConfigurationParseError(
                    f"Conflicting Structure rule for {config_file}"
                    "- do not add the config manually."
                )

            self.config.configuration_file_name = config_file

        if verbose:
            # Print the parsed configuration pretty
            pprint.pprint(self.config.directory_map, indent=2)
            pprint.pprint(self.config.structure_rules, indent=2)
            print(
                f"Structure rules count: {len(self.config.structure_rules.keys())}, "
                f"Directory map count: {len(self.config.directory_map.keys())}"
            )
            print("Configuration parsed successfully")

    def _validate_directory_map_use_rules(self):
        existing_rules = self.config.structure_rules.keys()
        for directory, rule in self.config.directory_map.items():
            for r in rule:
                if r not in existing_rules and r not in BUILTIN_DIRECTORY_RULES:
                    raise ConfigurationParseError(
                        f"Directory mapping '{directory}' uses non-existing rule '{r}'"
                    )

    @property
    def structure_rules(self) -> StructureRuleMap:
        """Property for structure rules."""
        return self.config.structure_rules

    @property
    def directory_map(self) -> DirectoryMap:
        """Property for directory mappings."""
        return self.config.directory_map

    @property
    def configuration_file_name(self) -> str:
        """Property for configuration file name."""
        return self.config.configuration_file_name

    @property
    def structure_rule_descriptions(self) -> dict[str, str]:
        """Property for structure rule descriptions."""
        return self.config.structure_rule_descriptions

    @property
    def directory_descriptions(self) -> dict[str, str]:
        """Property for directory descriptions."""
        return self.config.directory_descriptions


def _load_repo_structure_yaml(filename: str) -> dict:
    with open(filename, "r", encoding="utf-8") as file:
        return _load_repo_structure_yamls(file)


def _load_repo_structure_yamls(yaml_string: str | TextIO) -> dict:
    yaml = YAML.YAML(typ="safe")
    return yaml.load(yaml_string)


def _parse_structure_rules(
    structure_rules_yaml: dict,
) -> tuple[StructureRuleMap, dict[str, str]]:

    def _validate_use_rule_not_dangling(rules: StructureRuleMap) -> None:
        for rule_key in rules.keys():
            for entry in rules[rule_key]:
                if entry.use_rule and entry.use_rule not in rules:
                    raise ConfigurationParseError(
                        f"use_rule '{entry.use_rule}' in entry '{entry.path.pattern}'"
                        "is not a valid rule key"
                    )

    def _validate_use_rule_only_recursive(rules: StructureRuleMap) -> None:
        for rule_key in rules.keys():
            for entry in rules[rule_key]:
                if entry.use_rule and entry.use_rule != rule_key:
                    raise ConfigurationParseError(
                        f"use_rule '{entry.use_rule}' in entry '{entry.path.pattern}'"
                        "is not recursive"
                    )

    rules, descriptions = _build_rules(structure_rules_yaml)
    _validate_use_rule_not_dangling(rules)
    _validate_use_rule_only_recursive(rules)

    return rules, descriptions


def _build_rules(
    structure_rules_yaml: dict,
) -> tuple[StructureRuleMap, dict[str, str]]:

    def _parse_directory_structure(
        directory_structure_yaml: list, structure_rule_list: StructureRuleList
    ) -> str:
        """Parse directory structure entries and return the description."""
        if not directory_structure_yaml:
            raise ConfigurationParseError("Structure rule cannot be empty")

        # First entry must be the description
        first_entry = directory_structure_yaml[0]
        if "description" not in first_entry or len(first_entry) != 1:
            raise ConfigurationParseError(
                "First entry in structure rule must be a description object "
                "with only 'description' field"
            )

        description = first_entry["description"]

        # Parse remaining entries (skip the description at index 0)
        for item in directory_structure_yaml[1:]:
            structure_rule_list.append(_parse_entry_to_repo_entry(item))

        return description

    rules: StructureRuleMap = {}
    descriptions: dict[str, str] = {}
    if not structure_rules_yaml:
        return rules, descriptions

    for rule in structure_rules_yaml:
        structure_rules: StructureRuleList = []
        description = _parse_directory_structure(
            structure_rules_yaml[rule], structure_rules
        )
        rules[rule] = structure_rules
        descriptions[rule] = description
    return rules, descriptions


def _get_pattern(entry: dict) -> str:
    if "require" in entry:
        return entry["require"]
    if "allow" in entry:
        return entry["allow"]
    # if "forbid" in entry:
    return entry["forbid"]


def _get_is_required(entry: dict) -> bool:
    if "allow" in entry:
        return False
    if "forbid" in entry:
        return False
    # if "require" in entry:
    return True


def _parse_entry_to_repo_entry(entry: dict) -> RepoEntry:
    if_exists = []
    companion = []
    entry_pattern = _get_pattern(entry)

    is_required = _get_is_required(entry)

    if "if_exists" in entry:
        if_exists = entry["if_exists"]

    if "companion" in entry:
        companion = entry["companion"]

    is_dir = entry_pattern.endswith("/")
    entry_pattern = entry_pattern[0:-1] if is_dir else entry_pattern

    try:
        compiled_pattern = re.compile(entry_pattern)
    except re.error as e:
        raise StructureRuleError(
            f"Bad pattern {entry_pattern}, failed to compile: {e}"
        ) from e

    result = RepoEntry(
        path=compiled_pattern,
        is_dir=is_dir,
        is_required=is_required,
        is_forbidden="forbid" in entry,
        use_rule=entry["use_rule"] if "use_rule" in entry else "",
    )
    for sub_entry in if_exists:
        result.if_exists.append(_parse_entry_to_repo_entry(sub_entry))

    for sub_entry in companion:
        result.companion.append(_parse_entry_to_repo_entry(sub_entry))

    return result


def _get_pattern_key(entry: dict) -> str:
    if "require" in entry:
        return "require"
    if "allow" in entry:
        return "allow"
    # if "forbid" in entry:
    return "forbid"


def _expand_template_entry(
    template_yaml: list[dict], expansion_key: str, expansion_var: str
) -> list[dict]:

    def _expand_entry(entry: dict, expansion_key: str, expansion_var: str):
        # Skip description entries
        if "description" in entry and len(entry) == 1:
            return entry
        k = _get_pattern_key(entry)
        entry[k] = entry[k].replace(f"{{{{{expansion_key}}}}}", expansion_var)
        return entry

    expanded_yaml: list[dict] = []
    for entry in template_yaml:
        entry = _expand_entry(entry, expansion_key, expansion_var)
        if "if_exists" in entry:
            entry["if_exists"] = _expand_template_entry(
                entry["if_exists"], expansion_key, expansion_var
            )
        if "companion" in entry:
            entry["companion"] = _expand_template_entry(
                entry["companion"], expansion_key, expansion_var
            )
        expanded_yaml.append(entry)
    return expanded_yaml


def _parse_use_template(
    dir_map_yaml: dict, directory: str, templates_yaml: dict, config: Configuration
):
    if "use_template" not in dir_map_yaml:
        return

    def _expand_template(dir_map_yaml, templates_yaml):

        def _max_values_length(expansion_map: dict[str, list[str]]) -> int:
            max_length = 0
            for _, values in expansion_map.items():
                max_length = max(max_length, len(values))
            return max_length

        expansion_map = dir_map_yaml["parameters"]
        structure_rules_yaml: list[dict] = []
        for i in range(_max_values_length(expansion_map)):
            if dir_map_yaml["use_template"] not in templates_yaml:
                raise TemplateError(
                    f"Template '{dir_map_yaml['use_template']}'"
                    "not found in templates"
                )
            entries = copy.deepcopy(templates_yaml[dir_map_yaml["use_template"]])
            for expansion_key, expansion_vars in expansion_map.items():
                index = i % len(expansion_vars)
                entries = _expand_template_entry(
                    entries, expansion_key, expansion_vars[index]
                )
            structure_rules_yaml.extend(entries)
        return structure_rules_yaml

    structure_rules_yaml = _expand_template(dir_map_yaml, templates_yaml)

    # Filter out description entries before parsing to RepoEntry
    structure_rule_list = [
        _parse_entry_to_repo_entry(entry)
        for entry in structure_rules_yaml
        if not ("description" in entry and len(entry) == 1)
    ]

    # fmt: off
    template_rule_name = \
        f"__template_rule_{map_dir_to_rel_dir(directory)}_{dir_map_yaml['use_template']}"
    config.config.structure_rules[template_rule_name] = structure_rule_list
    config.config.directory_map[directory].append(template_rule_name)


def _parse_directory_map(
    directory_map_yaml: dict,
) -> tuple[DirectoryMap, dict[str, str]]:

    def _parse_use_rule(rule: dict, dir_map: list[str]) -> None:
        if rule.keys() == {"use_rule"}:
            dir_map.append(rule["use_rule"])

    def _extract_description(value_list: list) -> str:
        """Extract and validate description from directory map entry."""
        if not value_list:
            raise ConfigurationParseError("Directory map entry cannot be empty")

        first_entry = value_list[0]
        if "description" not in first_entry or len(first_entry) != 1:
            raise ConfigurationParseError(
                "First entry in directory map must be a description"
                "object with only 'description' field"
            )

        return first_entry["description"]

    mapping: DirectoryMap = {}
    descriptions: dict[str, str] = {}

    for directory, value in directory_map_yaml.items():
        description = _extract_description(value)
        descriptions[directory] = description

        for r in value[1:]:  # Skip the description at index 0
            if mapping.get(directory) is None:
                mapping[directory] = []
            _parse_use_rule(r, mapping[directory])

    return mapping, descriptions


def _parse_templates_to_configuration(
    templates_yaml: dict, directory_map_yaml: dict, config: Configuration
) -> None:
    for directory, value in directory_map_yaml.items():
        for use_map in value:
            _parse_use_template(use_map, directory, templates_yaml, config)
