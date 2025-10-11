import uuid

import pytest
import responses

from smoothintegration.exceptions import SIError


class TestExactGetConsentUrl:

    def test_can_get_consent_url_for_uk(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/exact/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=uk",
            json={
                "message": "Created Consent Url",
                "result": {
                    "consentUrl": "the-consent-url",
                },
            },
            status=200,
        )

        assert (
            test_client.exact.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                "uk",
            )
            == "the-consent-url"
        )

    def test_can_get_consent_url_for_nl(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/exact/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=nl",
            json={
                "message": "Created Consent Url",
                "result": {
                    "consentUrl": "the-consent-url",
                },
            },
            status=200,
        )

        assert (
            test_client.exact.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                "nl",
            )
            == "the-consent-url"
        )

    def test_can_pass_optional_state_parameter(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/exact/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=uk"
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
            test_client.exact.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                "uk",
                "51da0abd-beba-4882-a5b6-b3f8d61e8456",
            )
            == "the-consent-url"
        )

    def test_can_pass_optional_single_parameter(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/exact/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=uk"
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
            test_client.exact.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                "uk",
                single=True,
            )
            == "the-consent-url"
        )

    def test_can_pass_all_optional_parameters(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/exact/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=uk"
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
            test_client.exact.get_consent_url(
                company_id=uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                version="uk",
                state="some-value",
                single=True
            )
            == "the-consent-url"
        )

    def test_raises_error_on_bad_request(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/exact/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=uk",
            json={"message": "Exact is not configured for this organisation"},
            status=400,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.exact.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                "uk",
            )
        assert (
            str(excinfo.value)
            == "Bad Request: Exact is not configured for this organisation"
        )

    def test_raises_error_on_unauthorized(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/exact/connect"
            "?company_id=invalid-company-id"
            "&version=uk",
            json={"message": "Invalid 'X-Organisation' header"},
            status=401,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.exact.get_consent_url(
                "invalid-company-id",
                "uk",
            )
        assert str(excinfo.value) == "Unauthorized: Invalid 'X-Organisation' header"

    def test_raises_error_on_internal_server_error(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/exact/connect"
            "?company_id=d56b018d-42a3-4f47-b141-44d9d4d81878"
            "&version=uk",
            json={"message": "Internal Server Error"},
            status=500,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.exact.get_consent_url(
                uuid.UUID("d56b018d-42a3-4f47-b141-44d9d4d81878"),
                "uk",
            )
        assert str(excinfo.value) == "Internal Server Error"
