from typing import Literal, Optional, TypedDict

Integration = Literal["xero", "quickbooks", "freeagent", "myob", "exact"]


class AccountRef(TypedDict):
    id: Optional[str]
    external_id: Optional[str]
    nominal_code: Optional[str]
    name: Optional[str]


class CustomerRef(TypedDict):
    id: Optional[str]
    external_id: Optional[str]
    name: Optional[str]
