#!/usr/bin/env python3
#!/usr/bin/env python3

import os
import sys

import requests


def main():
    status = sys.argv[1].upper()

    base_url = os.getenv(
        "RELEASEGUARD_URL",
        "http://127.0.0.1:5001",
    ).rstrip("/")

    payload = {
        "build_number": os.getenv("BUILD_NUMBER", 0),
        "status": status,
        "branch": os.getenv("BRANCH_NAME", "unknown"),
        "commit_id": os.getenv("GIT_COMMIT", "unknown"),
        "build_url": os.getenv("BUILD_URL", ""),
        "passed_tests": os.getenv("PASSED_TESTS", 0),
        "failed_tests": os.getenv("FAILED_TESTS", 0),
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('BUILD_API_TOKEN', '')}"
    }

    try:
        response = requests.post(
            f"{base_url}/api/builds",
            json=payload,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

    except requests.exceptions.ConnectionError:
        print(
            f"ReleaseGuard is unavailable at {base_url}. "
            "Build results were not recorded.",
            file=sys.stderr,
        )
        return 1

    except requests.exceptions.Timeout:
        print(
            "ReleaseGuard did not respond within 10 seconds. "
            "Build results were not recorded.",
            file=sys.stderr,
        )
        return 1

    except requests.exceptions.HTTPError as error:
        print(
            f"ReleaseGuard rejected the build report: {error}",
            file=sys.stderr,
        )
        return 1

    except requests.exceptions.RequestException as error:
        print(
            f"ReleaseGuard reporting failed: {error}",
            file=sys.stderr,
        )
        return 1

    print(f"Recorded build {response.json()['build_number']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())