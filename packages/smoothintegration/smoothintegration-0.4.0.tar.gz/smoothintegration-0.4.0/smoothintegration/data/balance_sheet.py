from typing import List, Optional, cast

from typing_extensions import TypedDict

from smoothintegration import _http
from smoothintegration.data.types import AccountRef, Integration


class BalanceSheetBalance(TypedDict):
    account: AccountRef
    balance: str


class BalanceSheetRecord(TypedDict):
    id: str
    integration: Integration
    event_id: str
    month: str
    balances: list[BalanceSheetBalance]


class BalanceSheetResponse(TypedDict):
    message: str
    has_more: bool
    next_page: str
    result: List[BalanceSheetRecord]


def get(
    include_raw: Optional[bool] = None,
    limit: Optional[int] = None,
    where: Optional[str] = None,
) -> BalanceSheetResponse:
    """
    Retrieve a list of balance sheet monthly balances.
    """
    request_params: dict = {}
    if limit is not None:
        request_params["limit"] = limit
    if include_raw is not None:
        request_params["include_raw"] = "true" if include_raw else "false"
    if where is not None:
        request_params["where"] = where

    return cast(
        BalanceSheetResponse,
        _http.request(
            "/v1/data/balance_sheet",
            params=request_params,
        ),
    )
