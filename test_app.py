import sqlite3
import pytest

import app as application


@pytest.fixture
def client(tmp_path, monkeypatch):
    database = tmp_path / "test_firmware.db"
    monkeypatch.setattr(application, "DATABASE", str(database))
    application.init_db()

    application.app.config.update(TESTING=True)

    with application.app.test_client() as test_client:
        yield test_client


def submit_request(client):
    return client.post(
        "/",
        data={
            "project_name": "Gateway Firmware",
            "firmware_version": "1.0.0",
            "git_branch": "release/1.0",
            "commit_id": "abc123def456",
            "platform": "Embedded Linux",
            "signing_profile": "QA",
        },
        follow_redirects=True,
    )


def read_requests():
    with application.get_db() as db:
        return [
            dict(row) for row in db.execute(
                "SELECT * FROM firmware_requests"
            ).fetchall()
        ]


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Firmware Signing Approval" in response.data


def test_request_submission(client):
    response = submit_request(client)
    assert response.status_code == 200

    requests = read_requests()
    assert len(requests) == 1
    assert requests[0]["status"] == "PENDING_APPROVAL"


def test_approver_can_approve_request(client):
    submit_request(client)
    request_id = read_requests()[0]["id"]

    response = client.post(
        f"/approver/{request_id}/approve",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert read_requests()[0]["status"] == "APPROVED"


def test_approver_can_reject_request(client):
    submit_request(client)
    request_id = read_requests()[0]["id"]

    client.post(f"/approver/{request_id}/reject")

    assert read_requests()[0]["status"] == "REJECTED"


def test_missing_fields_are_rejected(client):
    response = client.post(
        "/",
        data={"project_name": "Gateway Firmware"},
        follow_redirects=True,
    )

    assert b"Please complete all fields." in response.data
    assert read_requests() == []


def test_processed_request_cannot_be_approved_again(client):
    submit_request(client)
    request_id = read_requests()[0]["id"]

    client.post(f"/approver/{request_id}/reject")
    client.post(f"/approver/{request_id}/approve")

    assert read_requests()[0]["status"] == "REJECTED"
