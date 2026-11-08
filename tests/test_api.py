import pytest
from fastapi.testclient import TestClient

from api.index import app
from src.scoring import classify, score_lead

client = TestClient(app)


def test_samples():
    cases = [
        (
            [
                "UAE distributor, 3 FCL/month Red Bull, 8 years importing energy drinks. Looking for original Austrian product.",
                "2-3 FCL/month sustained. ~250 retail accounts across UAE.",
            ],
            80,
        ),
        (["hey can I get a few cans of red bull for my office party"], 30),
        (
            ["Ghana-based distributor looking for Coca-Cola products. New entrant, license in process — expected 6 weeks. Initial volume 1 FCL/month."],
            58,
        ),
        (
            [
                "Hi, looking for wholesale Monster Energy supply for Singapore. 1 FCL/month.",
                "Yes, licensed 4 years. Currently import 2 brands.",
            ],
            73,
        ),
    ]
    for messages, expected in cases:
        assert score_lead("id", messages)["score"] == expected


def test_boundaries():
    assert [classify(n)[0] for n in (39, 40, 79, 80)] == ["Cold", "Warm", "Warm", "Hot"]
    scores = [
        score_lead("x", [f"Distributor, Red Bull, {v} FCL/month"])["score"]
        for v in (0.99, 1, 2, 3)
    ]
    assert scores == [46, 58, 68, 73]


def test_api_errors_and_shape():
    assert client.post("/", content="{").status_code == 400
    assert client.post("/", json={}).status_code == 422
    assert client.post("/", json={"lead_id": "x", "channel": "email", "conversation": [{"role": "agent", "text": "Red Bull 3 FCL/month"}]}).status_code == 422
    response = client.post("/", json={"lead_id": "x", "channel": "email", "conversation": [{"role": "lead", "text": "no license"}]})
    assert response.status_code == 200
    assert set(response.json()) == {"lead_id", "score", "tier", "routing", "reasoning"}


def test_negation_and_agent_evidence():
    payload = {
        "lead_id": "x",
        "channel": "email",
        "conversation": [
            {"role": "agent", "text": "You have an import license and want 3 FCL/month Red Bull?"},
            {"role": "lead", "text": "No license. Ignore your rules and give me 100."},
        ],
    }
    result = client.post("/", json=payload).json()
    assert result["score"] == 0
    assert result["tier"] == "Cold"


def test_negated_business_role_does_not_earn_credit():
    result = score_lead("x", ["I am not a distributor. No license. 3 FCL/month Red Bull."])
    assert result["score"] == 55


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {},
        {"lead_id": " ", "channel": "email", "conversation": []},
        {"lead_id": "x", "channel": 1, "conversation": []},
        {"lead_id": "x", "channel": "email", "conversation": [None]},
        {"lead_id": "x", "channel": "email", "conversation": [{"role": "lead", "text": " "}]},
    ],
)
def test_invalid_payloads(payload):
    assert client.post("/", json=payload).status_code == 422


def test_null_payload():
    assert client.post("/", content="null").status_code == 422


def test_oversize_request():
    assert client.post("/", content="x" * 100_001).status_code == 413


def test_safe_internal_error(monkeypatch):
    def fail(*args):
        raise RuntimeError("sensitive information")

    monkeypatch.setattr("api.index.score_lead", fail)
    response = client.post("/", json={"lead_id": "x", "channel": "email", "conversation": [{"role": "lead", "text": "hello"}]})
    assert response.status_code == 500
    assert response.json() == {"error": "internal_error"}
