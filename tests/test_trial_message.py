from scripts.send_twilio_alert import select_message_for_twilio


def test_trial_mode_uses_internal_alert_template():
    result = select_message_for_twilio(
        normal_message="Normal ReleaseGuard message",
        trial_mode=True,
    )

    assert result == "sms_internal_alerts"


def test_normal_mode_uses_original_message():
    normal_message = "Normal ReleaseGuard message"

    result = select_message_for_twilio(
        normal_message=normal_message,
        trial_mode=False,
    )

    assert result == normal_message