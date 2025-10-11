import uuid

import pytest
import responses

from smoothintegration.exceptions import SIError


class TestZohoBooksGetConsentUrl:

    def test_can_get_consent_url_for_eu(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/zohobooks/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=eu",
            json={
                "message": "Created Consent Url",
                "result": {
                    "consentUrl": "the-consent-url",
                },
            },
            status=200,
        )

        assert (
            test_client.zohobooks.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                "eu",
            )
            == "the-consent-url"
        )

    def test_can_get_consent_url_for_us(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/zohobooks/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=us",
            json={
                "message": "Created Consent Url",
                "result": {
                    "consentUrl": "the-consent-url",
                },
            },
            status=200,
        )

        assert (
            test_client.zohobooks.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                "us",
            )
            == "the-consent-url"
        )

    def test_can_pass_optional_state_parameter(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/zohobooks/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=eu"
            "&state=51da0abd-beba-4882-a5b6-b3f8d61e8456",
            json={
                "message": "Created Consent Url",
                "result": {
                    "consentUrl": "the-consent-url",
                },
            },
            status=200,
        )

        assert (
            test_client.zohobooks.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                "eu",
                "51da0abd-beba-4882-a5b6-b3f8d61e8456",
            )
            == "the-consent-url"
        )

    def test_can_pass_optional_single_parameter(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/zohobooks/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=eu"
            "&single=true",
            json={
                "message": "Created Consent Url",
                "result": {
                    "consentUrl": "the-consent-url",
                },
            },
            status=200,
        )

        assert (
            test_client.zohobooks.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                "eu",
                single=True,
            )
            == "the-consent-url"
        )

    def test_can_pass_all_optional_parameters(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/zohobooks/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=eu"
            "&state=some-value"
            "&single=true",
            json={
                "message": "Created Consent Url",
                "result": {
                    "consentUrl": "the-consent-url",
                },
            },
            status=200,
        )

        assert (
            test_client.zohobooks.get_consent_url(
                company_id=uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                version="eu",
                state="some-value",
                single=True,
            )
            == "the-consent-url"
        )

    def test_raises_error_on_bad_request(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/zohobooks/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=eu",
            json={
                "message": "ZohoBooks is not yet enabled for this organisation.\nHint: you can enable ZohoBooks in the SmoothIntegration dashboard at https://app.smooth-integration.com/integrations"},
            status=400,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.zohobooks.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                "eu",
            )
        assert (
            str(excinfo.value)
            == "Bad Request: ZohoBooks is not yet enabled for this organisation.\nHint: you can enable ZohoBooks in the SmoothIntegration dashboard at https://app.smooth-integration.com/integrations"
        )

    def test_raises_error_on_unauthorized(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/zohobooks/connect"
            "?company_id=invalid-company-id"
            "&version=eu",
            json={"message": "Invalid 'X-Organisation' header"},
            status=401,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.zohobooks.get_consent_url(
                "invalid-company-id",
                "eu",
            )
        assert str(excinfo.value) == "Unauthorized: Invalid 'X-Organisation' header"

    def test_raises_error_on_internal_server_error(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/zohobooks/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=eu",
            json={"message": "Internal Server Error"},
            status=500,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.zohobooks.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                "eu",
            )
        assert str(excinfo.value) == "Internal Server Error"
