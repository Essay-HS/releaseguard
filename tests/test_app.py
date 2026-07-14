def test_home_page_loads(client):
    assert client.get("/").status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"application": "ReleaseGuard", "status": "healthy", "version": "1.0.0"}


def test_invalid_route(client):
    assert client.get("/missing").status_code == 404


def test_build_creation_and_incident(client, auth):
    response = client.post("/api/builds", headers=auth, json={"build_number": 27, "status": "failed", "branch": "main", "commit_id": "abc123", "passed_tests": 16, "failed_tests": 2})
    assert response.status_code == 201
    assert response.json["status"] == "FAILED"
    page = client.get("/").get_data(as_text=True)
    assert "Build #27 finished with status FAILED" in page


def test_build_api_requires_token(client):
    assert client.post("/api/builds", json={"build_number": 1, "status": "SUCCESS"}).status_code == 401


def test_demo_success_build(client):
    response = client.post("/demo/build/success", follow_redirects=True)
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Build #1 succeeded" in page
    assert "SUCCESS" in page


def test_demo_failure_acknowledge_and_reset(client):
    failed = client.post("/demo/build/failed", follow_redirects=True)
    assert "opened a critical incident" in failed.get_data(as_text=True)
    acknowledged = client.post("/demo/incidents/1/acknowledge", follow_redirects=True)
    assert "Incident #1 acknowledged" in acknowledged.get_data(as_text=True)
    assert "Dashboard operator" in acknowledged.get_data(as_text=True)
    reset = client.post("/demo/reset", follow_redirects=True)
    assert "No builds yet" in reset.get_data(as_text=True)


def test_demo_health_check(client):
    response = client.post("/demo/health", follow_redirects=True)
    assert "Health check passed" in response.get_data(as_text=True)


def test_demo_controls_can_be_disabled(app):
    app.config["ENABLE_DEMO_CONTROLS"] = False
    assert app.test_client().post("/demo/build/success").status_code == 404
