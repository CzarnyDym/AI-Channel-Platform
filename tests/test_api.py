from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies import get_scan_runner
from app.scan_engine.pipeline import build_default_registry


CHANNEL_PAYLOAD = {
    "name": "Example Creator",
    "external_id": "UC-example-channel",
}


def create_channel(client: TestClient) -> dict:
    response = client.post("/channels", json=CHANNEL_PAYLOAD)
    assert response.status_code == 201
    return response.json()


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_channel(client: TestClient) -> None:
    created_channel = create_channel(client)

    assert created_channel["name"] == CHANNEL_PAYLOAD["name"]
    assert created_channel["external_id"] == CHANNEL_PAYLOAD["external_id"]
    assert created_channel["platform"] == "youtube"
    assert created_channel["id"]
    assert created_channel["created_at"]

    response = client.get(f"/channels/{created_channel['id']}")

    assert response.status_code == 200
    assert response.json() == created_channel


def test_duplicate_channel_returns_conflict(client: TestClient) -> None:
    create_channel(client)

    response = client.post("/channels", json=CHANNEL_PAYLOAD)

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "A channel with this platform and external ID already exists"
    )


def test_channel_fields_cannot_be_blank(client: TestClient) -> None:
    response = client.post(
        "/channels",
        json={"name": " ", "external_id": " "},
    )

    assert response.status_code == 422


def test_missing_channel_returns_not_found(client: TestClient) -> None:
    response = client.get(f"/channels/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Channel not found"}


def test_create_and_get_scan(client: TestClient) -> None:
    channel = create_channel(client)

    response = client.post(f"/channels/{channel['id']}/scans")

    assert response.status_code == 201
    created_scan = response.json()
    assert created_scan["channel_id"] == channel["id"]
    assert created_scan["status"] == "pending"
    assert created_scan["mode"] == "latest"
    assert created_scan["scope"] == {}
    assert created_scan["progress_percentage"] == 0
    assert len(created_scan["steps"]) == 7
    assert created_scan["id"]
    assert created_scan["created_at"]
    assert created_scan["updated_at"]

    response = client.get(f"/scans/{created_scan['id']}")

    assert response.status_code == 200
    completed_scan = response.json()
    assert completed_scan["status"] == "completed"
    assert completed_scan["progress_percentage"] == 100
    assert completed_scan["current_step"] is None
    assert completed_scan["pipeline_version"] == "scan-manifest-v1"

    skipped_steps = [
        step
        for step in completed_scan["steps"]
        if step["status"] == "skipped"
    ]
    assert len(skipped_steps) == 5
    assert {
        step["skip_reason"] for step in skipped_steps
    } == {"not_implemented"}

    response = client.get(f"/scans/{created_scan['id']}/report")

    assert response.status_code == 200
    report = response.json()
    assert report["report_type"] == "technical_scan_manifest"
    assert report["content"]["scan"]["id"] == created_scan["id"]


def test_create_scan_accepts_mode_and_scope(client: TestClient) -> None:
    channel = create_channel(client)

    response = client.post(
        f"/channels/{channel['id']}/scans",
        json={
            "mode": "recent_period",
            "scope": {"days": 30},
        },
    )

    assert response.status_code == 201
    assert response.json()["mode"] == "recent_period"
    assert response.json()["scope"] == {"days": 30}


def test_create_scan_for_missing_channel_returns_not_found(
    client: TestClient,
) -> None:
    response = client.post(f"/channels/{uuid4()}/scans")

    assert response.status_code == 404
    assert response.json() == {"detail": "Channel not found"}


def test_missing_scan_returns_not_found(client: TestClient) -> None:
    response = client.get(f"/scans/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Scan not found"}


def test_missing_scan_report_returns_not_found(
    client: TestClient,
) -> None:
    response = client.get(f"/scans/{uuid4()}/report")

    assert response.status_code == 404
    assert response.json() == {"detail": "Scan not found"}


class NonRunningScanRunner:
    def __init__(self) -> None:
        self.registry = build_default_registry()

    def run(self, scan_id: object) -> None:
        return None


def test_pending_scan_report_returns_conflict(
    client: TestClient,
) -> None:
    client.app.dependency_overrides[get_scan_runner] = (
        lambda: NonRunningScanRunner()
    )
    channel = create_channel(client)
    scan_response = client.post(f"/channels/{channel['id']}/scans")
    scan_id = scan_response.json()["id"]

    response = client.get(f"/scans/{scan_id}/report")

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Scan report is not available"
    }
