import uuid
from datetime import datetime
from typing import Optional, TypedDict, cast, List

from smoothintegration import _http


class Company(TypedDict):
    id: uuid.UUID
    name: str
    created_at: str
    integrations: List[str]


class ListCompaniesResponse(TypedDict):
    message: str
    result: List[Company]


def list_companies() -> Optional[List[Company]]:
    """
    List all Companies from SmoothIntegration.

    :returns: List of Companies
    :raises SIError: if the data could not be retrieved for any reason.
    """
    response = cast(
        ListCompaniesResponse,
        _http.request("/v1/companies", method="GET"),
    )

    def parse_company(company):
        company["created_at"] = datetime.fromisoformat(company["created_at"])
        return company

    return list(map(parse_company, response["result"]))


class DetailedCompanyConnection(TypedDict):
    id: str
    integration: str
    is_sandbox: bool
    status: str
    external_name: str
    external_id: str
    created_at: str


class DetailedCompany(TypedDict):
    id: uuid.UUID
    name: str
    created_at: str
    connections: List[DetailedCompanyConnection]


class GetCompanyResponse(TypedDict):
    message: str
    result: DetailedCompany


def get_company(company_id: uuid.UUID) -> Optional[Company]:
    """
    Get an existing Company from SmoothIntegration.

    :param company_id: The ID of the company to retrieve.

    :returns: The Company or None
    :raises SIError: if the data could not be retrieved for any reason.
    """
    response = cast(
        GetCompanyResponse,
        _http.request("/v1/companies/" + str(company_id), method="GET"),
    )

    return response["result"]


class CreateCompanyPayload(TypedDict):
    name: str


class CreateCompanyResponse(TypedDict):
    message: str
    result: Company


def create_company(company: CreateCompanyPayload) -> Company:
    """
    Create a new Company in SmoothIntegration.

    :param company: An object containing details about the company to be created.
        - name (str): The name of the company.

    :returns: The Created Company
    :raises SIError: if the consent url could not be retrieved for any reason.
    """
    response = cast(
        CreateCompanyResponse,
        _http.request("/v1/companies", method="POST", json=company),
    )

    return response["result"]
