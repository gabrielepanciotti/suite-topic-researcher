"""Regression tests for packaged vista configuration."""
from __future__ import annotations

import json
from pathlib import Path

from topic_researcher_backend import vista


def test_default_vista_matches_node_config_when_present():
    node_config = Path(__file__).resolve().parents[2] / "node.config"
    assert json.loads(node_config.read_text(encoding="utf-8"))["vista"] == vista.DEFAULT_VISTA


def test_vista_spec_uses_default_when_node_config_is_absent(monkeypatch, tmp_path):
    monkeypatch.setattr(vista, "NODE_CONFIG_PATH", tmp_path / "node.config")

    spec = vista.load_vista_spec()

    assert [section.id for section in spec.sezioni] == [
        "cerca",
        "risultati",
        "salvati",
        "impostazioni",
    ]
