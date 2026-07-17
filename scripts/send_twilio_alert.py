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
    trial_mode = os.getenv("TWILIO_TRIAL_MODE", "false").lower() == "true"

    message_to_send = select_message_for_twilio(
        normal_message=message,
        trial_mode=trial_mode,
    )

def select_message_for_twilio(normal_message, trial_mode):
    if trial_mode:
        return "sms_internal_alerts"

    return normal_message
if __name__ == "__main__":
    main()
