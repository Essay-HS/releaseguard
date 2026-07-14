#!/usr/bin/env python3
import os
import sys

import requests


url = os.getenv("HEALTHCHECK_URL", "http://127.0.0.1:5000/health")
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    healthy = response.json().get("status") == "healthy"
except (requests.RequestException, ValueError) as exc:
    print(f"Health check failed: {exc}", file=sys.stderr)
    raise SystemExit(1)
if not healthy:
    print(f"Unhealthy response from {url}", file=sys.stderr)
    raise SystemExit(1)
print(f"Healthy: {url}")

