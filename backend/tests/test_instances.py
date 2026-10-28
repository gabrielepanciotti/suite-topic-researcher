"""Il contratto operatore (spec Life 2026-10-14 §4) sull'API, con due istanze finte."""
from __future__ import annotations

from fastapi.testclient import TestClient

from suite_learn_core.queue import InMemoryQueue
from suite_learn_core.types import Item

from topic_researcher_backend.api import get_lanciatore, get_queue
from topic_researcher_backend.app import app


class LanciatoreFinto:
    def __init__(self) -> None:
        self.chiamate: list[tuple[list[str], dict[str, str]]] = []

    def __call__(self, argv, env, log):
        self.chiamate.append((argv, env))
        return 4242


def _client():
    queue = InMemoryQueue()
    for titolo, istanza in [("a", "alfa"), ("b", "beta"), ("vecchia", None)]:
        p = queue.put("topicResearcher", Item(title=titolo, body="x", source_id=f"s:{titolo}"))
        queue._items[p.id] = p.model_copy(update={"instance_id": istanza})
    queue.put("altroNodo", Item(title="fuori", body="x", source_id="s:fuori"))
    lanciatore = LanciatoreFinto()
    app.dependency_overrides[get_queue] = lambda: queue
    app.dependency_overrides[get_lanciatore] = lambda: lanciatore
    return TestClient(app), lanciatore


def test_instances_lists_both_and_names_the_unreachable():
    client, _ = _client()
    per_id = {i["id"]: i for i in client.get("/api/instances").json()}
    assert per_id["alfa"]["status"] == "ok" and per_id["alfa"]["default"] is True
    assert per_id["alfa"]["channels"]["telegram_chat_id"] == -100123
    assert per_id["alfa"]["channels"]["bus_tenant"] == "alfa"
    assert per_id["beta"]["status"] == "unreachable"
    assert "path assente" in per_id["beta"]["reason"]


def test_read_without_instance_returns_all_with_badge():
    client, _ = _client()
    righe = client.get("/api/research").json()
    assert {(r["title"], r["instance_id"]) for r in righe} == {
        ("a", "alfa"), ("b", "beta"), ("vecchia", "alfa"),
    }


def test_read_filtered_by_instance():
    client, _ = _client()
    righe = client.get("/api/research", params={"instance": "beta"}).json()
    assert [r["title"] for r in righe] == ["b"]


def test_read_unknown_instance_is_422_with_valid_ids():
    client, _ = _client()
    r = client.get("/api/research", params={"instance": "gamma"})
    assert r.status_code == 422
    assert r.json()["detail"]["valid"] == ["alfa", "beta"]


def test_write_without_instance_is_422_even_with_a_default():
    client, lanciatore = _client()
    r = client.post("/api/research", json={"topic": "pompe di calore"})
    assert r.status_code == 422
    assert r.json()["detail"]["error"] == "instance_required"
    assert lanciatore.chiamate == []


def test_write_unknown_instance_is_422():
    client, lanciatore = _client()
    r = client.post("/api/research", json={"topic": "pompe di calore", "instance": "gamma"})
    assert r.status_code == 422
    assert r.json()["detail"] == {
        "error": "instance_unknown",
        "message": r.json()["detail"]["message"],
        "valid": ["alfa", "beta"],
    }
    assert lanciatore.chiamate == []


def test_write_on_unreachable_instance_is_named_503():
    client, lanciatore = _client()
    r = client.post("/api/research", json={"topic": "pompe di calore", "instance": "beta"})
    assert r.status_code == 503
    assert r.json()["detail"]["error"] == "instance_unreachable"
    assert lanciatore.chiamate == []


def test_write_launches_research_with_the_instance_own_channels():
    client, lanciatore = _client()
    r = client.post("/api/research", json={"topic": "pompe di calore", "instance": "alfa"})
    assert r.status_code == 202
    assert r.json()["instance"] == "alfa" and r.json()["pid"] == 4242
    [(argv, env)] = lanciatore.chiamate
    assert argv[3:8] == ["research", "pompe di calore", "--node", "topicResearcher", "--instance"]
    assert argv[8] == "alfa"
    assert env["LIFE_INSTANCE"] == "alfa"
    assert env["LIFE_CHANNEL_BUS_TENANT"] == "alfa"
    assert env["LIFE_CHANNEL_TELEGRAM_CHAT_ID"] == "-100123"
    assert "LIFE_INSTANCE_DIR" not in env
