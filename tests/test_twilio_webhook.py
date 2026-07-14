def _sms(client, body):
    return client.post("/twilio/incoming", data={"Body": body, "From": "+15551234567"})


def test_status_without_builds(client):
    response = _sms(client, "STATUS")
    assert response.status_code == 200
    assert "no recorded builds" in response.get_data(as_text=True)


def test_acknowledge_incident(client, auth):
    client.post("/api/builds", headers=auth, json={"build_number": 43, "status": "FAILED"})
    response = _sms(client, "ACK 1")
    assert "Incident 1 acknowledged" in response.get_data(as_text=True)
    assert "0 open incidents" in _sms(client, "INCIDENTS").get_data(as_text=True)

