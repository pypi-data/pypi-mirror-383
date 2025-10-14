from typing import Dict, Any, Set
from collections import defaultdict


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case string to camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])


def wrap_metadata(value: Any) -> Dict[str, Any]:
    """Wrap a value in metadata format {key: value}."""
    return {"key": value}


def flat_to_nested_with_metadata(
    values: Dict[str, Any],
    prefix_map: Dict[str, str],
    root_metadata_fields: Set[str],
    nested_metadata_fields: Dict[str, Set[str]]
) -> Dict[str, Any]:
    """
    Generic function to convert flat dictionary to nested structure with metadata wrapping.

    This function handles conversion of flat dictionaries (typically from API responses or DataFrames)
    to nested structures suitable for API requests. It supports:
    - Prefix-based grouping (e.g., contact_information_* → contactInformation)
    - Metadata wrapping for specific fields (e.g., {key: value} format)
    - Snake_case to camelCase conversion

    Args:
        values: The flat dictionary to convert
        prefix_map: Map of snake_case prefixes to camelCase nested object names
            Example: {"contact_information": "contactInformation", "case_manager": "caseManager"}
        root_metadata_fields: Set of root-level field names (snake_case) that need metadata wrapping
            Example: {"cause_of_absence", "expected_duration"}
        nested_metadata_fields: Map of prefixes to sets of field names that need metadata wrapping
            Example: {"contact_information": {"location_type", "country"}}

    Returns:
        Nested dictionary with proper structure and metadata wrapping

    Example:
        Input (flat):
        {
            "cause_of_absence_key": 1,
            "contact_information_street": "Main St",
            "contact_information_country_key": 528,
            "hours_worked": 4
        }

        Output (nested):
        {
            "causeOfAbsence": {"key": 1},
            "contactInformation": {
                "street": "Main St",
                "country": {"key": 528}
            },
            "hoursWorked": 4
        }
    """
    if not isinstance(values, dict):
        return values

    data = dict(values)  # Create a copy

    # Target containers
    nested: Dict[str, Dict[str, Any]] = defaultdict(dict)
    root_out: Dict[str, Any] = {}

    for key, val in list(data.items()):
        if val is None:
            continue

        # 1) First, capture prefix-based keys (e.g., contact_information_street)
        matched_prefix = None
        for prefix in prefix_map:
            pref = prefix + "_"
            if key.startswith(pref):
                matched_prefix = prefix
                field_name = key[len(pref):]  # e.g., "street", "country_key"
                is_key = field_name.endswith("_key")
                clean = field_name[:-4] if is_key else field_name

                target_alias = prefix_map[prefix]  # e.g., "contactInformation"
                target_field_alias = snake_to_camel(clean)

                # Is it a metadata field?
                if is_key or clean in nested_metadata_fields.get(prefix, set()):
                    nested[target_alias][target_field_alias] = wrap_metadata(val)
                else:
                    nested[target_alias][target_field_alias] = val
                break

        if matched_prefix:
            continue  # This key has been processed

        # 2) Root-level *_key and normal fields
        if key.endswith("_key"):
            clean = key[:-4]  # e.g., cause_of_absence
            alias = snake_to_camel(clean)  # e.g., causeOfAbsence
            if clean in root_metadata_fields:
                root_out[alias] = wrap_metadata(val)
            else:
                # Unknown *_key field, still wrap it in metadata format
                root_out[alias] = wrap_metadata(val)
        else:
            # Plain root field
            root_out[snake_to_camel(key)] = val

    # 3) Combine results
    out = {**root_out}
    for obj_alias, obj_dict in nested.items():
        if obj_dict:  # Only add if not empty
            out[obj_alias] = obj_dict

    return out
