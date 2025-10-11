import uuid

import pytest
import responses

from smoothintegration.exceptions import SIError


class TestQuickbooksGetConsentUrl:

    def test_can_get_consent_url(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/quickbooks/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878",
            json={
                "message": "Created Consent Url",
                "result": {
                    "consentUrl": "the-consent-url",
                },
            },
            status=200,
        )

        assert (
            test_client.quickbooks.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
            )
            == "the-consent-url"
        )

    def test_raises_error_on_bad_request(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/quickbooks/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878",
            json={"message": "QuickBooks is not configured for this organisation"},
            status=400,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.quickbooks.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
            )
        assert (
            str(excinfo.value)
            == "Bad Request: QuickBooks is not configured for this organisation"
        )

    def test_raises_error_on_unauthorized(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/quickbooks/connect"
            "?company_id=invalid-company-id",
            json={"message": "Invalid 'X-Organisation' header"},
            status=401,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.quickbooks.get_consent_url(
                "invalid-company-id",
            )
        assert str(excinfo.value) == "Unauthorized: Invalid 'X-Organisation' header"

    def test_raises_error_on_internal_server_error(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/quickbooks/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878",
            json={"message": "Internal Server Error"},
            status=500,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.quickbooks.get_consent_url(
                uuid.UUID(
                    "d56b018d-42a3-4f47-b141-44d9d4d81878",
                )
            )
        assert str(excinfo.value) == "Internal Server Error"
