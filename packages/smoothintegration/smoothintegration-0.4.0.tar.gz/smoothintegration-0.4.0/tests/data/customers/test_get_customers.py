import responses

SUCCESS_RESPONSE_BODY = {
    "id": "11111111-1111-1111-1111-111111111111",
    "external_id": "44444444-4444-4444-4444-444444444444",
    "integration": "exact",
    "status": "active",
    "name": "Test Customer",
    "event_id": "200000000000000006",
}


class TestCustomersGet:
    def test_can_retrieve_customers(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/data/customers",
            json=SUCCESS_RESPONSE_BODY,
            status=200,
        )

        response = test_client.data.customers.get()

        assert response == SUCCESS_RESPONSE_BODY

    def test_can_use_all_parameters(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.GET,
            url="https://api.smooth-integration.com/v1/data/customers"
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

        response = test_client.data.customers.get(
            include_raw=True,
            limit=678,
            where="external_id=5678 AND event_id>=200000000000000000 AND integration=exact",
        )

        assert response == SUCCESS_RESPONSE_BODY
