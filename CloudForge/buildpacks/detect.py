"""
Language auto-detection for project deployments.

Scans a project directory to identify the programming language and select
the appropriate Dockerfile buildpack.
"""

import os
from dataclasses import dataclass


@dataclass
class DetectionResult:
    language: str
    confidence: float
    dockerfile_path: str
    detected_files: list[str]


# Detection rules: (file pattern, language, confidence boost)
DETECTION_RULES = [
    ("requirements.txt", "python", 0.9),
    ("Pipfile", "python", 0.85),
    ("pyproject.toml", "python", 0.85),
    ("setup.py", "python", 0.8),
    ("manage.py", "python", 0.7),
    ("package.json", "node", 0.9),
    ("yarn.lock", "node", 0.85),
    ("package-lock.json", "node", 0.85),
    ("go.mod", "go", 0.95),
    ("go.sum", "go", 0.8),
    ("pom.xml", "java", 0.9),
    ("build.gradle", "java", 0.9),
    ("build.gradle.kts", "java", 0.9),
    ("Cargo.toml", "rust", 0.9),
    ("Gemfile", "ruby", 0.9),
]

BUILDPACK_DIR = os.path.dirname(os.path.abspath(__file__))


def detect_language(project_path: str) -> DetectionResult:
    """Detect the programming language of a project by scanning for marker files."""
    scores: dict[str, float] = {}
    detected_files: dict[str, list[str]] = {}

    for filename, language, confidence in DETECTION_RULES:
        filepath = os.path.join(project_path, filename)
        if os.path.exists(filepath):
            scores[language] = max(scores.get(language, 0), confidence)
            detected_files.setdefault(language, []).append(filename)

    if not scores:
        # Fallback: scan file extensions
        ext_map = {
            ".py": "python",
            ".js": "node",
            ".ts": "node",
            ".go": "go",
            ".java": "java",
            ".rs": "rust",
            ".rb": "ruby",
        }
        for entry in os.listdir(project_path):
            _, ext = os.path.splitext(entry)
            if ext in ext_map:
                lang = ext_map[ext]
                scores[lang] = max(scores.get(lang, 0), 0.5)
                detected_files.setdefault(lang, []).append(entry)

    if not scores:
        return DetectionResult(
            language="unknown",
            confidence=0.0,
            dockerfile_path="",
            detected_files=[],
        )

    best_lang = max(scores, key=scores.get)
    dockerfile_path = os.path.join(BUILDPACK_DIR, best_lang, "Dockerfile")

    return DetectionResult(
        language=best_lang,
        confidence=scores[best_lang],
        dockerfile_path=dockerfile_path if os.path.exists(dockerfile_path) else "",
        detected_files=detected_files.get(best_lang, []),
    )


def list_supported_languages() -> list[str]:
    """Return list of languages with available buildpacks."""
    supported = []
    for entry in os.listdir(BUILDPACK_DIR):
        dockerfile = os.path.join(BUILDPACK_DIR, entry, "Dockerfile")
        if os.path.isdir(os.path.join(BUILDPACK_DIR, entry)) and os.path.exists(dockerfile):
            supported.append(entry)
    return sorted(supported)


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "."
    result = detect_language(path)
    print(f"Language:   {result.language}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Files:      {', '.join(result.detected_files)}")
    print(f"Buildpack:  {result.dockerfile_path or 'none'}")
