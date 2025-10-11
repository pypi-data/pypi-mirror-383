import responses

SUCCESS_RESPONSE_BODY = {
    "id": "11111111-1111-1111-1111-111111111111",
    "lines": [
        {
            "total": "-3680",
            "account": {
                "id": "96559927-7495-2a53-a770-be6e0b408895",
                "name": "Sales",
                "external_id": "d23e205b-b039-4711-a852-ed3dbac2ee9a",
            },
            "quantity": "16",
            "unit_price": "230",
        }
    ],
    "total": "4416",
    "number": "1",
    "status": "paid",
    "currency": "GBP",
    "customer": {
        "id": "22222222-2222-2222-2222-222222222222",
        "external_id": "33333333-3333-3333-3333-333333333333",
        "name": "Test Customer",
    },
    "due_date": "2025-02-01T00:00:00.000Z",
    "sub_total": "3680",
    "issue_date": "2025-01-01T00:00:00.000Z",
    "external_id": "44444444-4444-4444-4444-444444444444",
    "integration": "exact",
    "event_id": "200000000000000006",
}


class TestBillsGet:
    def test_can_retrieve_bills(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/data/bills",
            json=SUCCESS_RESPONSE_BODY,
            status=200,
        )

        response = test_client.data.bills.get()

        assert response == SUCCESS_RESPONSE_BODY

    def test_can_use_all_parameters(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            url="https://api.smooth-integration.com/v1/data/bills"
            + "?limit=678"
            + "&include_raw=true"
            + "&where="
            "external_id%3D5678"
            "+AND+"
            "event_id%3E%3D200000000000000000"
            "+AND+"
            "integration%3Dexact"
            "+AND+"
            "issue_date%3D2024-02-12"
            "+AND+"
            "total%3C5000"
            "+AND+"
            "due_amount%21%3D0",
            json=SUCCESS_RESPONSE_BODY,
            status=200,
        )

        response = test_client.data.bills.get(
            include_raw=True,
            limit=678,
            where="external_id=5678"
            " AND event_id>=200000000000000000"
            " AND integration=exact"
            " AND issue_date=2024-02-12"
            " AND total<5000"
            " AND due_amount!=0",
        )

        assert response == SUCCESS_RESPONSE_BODY
