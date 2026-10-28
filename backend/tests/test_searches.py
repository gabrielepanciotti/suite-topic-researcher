"""Finder-compatible search endpoints and their compatibility guarantees."""
from __future__ import annotations

import importlib

from fastapi.testclient import TestClient

from suite_learn_core.queue import InMemoryQueue
from suite_learn_core.types import Item

from topic_researcher_backend.api import get_lanciatore, get_queue
from topic_researcher_backend.app import app


class LanciatoreFinto:
    def __call__(self, argv, env, log):
        del argv, env, log
        return 4242


def _client() -> TestClient:
    queue = InMemoryQueue()
    for title in ("prima", "seconda", "terza"):
        queue.put("topicResearcher", Item(title=title, body="x", source_id=f"s:{title}"))
    app.dependency_overrides[get_queue] = lambda: queue
    app.dependency_overrides[get_lanciatore] = lambda: LanciatoreFinto()
    return TestClient(app)


def test_searches_paginate_with_an_opaque_cursor():
    client = _client()
    first = client.get("/api/searches", params={"limit": 2})
    assert first.status_code == 200
    body = first.json()
    assert [item["title"] for item in body["items"]] == ["prima", "seconda"]
    assert body["total"] == 3 and body["next_cursor"]

    last = client.get("/api/searches", params={"limit": 2, "cursor": body["next_cursor"]})
    assert [item["title"] for item in last.json()["items"]] == ["terza"]
    assert last.json()["next_cursor"] is None


def test_searches_reject_invalid_cursor_and_invalid_limit_with_common_error_shape():
    client = _client()
    invalid_cursor = client.get("/api/searches", params={"cursor": "non un cursor"})
    assert invalid_cursor.status_code == 422
    assert invalid_cursor.json()["error"]["code"] == "http_error"

    invalid_limit = client.get("/api/searches", params={"limit": 0})
    assert invalid_limit.status_code == 422
    error = invalid_limit.json()["error"]
    assert error["code"] == "validation_error" and error["field"] == "limit"
    assert isinstance(invalid_limit.json()["detail"], list)


def test_searches_post_is_a_202_alias_of_research():
    response = _client().post("/api/searches", json={"topic": "pompe di calore", "instance": "alfa"})
    assert response.status_code == 202
    assert response.json()["instance"] == "alfa" and response.json()["pid"] == 4242


def test_unknown_instance_gets_common_error_envelope():
    response = _client().get("/api/searches", params={"instance": "sconosciuta"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "instance_unknown"
    assert response.json()["detail"]["valid"] == ["alfa", "beta"]


def test_vista_is_available_with_explicit_local_development_opt_in(monkeypatch):
    monkeypatch.setenv("ALLOW_DEV_OWNER", "1")
    monkeypatch.setenv("LIFE_VISTA_DEFAULT_ROLE", "player")
    import topic_researcher_backend.app as app_module

    reloaded = importlib.reload(app_module)
    response = TestClient(reloaded.app).get("/api/vista")
    assert response.status_code == 200
    assert response.json()["ruolo"] == "player"
    assert [section["id"] for section in response.json()["sezioni"]] == [
        "cerca", "risultati", "salvati",
    ]
