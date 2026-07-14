from app.notifications import create_build_message


def test_failed_build_message():
    message = create_build_message(12, "FAILED", failed_tests=2)
    assert "Build #12" in message and "FAILED" in message and "2 tests failed" in message


def test_success_build_message():
    assert create_build_message(42, "SUCCESS", passed_tests=18) == "ReleaseGuard: Build #42 passed. 18 tests succeeded."

