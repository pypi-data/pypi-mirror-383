import pytest
import responses


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
        yield rsps


@pytest.fixture
def test_client():
    import smoothintegration

    smoothintegration.client_id = "a4a0a676-a645-4efc-bf1e-6f98631ae204"
    smoothintegration.client_secret = "1Nruyd8CrGPZsa88lZhxcYXfBB2Jv96900wjNst7FtQ"

    return smoothintegration
