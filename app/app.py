import json
import logging
import os
import time
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, g, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Histogram, generate_latest


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        APP_VERSION=os.getenv("APP_VERSION", "3.0.0"),
        FEATURE_BETA=os.getenv("FEATURE_BETA", "false").lower() == "true",
        LOG_DIR=os.getenv("LOG_DIR", "logs"),
    )
    if test_config:
        app.config.update(test_config)

    log_dir = Path(app.config["LOG_DIR"])
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"lab3.{id(app)}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = RotatingFileHandler(log_dir / "app.log", maxBytes=5_000_000, backupCount=2)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    app.extensions["request_logger"] = logger

    registry = CollectorRegistry()
    requests = Counter("lab3_http_requests_total", "HTTP requests", ["route", "status"], registry=registry)
    duration = Histogram("lab3_http_request_duration_seconds", "Request duration", ["route"], registry=registry)

    @app.before_request
    def start_timer():
        g.started = time.perf_counter()

    @app.after_request
    def record_request(response):
        route = request.url_rule.rule if request.url_rule else "unmatched"
        if route != "/metrics":
            elapsed = time.perf_counter() - g.started
            requests.labels(route, str(response.status_code)).inc()
            duration.labels(route).observe(elapsed)
            logger.info(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": request.method,
                "route": route,
                "status": response.status_code,
                "duration_seconds": elapsed,
            }))
        return response

    @app.get("/")
    def home():
        return jsonify(message="Rishav's DevOps Lab 3", name="Rishav",
                       roll_no="2301730245", version=app.config["APP_VERSION"])

    @app.get("/health")
    def health():
        return jsonify(status="UP", version=app.config["APP_VERSION"])

    @app.get("/metrics")
    def metrics():
        return app.response_class(generate_latest(registry), content_type=CONTENT_TYPE_LATEST)

    @app.get("/beta")
    def beta():
        enabled = app.config["FEATURE_BETA"]
        return jsonify(feature="beta", enabled=enabled), 200 if enabled else 404

    return app


app = create_app()
