import datetime
import uuid

import pytest
import responses

from smoothintegration.exceptions import SIError


class TestCompaniesGetCompany:

    def test_can_list_companies(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/companies",
            json={
                "message": "Successfully retrieved companies",
                "result": [
                    {
                        "id": "a13e9950-c550-4380-9c11-a3197584b553",
                        "name": "Second Company",
                        "created_at": "2025-04-20T07:52:57.444Z",
                        "integrations": []
                    },
                    {
                        "id": "af91caca-9b43-4c40-8a56-b279a9931c10",
                        "name": "First Company",
                        "created_at": "2025-04-20T03:00:27.008Z",
                        "integrations": ["exact"]
                    }
                ]
            },
            status=200,
        )

        assert test_client.companies.list_companies() == [
            {
                "id": "a13e9950-c550-4380-9c11-a3197584b553",
                "name": "Second Company",
                "created_at": datetime.datetime(2025, 4, 20, 7, 52, 57, 444000, tzinfo=datetime.timezone.utc),
                "integrations": []
            },
            {
                "id": "af91caca-9b43-4c40-8a56-b279a9931c10",
                "name": "First Company",
                "created_at": datetime.datetime(2025, 4, 20, 3, 0, 27, 8000, tzinfo=datetime.timezone.utc),
                "integrations": ["exact"]
            }
        ]

    def test_can_list_no_companies(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/companies",
            json={
                "message": "Successfully retrieved companies",
                "result": []
            },
            status=200,
        )

        assert test_client.companies.list_companies() == []

    def test_raises_error_on_unauthorized(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/companies",
            json={"message": "Invalid 'X-Organisation' header"},
            status=401,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.companies.list_companies()
        assert str(excinfo.value) == "Unauthorized: Invalid 'X-Organisation' header"

    def test_raises_error_on_internal_server_error(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/companies",
            json={"message": "Internal Server Error"},
            status=500,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.companies.list_companies()
        assert str(excinfo.value) == "Internal Server Error"
