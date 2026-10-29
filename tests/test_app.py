import json

import pytest

from app.app import create_app


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "LOG_DIR": str(tmp_path), "FEATURE_BETA": False})
    yield app
    logger = app.extensions["request_logger"]
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def test_home(app):
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert response.json["roll_no"] == "2301730245"


def test_health(app):
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "UP", "version": "3.0.0"}


def test_beta_disabled(app):
    response = app.test_client().get("/beta")
    assert response.status_code == 404
    assert response.json["enabled"] is False


def test_beta_enabled(app):
    app.config["FEATURE_BETA"] = True
    response = app.test_client().get("/beta")
    assert response.status_code == 200
    assert response.json["enabled"] is True


def test_metrics_count_requests_but_ignore_scrapes(app):
    client = app.test_client()
    client.get("/health")
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert b'lab3_http_requests_total{route="/health",status="200"} 1.0' in metrics.data
    assert b"lab3_http_request_duration_seconds_bucket" in metrics.data
    assert client.get("/metrics").data == metrics.data


def test_request_log_is_json(app):
    app.test_client().get("/health")
    path = app.config["LOG_DIR"] + "/app.log"
    with open(path) as stream:
        entry = json.loads(stream.readline())
    assert entry["route"] == "/health"
    assert entry["status"] == 200
    assert entry["duration_seconds"] >= 0


def test_unknown_paths_use_one_metric_label(app):
    client = app.test_client()
    client.get("/missing-one")
    client.get("/missing-two")
    metrics = client.get("/metrics").data
    assert b'lab3_http_requests_total{route="unmatched",status="404"} 2.0' in metrics
