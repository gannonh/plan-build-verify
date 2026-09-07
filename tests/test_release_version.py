import json
import shutil
from pathlib import Path

import pytest

from scripts.release_version import release

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo(tmp_path):
    shutil.copytree(ROOT / 'src/manifests', tmp_path / 'src/manifests')
    return tmp_path


def test_patch_preview_does_not_write(repo):
    files = list(repo.rglob('*.json'))
    before = {p: p.read_bytes() for p in files}
    current = json.loads((repo / 'src/manifests/claude/plugin.json').read_text())['version']
    major, minor, patch = map(int, current.split('.'))
    assert release(repo) == f'{major}.{minor}.{patch + 1}'
    assert {p: p.read_bytes() for p in files} == before


def test_apply_updates_all_versioned_manifests(repo):
    assert release(repo, '99.0.0', apply=True) == '99.0.0'
    for path in repo.rglob('*.json'):
        payload = json.loads(path.read_text())
        if 'version' in payload:
            assert payload['version'] == '99.0.0'
        for plugin in payload.get('plugins', []):
            if 'version' in plugin:
                assert plugin['version'] == '99.0.0'


@pytest.mark.parametrize('version', ['0.0.0', 'v1.0.0', '1.0', '01.0.0', '1.0.0;echo bad'])
def test_invalid_or_non_increasing_version_does_not_write(repo, version):
    before = {p: p.read_bytes() for p in repo.rglob('*.json')}
    with pytest.raises(ValueError):
        release(repo, version, apply=True)
    assert {p: p.read_bytes() for p in repo.rglob('*.json')} == before


def test_mismatched_versions_do_not_write(repo):
    path = repo / 'src/manifests/cursor/plugin.json'
    payload = json.loads(path.read_text())
    payload['version'] = '90.0.0'
    path.write_text(json.dumps(payload))
    before = {p: p.read_bytes() for p in repo.rglob('*.json')}
    with pytest.raises(ValueError, match='disagree'):
        release(repo, apply=True)
    assert {p: p.read_bytes() for p in repo.rglob('*.json')} == before


def test_same_version_is_rejected(repo):
    current = json.loads((repo / 'src/manifests/claude/plugin.json').read_text())['version']
    with pytest.raises(ValueError, match='must exceed'):
        release(repo, current, apply=True)
