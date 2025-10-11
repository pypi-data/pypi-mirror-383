import datetime
import hashlib
import hmac
from http import HTTPStatus
from typing import Optional, Tuple

import requests
from requests import PreparedRequest

from smoothintegration.exceptions import SIError


def _generate_hmac(
    request: PreparedRequest,
) -> Tuple[str, str]:
    timestamp = (
        datetime.datetime.utcnow().isoformat(sep="T", timespec="milliseconds") + "Z"
    )
    from smoothintegration import client_id, client_secret

    # Prepare the initial HMAC payload
    hmac_payload = f"{client_id}{request.method}{request.url}{timestamp}".encode(
        "utf-8"
    )

    # Add raw body to the HMAC if present
    if request.body is not None:
        hmac_payload += request.body

    # Create and calculate the HMAC
    hmac_obj = hmac.new(client_secret.encode("utf-8"), hmac_payload, hashlib.sha256)
    return hmac_obj.hexdigest(), timestamp


def _raw_request(
    **kwargs: any,
) -> requests.Response:
    # create the Request instance, and then do the request
    from smoothintegration import client_id

    url = kwargs.pop("url")
    passed_headers = kwargs.pop("headers", {})
    method = kwargs.pop("method", "GET")
    req = requests.Request(
        method=method,
        url="https://api.smooth-integration.com" + url,
        headers={
            "X-Organisation": client_id,
            "Content-Type": "application/json; charset=utf-8",
            **passed_headers,
        },
        **kwargs,
    )
    prepared_request = req.prepare()

    # generate and include the hmac headers in the request
    signature, timestamp = _generate_hmac(prepared_request)
    prepared_request.headers["X-Signature"] = signature
    prepared_request.headers["X-Timestamp"] = timestamp

    # do the request
    with requests.Session() as session:
        return session.send(prepared_request)


def request(
    url: str,
    **kwargs: any,
) -> object:
    """
    Perform an HTTP request to the SmoothIntegration API.

    :returns: the response body on any 2xx status code. Otherwise, raises smoothintegration.SIError
    :raises smoothintegration.SIError: if the request fails for any reason.
    """
    response = _raw_request(url=url, **kwargs)

    response_body: Optional[dict] = None
    response_message: Optional[str] = None
    parsing_failed = False
    try:
        response_body = response.json()
        response_message = response_body.get("message")
    except Exception:
        parsing_failed = True

    if response.status_code >= 500:
        raise SIError(HTTPStatus(response.status_code).phrase)

    if response.status_code < 200 or response.status_code >= 300:
        raise SIError(
            f"{HTTPStatus(response.status_code).phrase}: {response_message}"
        )

    if parsing_failed:
        raise SIError("Failed to parse response body as JSON")

    return response_body
