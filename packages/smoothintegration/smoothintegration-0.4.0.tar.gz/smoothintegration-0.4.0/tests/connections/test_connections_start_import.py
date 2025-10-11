import uuid

import pytest
import responses

from smoothintegration.exceptions import SIError


class TestConnectionsStartImport:

    def test_can_start_import(self, mocked_responses, test_client):
        connection_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.POST,
            f"https://api.smooth-integration.com/v1/connections/{connection_id}/import",
            json={
                "message": "Import Started",
                "result": {
                    "importId": "33333333-3333-3333-3333-333333333333",
                    "companyId": "22222222-2222-2222-2222-222222222222",
                    "connectionId": connection_id,
                    "tasks": [
                        "44444444-4444-4444-4444-444444444444",
                        "55555555-5555-55555-5555-555555555555",
                        "66666666-6666-6666-6666-666666666666",
                    ],
                },
            },
            status=200,
        )

        result = test_client.connections.start_import(uuid.UUID(connection_id))
        assert result == {
            "importId": "33333333-3333-3333-3333-333333333333",
            "companyId": "22222222-2222-2222-2222-222222222222",
            "connectionId": connection_id,
            "tasks": [
                "44444444-4444-4444-4444-444444444444",
                "55555555-5555-55555-5555-555555555555",
                "66666666-6666-6666-6666-666666666666",
            ],
        }

    def test_raises_error_on_bad_request(self, mocked_responses, test_client):
        connection_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.POST,
            f"https://api.smooth-integration.com/v1/connections/{connection_id}/import",
            json={"message": "Invalid Connection ID"},
            status=400,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.connections.start_import(uuid.UUID(connection_id))
        assert str(excinfo.value) == "Bad Request: Invalid Connection ID"

    def test_raises_error_on_unauthorized(self, mocked_responses, test_client):
        connection_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.POST,
            f"https://api.smooth-integration.com/v1/connections/{connection_id}/import",
            json={"message": "Invalid 'X-Organisation' header"},
            status=401,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.connections.start_import(uuid.UUID(connection_id))
        assert str(excinfo.value) == "Unauthorized: Invalid 'X-Organisation' header"

    def test_raises_error_on_not_found(self, mocked_responses, test_client):
        connection_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.POST,
            f"https://api.smooth-integration.com/v1/connections/{connection_id}/import",
            json={"message": "Connection Not Found"},
            status=404,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.connections.start_import(uuid.UUID(connection_id))
        assert str(excinfo.value) == "Not Found: Connection Not Found"

    def test_raises_error_on_internal_server_error(self, mocked_responses, test_client):
        connection_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.POST,
            f"https://api.smooth-integration.com/v1/connections/{connection_id}/import",
            json={"message": "Internal Server Error"},
            status=500,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.connections.start_import(uuid.UUID(connection_id))
        assert str(excinfo.value) == "Internal Server Error"
