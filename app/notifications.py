import os


def create_build_message(
    build_number,
    status,
    passed_tests=0,
    failed_tests=0,
    build_url="",
):
    status = status.upper()

    if status == "SUCCESS":
        test_word = "test" if int(passed_tests) == 1 else "tests"
        text = (
            f"ReleaseGuard: Build #{build_number} passed. "
            f"{passed_tests} {test_word} succeeded."
        )
    else:
        test_word = "test" if int(failed_tests) == 1 else "tests"
        text = (
            f"ReleaseGuard ALERT: Build #{build_number} {status}. "
            f"{failed_tests} {test_word} failed."
        )

    return f"{text} Jenkins: {build_url}" if build_url else text


def send_sms(message, to_number=None):
    from twilio.rest import Client

    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    sender = os.getenv("TWILIO_PHONE_NUMBER")
    recipient = to_number or os.getenv("ALERT_PHONE_NUMBER")
    if not all((sid, token, sender, recipient)):
        raise RuntimeError("Twilio credentials and phone numbers must be configured")
    return Client(sid, token).messages.create(body=message, from_=sender, to=recipient)

