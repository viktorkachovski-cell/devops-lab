from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_healthz():
    assert client.get("/healthz").json() == {"status": "ok"}


def test_roll_returns_1_to_6():
    for _ in range(20):
        assert 1 <= client.get("/roll").json()["result"] <= 6


def test_roll_can_fail(monkeypatch):
    monkeypatch.setattr(main, "FAIL_RATE", 1.0)
    assert client.get("/roll").status_code == 500


def test_metrics_exposed():
    client.get("/roll")
    assert "dicey_rolls_total" in client.get("/metrics").text