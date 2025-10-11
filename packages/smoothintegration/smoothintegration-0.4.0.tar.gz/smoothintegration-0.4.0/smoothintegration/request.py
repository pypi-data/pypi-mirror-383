import uuid

import requests

from smoothintegration import _http
from smoothintegration.exceptions import SIError


def make_request(
    connection_id: uuid.UUID,
    path: str,
    **kwargs,
) -> requests.Response:
    """
    Make a HTTP request directly to the third party API. This is used as you would the Python requests library.
    All Authorization is handled by SmoothIntegration, so do not pass any Authorization headers like "Authorization" or "Xero-Tenant-Id".

    Example:

    >>> smoothintegration.request.make_request(
    >>>     uuid.UUID("3a739c6e-d4bc-4b40-ae52-bc8b01bb9973"),
    >>>     path="/Invoices",
    >>>     method="POST",
    >>>     json={'foo': 'bar'},
    >>>     # any other kwargs are passed to the requests library like "headers" or "params"
    >>> )

    :returns: The Response from the third party API as is.
    :raises SIError: if there was an issue preparing the authorization.
    """

    if not path.startswith("/"):
        raise SIError("path must start with a /")

    # Do not allow the "url" to be passed in the kwargs
    if "url" in kwargs:
        raise SIError("url is not allowed in kwargs. The url will be constructed automatically based on the connection_id and path provided")

    return _http._raw_request(
        **kwargs,
        url="/v1/request/" + str(connection_id) + path,
    )
