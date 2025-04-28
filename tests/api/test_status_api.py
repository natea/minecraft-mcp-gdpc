from fastapi.testclient import TestClient

# The api_client fixture is automatically available due to conftest.py
# No need to explicitly import it here unless you need type hinting
# from .conftest import api_client # Example for type hinting if needed

def test_health_check(api_client: TestClient):
    """
    Tests the /health endpoint.
    """
    response = api_client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("Tested /health endpoint.")

def test_gdpc_status(api_client: TestClient):
    """
    Tests the /gdpc-status endpoint.
    Asserts the endpoint returns a 200 status and the expected JSON structure.
    The actual connection status depends on the environment where tests are run.
    """
    response = api_client.get("/v1/gdpc-status")
    assert response.status_code == 200
    data = response.json()
    assert "minecraft_version" in data
    assert "status" in data
    # You might want more specific assertions about the values here,
    # but checking for the presence of keys is a good start.
    print(f"Tested /v1/gdpc-status endpoint. Data: {data}")