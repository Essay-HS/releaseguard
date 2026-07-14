import hmac
import secrets

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for

from .db import get_db

bp = Blueprint("main", __name__)
VALID_STATUSES = {"SUCCESS", "FAILED", "UNSTABLE", "ABORTED"}


def _rows(query, params=()):
    return [dict(row) for row in get_db().execute(query, params).fetchall()]


def _save_build(values):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO builds (build_number,status,branch,commit_id,passed_tests,failed_tests,build_url) VALUES (?,?,?,?,?,?,?)",
        values,
    )
    if values[1] != "SUCCESS":
        db.execute(
            "INSERT INTO incidents (build_id,summary,severity) VALUES (?,?,?)",
            (cursor.lastrowid, f"Build #{values[0]} finished with status {values[1]}", "critical" if values[1] == "FAILED" else "high"),
        )
    db.commit()
    return dict(db.execute("SELECT * FROM builds WHERE id = ?", (cursor.lastrowid,)).fetchone())


def _require_demo_controls():
    if not current_app.config["ENABLE_DEMO_CONTROLS"]:
        abort(404)


@bp.get("/")
def index():
    builds = _rows("SELECT * FROM builds ORDER BY id DESC LIMIT 10")
    incidents = _rows("SELECT * FROM incidents ORDER BY id DESC LIMIT 10")
    return render_template("index.html", builds=builds, incidents=incidents, demo_enabled=current_app.config["ENABLE_DEMO_CONTROLS"])


@bp.get("/health")
def health():
    try:
        get_db().execute("SELECT 1").fetchone()
    except Exception:
        return jsonify(status="unhealthy", application="ReleaseGuard", version=current_app.config["APP_VERSION"]), 503
    return jsonify(status="healthy", application="ReleaseGuard", version=current_app.config["APP_VERSION"])


@bp.get("/api/builds")
def list_builds():
    return jsonify(_rows("SELECT * FROM builds ORDER BY id DESC LIMIT 100"))


@bp.post("/api/builds")
def create_build():
    configured = current_app.config.get("BUILD_API_TOKEN", "")
    provided = request.headers.get("Authorization", "").removeprefix("Bearer ")
    if configured and not hmac.compare_digest(configured, provided):
        return jsonify(error="unauthorized"), 401

    data = request.get_json(silent=True) or {}
    required = ("build_number", "status")
    if any(key not in data for key in required):
        return jsonify(error="build_number and status are required"), 400
    status = str(data["status"]).upper()
    if status not in VALID_STATUSES:
        return jsonify(error="invalid status"), 400
    try:
        values = (
            int(data["build_number"]), status, str(data.get("branch", "unknown"))[:100],
            str(data.get("commit_id", "unknown"))[:100], int(data.get("passed_tests", 0)),
            int(data.get("failed_tests", 0)), str(data.get("build_url", ""))[:500],
        )
    except (TypeError, ValueError):
        return jsonify(error="numeric fields must contain integers"), 400

    return jsonify(_save_build(values)), 201


@bp.post("/demo/build/<status>")
def demo_build(status):
    _require_demo_controls()
    status = status.upper()
    if status not in {"SUCCESS", "FAILED"}:
        abort(404)
    db = get_db()
    next_number = db.execute("SELECT COALESCE(MAX(build_number), 0) + 1 FROM builds").fetchone()[0]
    failed = 2 if status == "FAILED" else 0
    passed = 16 if failed else 18
    _save_build((next_number, status, "main", secrets.token_hex(4), passed, failed, "demo://local-build"))
    if status == "SUCCESS":
        flash(f"Build #{next_number} succeeded. ReleaseGuard saved it without creating an incident.", "success")
    else:
        flash(f"Build #{next_number} failed. ReleaseGuard saved it and opened a critical incident.", "error")
    return redirect(url_for("main.index"))


@bp.post("/demo/health")
def demo_health():
    _require_demo_controls()
    get_db().execute("SELECT 1").fetchone()
    flash("Health check passed: Flask is running and the database responded.", "success")
    return redirect(url_for("main.index"))


@bp.post("/demo/incidents/<int:incident_id>/acknowledge")
def demo_acknowledge(incident_id):
    _require_demo_controls()
    db = get_db()
    cursor = db.execute(
        "UPDATE incidents SET status='acknowledged', acknowledged_by='Dashboard operator', acknowledged_at=CURRENT_TIMESTAMP WHERE id=? AND status='open'",
        (incident_id,),
    )
    db.commit()
    flash(f"Incident #{incident_id} acknowledged." if cursor.rowcount else f"Incident #{incident_id} was already handled or not found.", "success" if cursor.rowcount else "info")
    return redirect(url_for("main.index"))


@bp.post("/demo/reset")
def demo_reset():
    _require_demo_controls()
    db = get_db()
    db.execute("DELETE FROM incidents")
    db.execute("DELETE FROM builds")
    db.commit()
    flash("Demo data cleared. ReleaseGuard is ready for a fresh walkthrough.", "info")
    return redirect(url_for("main.index"))
