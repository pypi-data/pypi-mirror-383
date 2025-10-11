import responses

SUCCESS_RESPONSE_BODY = {
    "last_event_id": "123456789012345678",
    "events": [
        {
            "company_id": "00000000-0000-4000-8000-000000000009",
            "connection_id": "00000000-0000-4000-8000-000000000010",
            "event_id": "200000000000000005",
            "document_id": "11111111-1111-1111-1111-111111111111",
            "event": "account",
            "document": {
                "code": "5678",
                "external_id": "1234",
                "id": "11111111-1111-1111-1111-111111111111",
                "integration": "xero",
            },
        }
    ],
}


class TestCDCGet:
    def test_can_retrieve_cdc_events(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/data/cdc?from=0",
            json=SUCCESS_RESPONSE_BODY,
            status=200,
        )

        response = test_client.data.cdc.get(
            from_event_id="0",
        )

        assert response == SUCCESS_RESPONSE_BODY

    def test_can_use_all_parameters(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            url="https://api.smooth-integration.com/v1/data/cdc"
            + "?from=123456789012345678"
            + "&limit=678"
            + "&company_id=a5c8d02c-f8dd-45ee-9495-53c1781501b7"
            + "&connection_id=0730d67d-7d48-4a3a-8a72-04c0a4666fd0"
            + "&event=invoice%2Cbalances"
            + "&include_raw=true",
            json=SUCCESS_RESPONSE_BODY,
            status=200,
        )

        response = test_client.data.cdc.get(
            from_event_id="123456789012345678",
            limit=678,
            company_id="a5c8d02c-f8dd-45ee-9495-53c1781501b7",
            connection_id="0730d67d-7d48-4a3a-8a72-04c0a4666fd0",
            event=["invoice", "balances"],
            include_raw=True,
        )

        assert response == SUCCESS_RESPONSE_BODY
