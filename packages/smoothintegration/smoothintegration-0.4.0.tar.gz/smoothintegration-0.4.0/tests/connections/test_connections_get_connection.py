import uuid

import pytest
import responses

from smoothintegration.exceptions import SIError


class TestConnectionsGetConnection:

    def test_can_get_connection(self, mocked_responses, test_client):
        connection_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/connections/{connection_id}",
            json={
                "message": "Connection Retrieved",
                "result": {
                    "id": connection_id,
                    "company_id": "22222222-2222-2222-2222-222222222222",
                    "integration": "xero",
                    "external_name": "Test Connection",
                    "external_id": "ext123",
                    "scopes": ["accounting.transactions", "accounting.contacts.read"],
                    "data": {},
                    "created_at": "2024-03-21T10:00:00Z",
                    "is_sandbox": False,
                    "status": "connected",
                },
            },
            status=200,
        )

        result = test_client.connections.get_connection(uuid.UUID(connection_id))
        assert result == {
            "id": connection_id,
            "company_id": "22222222-2222-2222-2222-222222222222",
            "integration": "xero",
            "external_name": "Test Connection",
            "external_id": "ext123",
            "scopes": ["accounting.transactions", "accounting.contacts.read"],
            "data": {},
            "created_at": "2024-03-21T10:00:00Z",
            "is_sandbox": False,
            "status": "connected",
        }

    def test_raises_error_on_bad_request(self, mocked_responses, test_client):
        connection_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/connections/{connection_id}",
            json={"message": "Invalid Connection ID"},
            status=400,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.connections.get_connection(uuid.UUID(connection_id))
        assert str(excinfo.value) == "Bad Request: Invalid Connection ID"

    def test_raises_error_on_unauthorized(self, mocked_responses, test_client):
        connection_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/connections/{connection_id}",
            json={"message": "Invalid 'X-Organisation' header"},
            status=401,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.connections.get_connection(uuid.UUID(connection_id))
        assert str(excinfo.value) == "Unauthorized: Invalid 'X-Organisation' header"

    def test_raises_error_on_not_found(self, mocked_responses, test_client):
        connection_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/connections/{connection_id}",
            json={"message": "Connection Not Found"},
            status=404,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.connections.get_connection(uuid.UUID(connection_id))
        assert str(excinfo.value) == "Not Found: Connection Not Found"

    def test_raises_error_on_internal_server_error(self, mocked_responses, test_client):
        connection_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/connections/{connection_id}",
            json={"message": "Internal Server Error"},
            status=500,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.connections.get_connection(uuid.UUID(connection_id))
        assert str(excinfo.value) == "Internal Server Error"
