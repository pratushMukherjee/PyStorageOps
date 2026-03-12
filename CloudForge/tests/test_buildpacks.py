"""Tests for buildpack language detection."""

import os
import tempfile

import pytest

sys_path_setup = True  # conftest handles sys.path

from buildpacks.detect import detect_language, list_supported_languages


class TestLanguageDetection:
    def test_detect_python_by_requirements(self):
        with tempfile.TemporaryDirectory() as td:
            open(os.path.join(td, "requirements.txt"), "w").close()
            open(os.path.join(td, "main.py"), "w").close()
            result = detect_language(td)
            assert result.language == "python"
            assert result.confidence >= 0.9

    def test_detect_node_by_package_json(self):
        with tempfile.TemporaryDirectory() as td:
            open(os.path.join(td, "package.json"), "w").close()
            result = detect_language(td)
            assert result.language == "node"
            assert result.confidence >= 0.9

    def test_detect_go_by_go_mod(self):
        with tempfile.TemporaryDirectory() as td:
            open(os.path.join(td, "go.mod"), "w").close()
            result = detect_language(td)
            assert result.language == "go"
            assert result.confidence >= 0.95

    def test_detect_java_by_pom(self):
        with tempfile.TemporaryDirectory() as td:
            open(os.path.join(td, "pom.xml"), "w").close()
            result = detect_language(td)
            assert result.language == "java"
            assert result.confidence >= 0.9

    def test_detect_unknown_empty_dir(self):
        with tempfile.TemporaryDirectory() as td:
            result = detect_language(td)
            assert result.language == "unknown"
            assert result.confidence == 0.0

    def test_detect_by_file_extension_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            open(os.path.join(td, "app.py"), "w").close()
            result = detect_language(td)
            assert result.language == "python"
            assert result.confidence == 0.5

    def test_list_supported_languages(self):
        languages = list_supported_languages()
        assert "python" in languages
        assert "node" in languages
        assert "go" in languages
        assert "java" in languages

    def test_detection_returns_dockerfile_path(self):
        with tempfile.TemporaryDirectory() as td:
            open(os.path.join(td, "requirements.txt"), "w").close()
            result = detect_language(td)
            assert result.dockerfile_path.endswith("Dockerfile")
