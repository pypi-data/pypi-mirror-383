import uuid

import pytest
import responses
from freezegun import freeze_time
from responses import matchers

from smoothintegration.exceptions import SIError


class TestRequest:

    def test_can_make_minimal_get_request(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/request/9d952948-1697-4282-b2d0-e19ea0098723/Invoices",
            json={
                "example": "response",
            },
            status=200,
        )

        response = test_client.request.make_request(
            uuid.UUID("9d952948-1697-4282-b2d0-e19ea0098723"),
            path="/Invoices"
        )
        assert response.status_code == 200
        assert response.json() == {"example": "response"}

    def test_can_pass_query_parameters(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/request/9d952948-1697-4282-b2d0-e19ea0098723/Invoices?foo=bar",
            json={
                "example": "response",
            },
            status=200,
        )

        response = test_client.request.make_request(
            uuid.UUID("9d952948-1697-4282-b2d0-e19ea0098723"),
            path="/Invoices",
            params={"foo": "bar"},
        )
        assert response.status_code == 200
        assert response.json() == {"example": "response"}

    @freeze_time("2025-03-20 12:00:00", tz_offset=0)
    def test_can_pass_headers(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/request/9d952948-1697-4282-b2d0-e19ea0098723/Invoices",
            match=[
                matchers.header_matcher(
                    {
                        "foo": "bar",
                        # The headers produced by the http utility should remain
                        "X-Organisation": "a4a0a676-a645-4efc-bf1e-6f98631ae204",
                        "X-Timestamp": "2025-03-20T12:00:00.000Z",
                        "X-Signature": "f6a9c9730ecaaa7d602bb1986d8b51f25a1f03784a727b07f46dcc8e97048a91",
                    }
                )],
            json={
                "example": "response",
            },
            status=200,
        )

        response = test_client.request.make_request(
            uuid.UUID("9d952948-1697-4282-b2d0-e19ea0098723"),
            path="/Invoices",
            headers={"foo": "bar"},
        )
        assert response.status_code == 200
        assert response.json() == {"example": "response"}

    def test_can_make_post_request_with_body(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.POST,
            "https://api.smooth-integration.com/v1/request/9d952948-1697-4282-b2d0-e19ea0098723/Invoices",
            match=[matchers.json_params_matcher({"foo": "bar"})],
            json={
                "example": "response",
            },
            status=200,
        )

        response = test_client.request.make_request(
            uuid.UUID("9d952948-1697-4282-b2d0-e19ea0098723"),
            path="/Invoices",
            method="POST",
            json={"foo": "bar"},
        )
        assert response.status_code == 200
        assert response.json() == {"example": "response"}

    def test_returns_any_response_as_is(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/request/9d952948-1697-4282-b2d0-e19ea0098723/Invoices",
            json={
                "error": "Internal Server Error",
            },
            status=500,
        )

        # Making the request should return the response as is, without raising any exceptions
        response = test_client.request.make_request(
            uuid.UUID("9d952948-1697-4282-b2d0-e19ea0098723"),
            path="/Invoices",
        )
        assert response.status_code == 500
        assert response.json() == {"error": "Internal Server Error"}

    def test_rejects_passing_of_url_kwarg(self, mocked_responses, test_client):
        with pytest.raises(SIError) as excinfo:
            test_client.request.make_request(
                uuid.UUID("9d952948-1697-4282-b2d0-e19ea0098723"),
                path="/Invoices",
                url="https://api.smooth-integration.com/v1/9d952948-1697-4282-b2d0-e19ea0098723/Invoices",
            )
        assert str(excinfo.value) == "url is not allowed in kwargs. The url will be constructed automatically based on the connection_id and path provided"
