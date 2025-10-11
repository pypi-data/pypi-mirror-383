import hashlib
import hmac

import responses
from freezegun import freeze_time
from responses import matchers

from smoothintegration import _http


def _generate_hmac(payload: str) -> str:
    return hmac.new(
        "1Nruyd8CrGPZsa88lZhxcYXfBB2Jv96900wjNst7FtQ".encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


@freeze_time("2025-03-20 12:00:00", tz_offset=0)
class TestHTTP:
    def test_adds_required_auth_headers_get(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/data/accounts",
            json={"success": "true"},
            status=200,
            match=[
                matchers.header_matcher(
                    {
                        "X-Organisation": "a4a0a676-a645-4efc-bf1e-6f98631ae204",
                        "X-Timestamp": "2025-03-20T12:00:00.000Z",
                        "X-Signature": _generate_hmac(
                            "a4a0a676-a645-4efc-bf1e-6f98631ae204"
                            + "GET"
                            + "https://api.smooth-integration.com/v1/data/accounts"
                            + "2025-03-20T12:00:00.000Z"
                        ),
                    }
                )
            ],
        )

        response = _http.request(
            "/v1/data/accounts",
            method="GET",
        )

        assert response == {"success": "true"}

    def test_adds_required_auth_headers_with_query_params(
        self, mocked_responses, test_client
    ):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/data/accounts?where=event_id%3E1234",
            json={"success": "true"},
            status=200,
            match=[
                matchers.header_matcher(
                    {
                        "X-Organisation": "a4a0a676-a645-4efc-bf1e-6f98631ae204",
                        "X-Timestamp": "2025-03-20T12:00:00.000Z",
                        "X-Signature": _generate_hmac(
                            "a4a0a676-a645-4efc-bf1e-6f98631ae204"
                            + "GET"
                            + "https://api.smooth-integration.com/v1/data/accounts?where=event_id%3E1234"
                            + "2025-03-20T12:00:00.000Z"
                        ),
                    }
                )
            ],
        )

        response = _http.request(
            "/v1/data/accounts",
            method="GET",
            params={"where": "event_id>1234"},
        )

        assert response == {"success": "true"}

    def test_adds_required_auth_headers_with_many_query_params(
        self, mocked_responses, test_client
    ):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/data/cdc"
            "?from_event_id=1234"
            + "&connection=22222222-2222-2222-2222-222222222222"
            + "&include_raw=true"
            + "&event=invoice%2Cbill%2Csupplier%2Cconnection"
            + "&company=11111111-1111-1111-1111-111111111111"
            + "&limit=10",
            json={"success": "true"},
            status=200,
            match=[
                matchers.header_matcher(
                    {
                        "X-Organisation": "a4a0a676-a645-4efc-bf1e-6f98631ae204",
                        "X-Timestamp": "2025-03-20T12:00:00.000Z",
                        "X-Signature": _generate_hmac(
                            "a4a0a676-a645-4efc-bf1e-6f98631ae204"
                            + "GET"
                            + "https://api.smooth-integration.com/v1/data/cdc"
                            "?from_event_id=1234"
                            + "&connection=22222222-2222-2222-2222-222222222222"
                            + "&include_raw=true"
                            + "&event=invoice%2Cbill%2Csupplier%2Cconnection"
                            + "&company=11111111-1111-1111-1111-111111111111"
                            + "&limit=10"
                            + "2025-03-20T12:00:00.000Z"
                        ),
                    }
                )
            ],
        )

        response = _http.request(
            "/v1/data/cdc",
            method="GET",
            params={
                "from_event_id": "1234",
                "connection": "22222222-2222-2222-2222-222222222222",
                "include_raw": "true",
                "event": "invoice,bill,supplier,connection",
                "company": "11111111-1111-1111-1111-111111111111",
                "limit": 10,
            },
        )

        assert response == {"success": "true"}

    def test_adds_required_auth_headers_post(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.POST,
            "https://api.smooth-integration.com/v1/companies",
            json={"success": "true"},
            status=200,
            match=[
                matchers.header_matcher(
                    {
                        "X-Organisation": "a4a0a676-a645-4efc-bf1e-6f98631ae204",
                        "X-Timestamp": "2025-03-20T12:00:00.000Z",
                        "X-Signature": _generate_hmac(
                            "a4a0a676-a645-4efc-bf1e-6f98631ae204"
                            + "POST"
                            + "https://api.smooth-integration.com/v1/companies"
                            + "2025-03-20T12:00:00.000Z"
                            + '{"name": "Test Company"}'
                        ),
                    }
                )
            ],
        )

        response = _http.request(
            "/v1/companies",
            method="POST",
            json={"name": "Test Company"},
        )

        assert response == {"success": "true"}
