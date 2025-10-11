from typing import List, Literal, Optional, cast

from typing_extensions import TypedDict

from smoothintegration import _http
from smoothintegration.data.types import Integration

AccountClassification = Literal["income", "expense", "asset", "liability", "equity"]

AccountStatus = Literal["active", "archived", "deleted"]


class Account(TypedDict):
    id: str
    external_id: str
    integration: Integration
    event_id: str
    status: AccountStatus
    nominal_code: Optional[str]
    classification: Optional[AccountClassification]
    name: Optional[str]


class AccountsResponse(TypedDict):
    message: str
    has_more: bool
    next_page: str
    result: List[Account]


def get(
    include_raw: Optional[bool] = None,
    limit: Optional[int] = None,
    where: Optional[str] = None,
) -> AccountsResponse:
    """
    Retrieve a list of accounts.
    """
    request_params: dict = {}
    if limit is not None:
        request_params["limit"] = limit
    if include_raw is not None:
        request_params["include_raw"] = "true" if include_raw else "false"
    if where is not None:
        request_params["where"] = where

    return cast(
        AccountsResponse,
        _http.request(
            "/v1/data/accounts",
            params=request_params,
        ),
    )
