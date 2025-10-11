from typing import List, Optional, cast

from typing_extensions import TypedDict

from smoothintegration import _http
from smoothintegration.data.types import AccountRef, Integration


class ProfitAndLossBalance(TypedDict):
    account: AccountRef
    balance: str


class ProfitAndLossRecord(TypedDict):
    id: str
    integration: Integration
    event_id: str
    month: str
    balances: list[ProfitAndLossBalance]


class ProfitAndLossConfig(TypedDict):
    include_raw: Optional[bool]
    limit: Optional[int]
    where: Optional[str]


class ProfitAndLossResponse(TypedDict):
    message: str
    has_more: bool
    next_page: str
    result: List[ProfitAndLossRecord]


def get(
    include_raw: Optional[bool] = None,
    limit: Optional[int] = None,
    where: Optional[str] = None,
) -> ProfitAndLossResponse:
    """
    Retrieve a list of profit and loss monthly balances.
    """
    request_params: dict = {}
    if limit is not None:
        request_params["limit"] = limit
    if include_raw is not None:
        request_params["include_raw"] = "true" if include_raw else "false"
    if where is not None:
        request_params["where"] = where

    return cast(
        ProfitAndLossResponse,
        _http.request(
            "/v1/data/profit_and_loss",
            params=request_params,
        ),
    )
