"""Verify GitHub/HACS package metadata without loading Home Assistant."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "mcz_maestro"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hacs_manifest_has_required_keys():
    manifest = _json(COMPONENT / "manifest.json")
    required = {"domain", "name", "codeowners", "documentation", "issue_tracker", "version"}
    assert required <= manifest.keys()
    assert manifest["domain"] == COMPONENT.name
    assert manifest["codeowners"] == ["@NadeoGolf"]
    assert manifest["version"] == "0.21.1"
    assert manifest["issue_tracker"].startswith("https://github.com/")
    assert manifest["integration_type"] == "device"
    keys = list(manifest)
    assert keys[:2] == ["domain", "name"]
    assert keys[2:] == sorted(keys[2:])


def test_manifest_version_matches_constant():
    const = ast.parse((COMPONENT / "const.py").read_text(encoding="utf-8"))
    versions = [
        assignment.value.value
        for assignment in const.body
        if isinstance(assignment, ast.Assign)
        for target in assignment.targets
        if isinstance(target, ast.Name) and target.id == "INTEGRATION_VERSION"
        and isinstance(assignment.value, ast.Constant)
    ]
    assert versions == [_json(COMPONENT / "manifest.json")["version"]]


def test_hacs_json_is_current():
    hacs = _json(ROOT / "hacs.json")
    assert hacs["name"] == "MCZ Maestro Local"
    assert "render_readme" not in hacs
    assert not hacs.get("content_in_root", False)


def test_config_flow_has_english_and_french_translations():
    original = _json(COMPONENT / "strings.json")
    english = _json(COMPONENT / "translations/en.json")
    french = _json(COMPONENT / "translations/fr.json")
    assert original == english
    for language in (english, french):
        assert set(language["config"]["step"]["user"]["data"]) == {"host", "port"}
        assert set(language["options"]["step"]["init"]["data"]) == {
            "name", "model", "stove_type", "control_mode", "scan_interval"
        }
        assert "cannot_connect" in language["config"]["error"]
        assert "already_configured" in language["config"]["abort"]


def test_repo_has_supporting_files():
    for relpath in ("README.md", "LICENSE", "NOTICE.md", "CHANGELOG.md", "CONTRIBUTING.md",
                    "SECURITY.md", ".github/workflows/validate.yml", "docs/PUBLICATION_GITHUB.md"):
        assert (ROOT / relpath).is_file(), relpath
