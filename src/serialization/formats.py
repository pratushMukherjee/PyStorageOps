"""
Multi-format serialization for storage metadata.

Supports JSON, YAML, and Protocol Buffers (as dict-based wire format).
Demonstrates familiarity with data serialization formats used in storage systems.
"""

import json

import yaml


def to_json(data: dict, pretty: bool = True) -> str:
    """Serialize data to JSON string."""
    return json.dumps(data, indent=2 if pretty else None, default=str)


def from_json(json_str: str) -> dict:
    """Deserialize JSON string to dict."""
    return json.loads(json_str)


def to_yaml(data: dict) -> str:
    """Serialize data to YAML string."""
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def from_yaml(yaml_str: str) -> dict:
    """Deserialize YAML string to dict."""
    return yaml.safe_load(yaml_str)


def to_protobuf_dict(data: dict) -> dict:
    """Convert storage metadata to Protocol Buffers-style wire format.

    This simulates how data would be structured for protobuf serialization,
    using snake_case field names and explicit typing as protobuf would.
    """
    wire = {
        "message_type": "StorageMetadata",
        "fields": {},
    }
    for key, value in data.items():
        if isinstance(value, list):
            wire["fields"][key] = {
                "type": "repeated",
                "value": [_convert_value(v) for v in value],
            }
        else:
            wire["fields"][key] = _convert_value(value)
    return wire


def from_protobuf_dict(wire: dict) -> dict:
    """Convert Protocol Buffers-style wire format back to dict."""
    result = {}
    for key, field in wire.get("fields", {}).items():
        if isinstance(field, dict) and field.get("type") == "repeated":
            result[key] = [_unconvert_value(v) for v in field["value"]]
        else:
            result[key] = _unconvert_value(field)
    return result


def _convert_value(value):
    if isinstance(value, dict):
        return {"type": "message", "value": {k: _convert_value(v) for k, v in value.items()}}
    elif isinstance(value, int):
        return {"type": "int64", "value": value}
    elif isinstance(value, float):
        return {"type": "double", "value": value}
    elif isinstance(value, str):
        return {"type": "string", "value": value}
    elif isinstance(value, bool):
        return {"type": "bool", "value": value}
    elif isinstance(value, list):
        return {"type": "repeated", "value": [_convert_value(v) for v in value]}
    return {"type": "string", "value": str(value)}


def _unconvert_value(field):
    if not isinstance(field, dict) or "type" not in field:
        return field
    if field["type"] == "message":
        return {k: _unconvert_value(v) for k, v in field["value"].items()}
    if field["type"] == "repeated":
        return [_unconvert_value(v) for v in field["value"]]
    return field["value"]
