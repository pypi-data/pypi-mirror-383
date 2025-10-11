import responses

SUCCESS_RESPONSE_BODY = {
    "id": "11111111-1111-1111-1111-111111111111",
    "integration": "exact",
    "event_id": "200000000000000006",
    "month": "2025-03",
    "balances": [
        {
            "account": {
                "id": "55555555-5555-5555-5555-555555555555",
                "name": "Sales",
                "external_id": "66666666-6666-6666-6666-666666666666",
                "nominal_code": "200",
            },
            "balance": "-3680",
        }
    ],
}


class TestProfitAndLossGet:
    def test_can_retrieve_profit_and_loss(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/data/profit_and_loss",
            json=SUCCESS_RESPONSE_BODY,
            status=200,
        )

        response = test_client.data.profit_and_loss.get()

        assert response == SUCCESS_RESPONSE_BODY

    def test_can_use_all_parameters(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            url="https://api.smooth-integration.com/v1/data/profit_and_loss"
            + "?limit=678"
            + "&include_raw=true"
            + "&where="
            "event_id%3E%3D200000000000000000"
            "+AND+"
            "integration%3Dexact"
            "+AND+"
            "month>=2022-01-01"
            "+AND+"
            "month<2026-01-01",
            json=SUCCESS_RESPONSE_BODY,
            status=200,
        )

        response = test_client.data.profit_and_loss.get(
            include_raw=True,
            limit=678,
            where="event_id>=200000000000000000 AND integration=exact AND month>=2022-01-01 AND month<2026-01-01",
        )

        assert response == SUCCESS_RESPONSE_BODY
