#!/usr/bin/env python3
import os
import sys

import requests


status = sys.argv[1].upper()
base_url = os.getenv("RELEASEGUARD_URL", "http://127.0.0.1:5001").rstrip("/")
payload = {"build_number": os.getenv("BUILD_NUMBER", 0), "status": status, "branch": os.getenv("BRANCH_NAME", "unknown"), "commit_id": os.getenv("GIT_COMMIT", "unknown"), "build_url": os.getenv("BUILD_URL", ""), "passed_tests": os.getenv("PASSED_TESTS", 0), "failed_tests": os.getenv("FAILED_TESTS", 0)}
headers = {"Authorization": f"Bearer {os.getenv('BUILD_API_TOKEN', '')}"}
response = requests.post(f"{base_url}/api/builds", json=payload, headers=headers, timeout=10)
response.raise_for_status()
print(f"Recorded build {response.json()['build_number']}")

