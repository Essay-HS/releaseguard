# ReleaseGuard

ReleaseGuard is a Flask-based CI/CD monitoring dashboard that records Jenkins build results, creates incidents for failed builds, validates application health, and sends or receives Twilio SMS messages.

## Quick start

```bash
cd /Users/ac/Projects/releaseguard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app run run --debug
```

Open `http://127.0.0.1:5001`. Verify the service at `GET /health`.

If Flask reports `Could not import 'run'` or `cp` reports that `.env.example` is
missing, check `pwd`. Both files must be visible in the current directory before
running the setup commands:

```bash
pwd
ls run.py .env.example requirements.txt
```

## Record a build

```bash
curl -X POST http://127.0.0.1:5000/api/builds \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer change-me' \
  -d '{"build_number":42,"status":"SUCCESS","branch":"main","commit_id":"abc123","passed_tests":18}'
```

Failed, unstable, and aborted builds automatically create incidents. Allowed statuses are `SUCCESS`, `FAILED`, `UNSTABLE`, and `ABORTED`.

## Twilio setup

Copy `.env.example` to `.env` and replace all placeholder values. Configure the Twilio number's incoming-message webhook as `POST https://YOUR_HOST/twilio/incoming`, and set `TWILIO_WEBHOOK_URL` to that exact public URL so signatures can be validated. Supported inbound commands are `STATUS`, `LAST BUILD`, `INCIDENTS`, and `ACK <id>`.

To preview an outbound message without sending it:

```bash
TWILIO_DRY_RUN=true BUILD_NUMBER=42 PASSED_TESTS=18 python scripts/send_twilio_alert.py SUCCESS
```

## Jenkins setup

Create secret-text credentials with IDs `releaseguard-api-token`, `twilio-account-sid`, `twilio-auth-token`, `twilio-from-number`, and `alert-phone-number`. Configure `RELEASEGUARD_URL`; optionally configure `DEPLOY_COMMAND` and `HEALTHCHECK_URL`. Jenkins installs dependencies, runs tests with JUnit output, optionally deploys, checks production health, records the outcome, and sends the matching alert.

## Tests

```bash
pytest --cov=app
```

Tests use a temporary SQLite database and bypass Twilio signature validation in Flask testing mode. They never send real messages.
