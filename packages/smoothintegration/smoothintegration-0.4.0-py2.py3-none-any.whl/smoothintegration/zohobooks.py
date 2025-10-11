import uuid
from typing import Literal, TypedDict, cast, Optional

from smoothintegration import _http

ZohoBooksVersion = Literal["us", "eu", "in", "au", "jp", "ca", "cn", "sa"]


class GetConsentUrlResponseResult(TypedDict):
    consentUrl: str


class GetConsentUrlResponse(TypedDict):
    message: str
    result: GetConsentUrlResponseResult


def get_consent_url(
    company_id: uuid.UUID,
    version: str,
    state: Optional[str] = None,
    single: Optional[bool] = False,
) -> str:
    """
    Get the URL to redirect the user to in order to get consent to connect to an ZohoBooks company.

    :param company_id: The ID of the SmoothIntegration company to add this new Connection to.
    :param version: Version of ZohoBooks to connect to. One of "us", "eu", "in", "au", "jp", "ca", "cn", "sa".
    :param state: Optional string. This will be returned to the success page on a new connection.
    :param single: Optional boolean. If set to true, the user will be asked which single organisation to connect,
    instead of connection all organisations at once.

    :returns: The URL to redirect the user to in order to get consent.
    :raises SIError: if the consent url could not be retrieved for any reason.
    """
    request_params = {
        "company_id": company_id,
        "version": version,
    }

    if state is not None:
        request_params["state"] = state

    if single is True:
        request_params["single"] = "true"

    response = cast(
        GetConsentUrlResponse,
        _http.request("/v1/zohobooks/connect", params=request_params),
    )

    return response["result"]["consentUrl"]
