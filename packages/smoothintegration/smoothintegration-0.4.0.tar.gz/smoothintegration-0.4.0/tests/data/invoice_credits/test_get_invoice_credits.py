import responses

SUCCESS_RESPONSE_BODY = {
    "id": "11111111-1111-1111-1111-111111111111",
    "lines": [
        {
            "total": "5200",
            "account": {
                "id": "55555555-5555-5555-5555-555555555555",
                "name": "Sales",
                "external_id": "66666666-6666-6666-6666-666666666666",
            },
            "quantity": "1",
            "unit_price": "5200",
        }
    ],
    "total": "5200",
    "number": "3",
    "status": "open",
    "currency": "GBP",
    "customer": {
        "id": "22222222-2222-2222-2222-222222222222",
        "external_id": "33333333-3333-3333-3333-333333333333",
        "name": "Test Customer",
    },
    "due_date": "2025-04-03T00:00:00.000Z",
    "sub_total": "5200",
    "issue_date": "2025-03-04T00:00:00.000Z",
    "external_id": "44444444-4444-4444-4444-444444444444",
    "integration": "exact",
    "event_id": "200000000000000006",
}


class TestInvoiceCreditsGet:
    def test_can_retrieve_invoice_credits(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/data/invoice_credits",
            json=SUCCESS_RESPONSE_BODY,
            status=200,
        )

        response = test_client.data.invoice_credits.get()

        assert response == SUCCESS_RESPONSE_BODY

    def test_can_use_all_parameters(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            url="https://api.smooth-integration.com/v1/data/invoice_credits"
            + "?limit=678"
            + "&include_raw=true"
            + "&where="
            "external_id%3D5678"
            "+AND+"
            "event_id%3E%3D200000000000000000"
            "+AND+"
            "integration%3Dexact",
            json=SUCCESS_RESPONSE_BODY,
            status=200,
        )

        response = test_client.data.invoice_credits.get(
            include_raw=True,
            limit=678,
            where="external_id=5678"
            " AND event_id>=200000000000000000"
            " AND integration=exact",
        )

        assert response == SUCCESS_RESPONSE_BODY
