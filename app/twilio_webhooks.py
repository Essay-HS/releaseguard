from datetime import datetime, timezone

from flask import Blueprint, Response, current_app, request
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from .db import get_db

bp = Blueprint("twilio", __name__)


def _valid_signature():
    if current_app.testing:
        return True
    token = current_app.config.get("TWILIO_AUTH_TOKEN")
    url = current_app.config.get("TWILIO_WEBHOOK_URL")
    signature = request.headers.get("X-Twilio-Signature", "")
    return bool(token and url and signature and RequestValidator(token).validate(url, request.form, signature))


@bp.post("/twilio/incoming")
def incoming():
    if not _valid_signature():
        return Response("Invalid signature", status=403)
    command = request.form.get("Body", "").strip().upper()
    sender = request.form.get("From", "unknown")
    db = get_db()
    response = MessagingResponse()

    if command == "STATUS":
        build = db.execute("SELECT * FROM builds ORDER BY id DESC LIMIT 1").fetchone()
        response.message("ReleaseGuard has no recorded builds." if not build else f"ReleaseGuard status: last build #{build['build_number']} was {build['status']} at {build['created_at']}.")
    elif command == "LAST BUILD":
        build = db.execute("SELECT * FROM builds ORDER BY id DESC LIMIT 1").fetchone()
        response.message("No builds recorded." if not build else f"Build #{build['build_number']}: {build['status']}; {build['passed_tests']} passed, {build['failed_tests']} failed.")
    elif command == "INCIDENTS":
        count = db.execute("SELECT COUNT(*) FROM incidents WHERE status = 'open'").fetchone()[0]
        response.message(f"ReleaseGuard has {count} open incident{'s' if count != 1 else ''}.")
    elif command.startswith("ACK "):
        try:
            incident_id = int(command.split(maxsplit=1)[1])
        except ValueError:
            response.message("Use ACK followed by an incident number, for example ACK 42.")
        else:
            cursor = db.execute(
                "UPDATE incidents SET status='acknowledged', acknowledged_by=?, acknowledged_at=? WHERE id=? AND status='open'",
                (sender, datetime.now(timezone.utc).isoformat(), incident_id),
            )
            db.commit()
            response.message(f"Incident {incident_id} acknowledged by {sender}." if cursor.rowcount else f"Open incident {incident_id} was not found.")
    else:
        response.message("Commands: STATUS, LAST BUILD, INCIDENTS, or ACK <incident number>.")
    return Response(str(response), mimetype="application/xml")

