from typing import List, Optional, cast

from typing_extensions import TypedDict

from smoothintegration import _http
from smoothintegration.data.types import Integration


class Customer(TypedDict):
    id: str
    external_id: str
    integration: Integration
    name: Optional[str]


class CustomersResponse(TypedDict):
    message: str
    has_more: bool
    next_page: str
    result: List[Customer]


def get(
    include_raw: Optional[bool] = None,
    limit: Optional[int] = None,
    where: Optional[str] = None,
) -> CustomersResponse:
    """
    Retrieve a list of customers.
    """
    request_params: dict = {}
    if limit is not None:
        request_params["limit"] = limit
    if include_raw is not None:
        request_params["include_raw"] = "true" if include_raw else "false"
    if where is not None:
        request_params["where"] = where

    return cast(
        CustomersResponse,
        _http.request(
            "/v1/data/customers",
            params=request_params,
        ),
    )
