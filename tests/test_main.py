from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import TranscriptionResponse, RequestType, Operation, Channel

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_metrics_exposed():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "transcriptions_total" in r.text


def test_transcribe_rejects_non_image():
    r = client.post("/transcribe", files={"file": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_transcribe_success():
    fake_response = TranscriptionResponse(
        subject="Test", descriptionHtml="<p>Test</p>",
        requestType=RequestType.PASSEPORT, operation=Operation.RENOUVELLEMENT,
        channel=Channel.MAIL, confidence=0.95,
    )
    with patch("app.main.transcribe_letter", return_value=fake_response):
        r = client.post("/transcribe", files={"file": ("a.jpg", b"fakebytes", "image/jpeg")})
    assert r.status_code == 200
    assert r.json()["requestType"] == "passeport"