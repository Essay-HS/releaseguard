#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.notifications import create_build_message, send_sms


def main():
    parser = argparse.ArgumentParser(description="Send a ReleaseGuard build alert")
    parser.add_argument("status", choices=["SUCCESS", "FAILED", "UNSTABLE", "ABORTED"])
    args = parser.parse_args()
    message = create_build_message(os.getenv("BUILD_NUMBER", "unknown"), args.status, os.getenv("PASSED_TESTS", 0), os.getenv("FAILED_TESTS", 0), os.getenv("BUILD_URL", ""))
    message_to_send = message
    if os.getenv("TWILIO_TRIAL_MODE", "false").lower() == "true":
     message_to_send = "sms_internal_alerts"
    if os.getenv("TWILIO_DRY_RUN", "false").lower() == "true":
        print(message_to_send)
    else:
        sent = send_sms(message_to_send)
        print(f"Sent Twilio message {sent.sid}")


if __name__ == "__main__":
    main()
