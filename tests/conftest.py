import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db"), "BUILD_API_TOKEN": "test-token"})


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth():
    return {"Authorization": "Bearer test-token"}

