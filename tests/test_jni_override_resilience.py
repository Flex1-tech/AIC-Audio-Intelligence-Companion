"""Tests de résilience pour la configuration de surcharge JNI de Flet / Flutter.

Vérifie :
1. Cas où la section [tool.flet.flutter.pubspec.dependency_overrides] est absente.
2. Cas où la section est présente mais la clé 'jni' est absente.
3. Cas où la clé 'jni' est présente avec une version obsolète ou incorrecte (ex: 1.0.0).
4. Prise en charge native par le chargeur TOML de flet_cli.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path


def patch_pyproject_content(text: str) -> str:
    """Garantit la présence de la surcharge jni = "^1.1.0" dans pyproject.toml."""
    section = "[tool.flet.flutter.pubspec.dependency_overrides]"
    if section not in text:
        text = text.rstrip() + "\n\n" + section + '\njni = "^1.1.0"\n'
    else:
        if re.search(r"^\s*jni\s*=", text, re.MULTILINE):
            text = re.sub(r"^\s*jni\s*=.*$", 'jni = "^1.1.0"', text, flags=re.MULTILINE)
        else:
            text = text.replace(section, section + '\njni = "^1.1.0"')
    return text


def test_missing_section():
    content = """
[project]
name = "aic"
version = "2.1.0"

[tool.flet]
product = "AIC"
"""
    patched = patch_pyproject_content(content)
    data = tomllib.loads(patched)
    assert data["tool"]["flet"]["flutter"]["pubspec"]["dependency_overrides"]["jni"] == "^1.1.0"


def test_missing_key():
    content = """
[tool.flet.flutter.pubspec.dependency_overrides]
other_dep = "1.0.0"
"""
    patched = patch_pyproject_content(content)
    data = tomllib.loads(patched)
    assert data["tool"]["flet"]["flutter"]["pubspec"]["dependency_overrides"]["jni"] == "^1.1.0"
    assert data["tool"]["flet"]["flutter"]["pubspec"]["dependency_overrides"]["other_dep"] == "1.0.0"


def test_wrong_version():
    content = """
[tool.flet.flutter.pubspec.dependency_overrides]
jni = "1.0.0"
"""
    patched = patch_pyproject_content(content)
    data = tomllib.loads(patched)
    assert data["tool"]["flet"]["flutter"]["pubspec"]["dependency_overrides"]["jni"] == "^1.1.0"


def test_current_pyproject_contains_valid_override():
    """Vérifie que le pyproject.toml actuel du projet contient bien la configuration attendue."""
    pyproject_file = Path(__file__).resolve().parent.parent / "pyproject.toml"
    assert pyproject_file.exists(), "pyproject.toml introuvable"

    content = pyproject_file.read_text(encoding="utf-8")
    data = tomllib.loads(content)
    override = data.get("tool", {}).get("flet", {}).get("flutter", {}).get("pubspec", {}).get("dependency_overrides", {})
    assert override.get("jni") == "^1.1.0", f"Surcharge JNI invalide ou absente: {override}"
