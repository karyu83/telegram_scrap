import os

from src.pathing import resolve_in_workspace, resolve_workspace_dir


def test_resolve_workspace_dir_prefers_argument(monkeypatch):
    monkeypatch.setenv("TICC_WORKSPACE_DIR", "/env/workspace")
    assert resolve_workspace_dir("/explicit/workspace") == os.path.abspath("/explicit/workspace")


def test_resolve_workspace_dir_uses_env(monkeypatch):
    monkeypatch.delenv("TICC_WORKSPACE_DIR", raising=False)
    monkeypatch.setenv("OPENCLAW_WORKSPACE", "/home/ubuntu/.openclaw/workspace")

    resolved = resolve_workspace_dir()
    assert resolved == os.path.abspath("/home/ubuntu/.openclaw/workspace")


def test_resolve_in_workspace_for_relative_path():
    workspace = os.path.normpath("/workspace/project")
    resolved = resolve_in_workspace("logs", workspace)
    assert resolved == os.path.normpath("/workspace/project/logs")
