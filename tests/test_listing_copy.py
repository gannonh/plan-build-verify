from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
LISTINGS = ROOT / "docs" / "marketplace-listings.md"


def test_readme_omits_npx_skills_add() -> None:
    assert "npx skills add" not in README.read_text(encoding="utf-8")


def test_listing_copy_omits_npx_skills_add() -> None:
    assert "npx skills add" not in LISTINGS.read_text(encoding="utf-8")


def test_listing_copy_has_identity_facts() -> None:
    text = LISTINGS.read_text(encoding="utf-8")
    assert "plan-build-verify" in text
    assert "MIT" in text
    assert "https://github.com/gannonh/plan-build-verify" in text


def test_listing_copy_has_submit_urls() -> None:
    text = LISTINGS.read_text(encoding="utf-8")
    assert "https://cursor.com/marketplace/publish" in text
    assert "https://platform.claude.com/plugins/submit" in text


def test_readme_keeps_git_marketplace_commands() -> None:
    text = README.read_text(encoding="utf-8")
    assert "/plugin marketplace add gannonh/plan-build-verify" in text
    assert "codex plugin marketplace add gannonh/plan-build-verify" in text


def test_readme_keeps_cursor_local_copy_command() -> None:
    text = README.read_text(encoding="utf-8")
    assert "cp -R plugins/cursor ~/.cursor/plugins/local/plan-build-verify" in text


def test_readme_notes_listing_submitted_not_public() -> None:
    text = README.read_text(encoding="utf-8")
    assert "_submitted, not public yet_" in text


def test_listing_copy_tells_readers_to_install_plugin() -> None:
    text = LISTINGS.read_text(encoding="utf-8")
    assert "install" in text.lower()
    assert "plan-build-verify" in text
