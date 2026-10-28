"""La migrazione additiva delle righe senza istanza (spec Life 2026-10-14 §4.2)."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest

from topic_researcher_backend import instances as ist

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "utility" / "assegna_istanza.py"


def _script():
    spec = importlib.util.spec_from_file_location("assegna_istanza", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _coda(righe: list[str]) -> Path:
    coda = Path(os.environ["LEARN_QUEUE_ROOT"])
    (coda / "topicResearcher.jsonl").write_text("\n".join(righe) + "\n", encoding="utf-8")
    return coda / "topicResearcher.jsonl"


def test_only_rows_without_instance_get_the_device_default_and_nothing_is_lost():
    path = _coda([
        json.dumps({"id": "1", "node_id": "topicResearcher"}),
        json.dumps({"id": "2", "node_id": "topicResearcher", "instance_id": "beta"}),
        "riga illeggibile",
    ])
    assert _script().main([]) == 0
    righe = path.read_text(encoding="utf-8").splitlines()
    assert json.loads(righe[0])["instance_id"] == "alfa"
    assert json.loads(righe[1])["instance_id"] == "beta"
    assert righe[2] == "riga illeggibile"
    assert len(list(path.parent.glob("*.bak-*-prima-istanza"))) == 1


def test_dry_run_writes_nothing():
    path = _coda([json.dumps({"id": "1"})])
    prima = path.read_text(encoding="utf-8")
    _script().main(["--dry-run"])
    assert path.read_text(encoding="utf-8") == prima


def test_unknown_instance_refuses():
    _coda([json.dumps({"id": "1"})])
    with pytest.raises(ist.IstanzaSconosciuta):
        _script().main(["--instance", "gamma"])
