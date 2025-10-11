import time

import responses


class TestCDCGet:

    def test_can_stream_cdc_events(self, mocked_responses, test_client, monkeypatch):
        # Scenario:
        # Start streaming, makes request immediately, gets 10 events with flag "has_more"
        # Because has_more is true, it immediately makes the next request
        # Second request returns 2 elements with has_more = false
        # It should then wait 5 seconds and make the third request

        # Mock time.sleep to do nothing
        monkeypatch.setattr(time, "sleep", lambda x: None)

        # First request
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/data/cdc?from=0&limit=10&event=invoice",
            json={
                "message": "Successfully retrieved events",
                "last_event_id": "100000000000000014",
                "has_more": True,
                "next_page": "/v1/data/cdc?from=100000000000000014",
                "result": [
                    {"event_id": "100000000000000001"},
                    {"event_id": "100000000000000002"},
                    {"event_id": "100000000000000004"},
                    {"event_id": "100000000000000007"},
                    {"event_id": "100000000000000008"},
                    {"event_id": "100000000000000009"},
                    {"event_id": "100000000000000010"},
                    {"event_id": "100000000000000011"},
                    {"event_id": "100000000000000013"},
                    {"event_id": "100000000000000014"},
                ],
            },
            status=200,
        )

        # Second request
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/data/cdc?from=100000000000000014&limit=10&event=invoice",
            json={
                "message": "Successfully retrieved events",
                "last_event_id": "100000000000000016",
                "has_more": False,
                "next_page": "/v1/data/cdc?from=100000000000000016",
                "result": [
                    {"event_id": "100000000000000015"},
                    {"event_id": "100000000000000016"},
                ],
            },
            status=200,
        )

        # Third request
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/data/cdc?from=100000000000000016&limit=10&event=invoice",
            json={
                "message": "Successfully retrieved events",
                "last_event_id": None,
                "has_more": False,
                "next_page": "/v1/data/cdc?from=100000000000000016",
                "result": [],
            },
            status=200,
        )

        # Fourth request
        mocked_responses.add(
            responses.GET,
            "https://api.smooth-integration.com/v1/data/cdc?from=100000000000000016&limit=10&event=invoice",
            json={
                "message": "Successfully retrieved events",
                "last_event_id": "100000000000000023",
                "has_more": False,
                "next_page": "",
                "result": [
                    {"event_id": "100000000000000021"},
                    {"event_id": "100000000000000023"},
                ],
            },
            status=200,
        )

        # Run through the scenario
        events_generator = test_client.data.cdc.stream(
            from_event_id="0",
            limit=10,
            event=["invoice"],
        )

        events = []
        for i, e in enumerate(events_generator):
            events.append(e)
            if i >= 13:
                break

        # Should contain all events
        assert events == [
            {"event_id": "100000000000000001"},
            {"event_id": "100000000000000002"},
            {"event_id": "100000000000000004"},
            {"event_id": "100000000000000007"},
            {"event_id": "100000000000000008"},
            {"event_id": "100000000000000009"},
            {"event_id": "100000000000000010"},
            {"event_id": "100000000000000011"},
            {"event_id": "100000000000000013"},
            {"event_id": "100000000000000014"},
            {"event_id": "100000000000000015"},
            {"event_id": "100000000000000016"},
            {"event_id": "100000000000000021"},
            {"event_id": "100000000000000023"},
        ]
