from app.notifications import create_build_message, send_sms
import pytest


def test_failed_build_message():
    message = create_build_message(12, "FAILED", failed_tests=2)
    assert "Build #12" in message and "FAILED" in message and "2 tests failed" in message


def test_success_build_message():
    assert create_build_message(42, "SUCCESS", passed_tests=18) == "ReleaseGuard: Build #42 passed. 18 tests succeeded."

def test_single_failed_test_message_uses_singular_word():
    message = create_build_message(23, "FAILED", failed_tests=1)
    assert "1 test failed" in message


def test_single_passed_test_message_uses_singular_word():
    message = create_build_message(24, "SUCCESS", passed_tests=1)
    assert "1 test succeeded" in message

def test_sms_requires_twilio_configuration(monkeypatch):
    # Remove each Twilio environment variable.
    monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWILIO_PHONE_NUMBER", raising=False)
    monkeypatch.delenv("ALERT_PHONE_NUMBER", raising=False)

    #Call Send_sms() and verify that it raises RunetimeError.
    #Confirm that the error message mention Twilio configuration.
    with pytest.raises(RuntimeError, match="Twilio credentials"):
        send_sms("This is a test message sent via Twilio")