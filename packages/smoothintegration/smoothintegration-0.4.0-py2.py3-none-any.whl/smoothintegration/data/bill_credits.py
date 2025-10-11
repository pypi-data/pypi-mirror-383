from typing import List, Literal, Optional, cast

from typing_extensions import TypedDict

from smoothintegration import _http
from smoothintegration.data.types import AccountRef, CustomerRef, Integration


class BillCreditLineItem(TypedDict):
    total: Optional[str]
    quantity: Optional[str]
    unit_price: Optional[str]
    account: Optional[AccountRef]


BillCreditStatus = Literal["draft", "open", "paid", "void", "deleted"]


class BillCredit(TypedDict):
    id: str
    external_id: str
    integration: Integration
    event_id: str
    number: Optional[str]
    reference: Optional[str]
    sub_total: Optional[str]
    total: Optional[str]
    currency: Optional[str]
    issue_date: Optional[str]
    status: Optional[BillCreditStatus]
    due_date: Optional[str]
    customer: Optional[CustomerRef]
    lines: List[BillCreditLineItem]


class BillCreditsResponse(TypedDict):
    message: str
    has_more: bool
    next_page: str
    result: List[BillCredit]


def get(
    include_raw: Optional[bool] = None,
    limit: Optional[int] = None,
    where: Optional[str] = None,
) -> BillCreditsResponse:
    """
    Retrieve a list of bill credits.
    """
    request_params: dict = {}
    if limit is not None:
        request_params["limit"] = limit
    if include_raw is not None:
        request_params["include_raw"] = "true" if include_raw else "false"
    if where is not None:
        request_params["where"] = where

    return cast(
        BillCreditsResponse,
        _http.request(
            "/v1/data/bill_credits",
            params=request_params,
        ),
    )
