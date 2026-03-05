"""Tests for multi-format serialization."""

from src.serialization.formats import (
    from_json,
    from_protobuf_dict,
    from_yaml,
    to_json,
    to_protobuf_dict,
    to_yaml,
)


class TestSerialization:
    SAMPLE_DATA = {
        "device": "test-vol",
        "block_size": 4096,
        "block_count": 1024,
        "files": [
            {"name": "file1.txt", "size": 100},
            {"name": "file2.txt", "size": 200},
        ],
    }

    def test_json_roundtrip(self):
        json_str = to_json(self.SAMPLE_DATA)
        restored = from_json(json_str)
        assert restored == self.SAMPLE_DATA

    def test_yaml_roundtrip(self):
        yaml_str = to_yaml(self.SAMPLE_DATA)
        restored = from_yaml(yaml_str)
        assert restored == self.SAMPLE_DATA

    def test_protobuf_dict_roundtrip(self):
        wire = to_protobuf_dict(self.SAMPLE_DATA)
        assert wire["message_type"] == "StorageMetadata"
        restored = from_protobuf_dict(wire)
        assert restored["device"] == "test-vol"
        assert restored["block_size"] == 4096

    def test_json_pretty_format(self):
        json_str = to_json({"key": "value"}, pretty=True)
        assert "\n" in json_str

    def test_json_compact_format(self):
        json_str = to_json({"key": "value"}, pretty=False)
        assert "\n" not in json_str
