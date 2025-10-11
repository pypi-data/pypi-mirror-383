import uuid

import pytest
import responses

from smoothintegration.exceptions import SIError


class TestCompaniesGetCompany:

    def test_can_get_company(self, mocked_responses, test_client):
        company_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/companies/{company_id}",
            json={
                "message": "Company Retrieved",
                "result": {
                    "name": "Test Company",
                    "id": company_id,
                },
            },
            status=200,
        )

        assert test_client.companies.get_company(uuid.UUID(company_id)) == {
            "id": company_id,
            "name": "Test Company",
        }

    def test_raises_error_on_bad_request(self, mocked_responses, test_client):
        company_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/companies/{company_id}",
            json={"message": "Invalid Company ID"},
            status=400,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.companies.get_company(uuid.UUID(company_id))
        assert str(excinfo.value) == "Bad Request: Invalid Company ID"

    def test_raises_error_on_unauthorized(self, mocked_responses, test_client):
        company_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/companies/{company_id}",
            json={"message": "Invalid 'X-Organisation' header"},
            status=401,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.companies.get_company(uuid.UUID(company_id))
        assert str(excinfo.value) == "Unauthorized: Invalid 'X-Organisation' header"

    def test_raises_error_on_internal_server_error(self, mocked_responses, test_client):
        company_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/companies/{company_id}",
            json={"message": "Internal Server Error"},
            status=500,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.companies.get_company(uuid.UUID(company_id))
        assert str(excinfo.value) == "Internal Server Error"

    def test_raises_error_on_not_found(self, mocked_responses, test_client):
        company_id = "11111111-1111-1111-1111-111111111111"
        mocked_responses.add(
            responses.GET,
            f"https://api.smooth-integration.com/v1/companies/{company_id}",
            json={"message": "Company Not Found"},
            status=404,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.companies.get_company(uuid.UUID(company_id))
        assert str(excinfo.value) == "Not Found: Company Not Found"
