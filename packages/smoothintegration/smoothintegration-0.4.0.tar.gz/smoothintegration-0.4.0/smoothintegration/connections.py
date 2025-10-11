import uuid
from typing import Literal, Optional, TypedDict, cast

from smoothintegration import _http


class Connection(TypedDict):
    id: uuid.UUID
    company_id: uuid.UUID
    integration: Literal["xero", "quickbooks", "freeagent", "myob", "exact"]
    external_name: str
    external_id: str
    scopes: list[str]
    data: dict
    created_at: str
    is_sandbox: bool
    status: Literal["connected", "externally_disconnected", "internally_disconnected"]


class GetConnectionResponse(TypedDict):
    message: str
    result: Connection


class ConnectionImportTask(TypedDict):
    task: str
    task_id: uuid.UUID


class ConnectionImport(TypedDict):
    import_id: uuid.UUID
    company_id: uuid.UUID
    connection_id: uuid.UUID
    tasks: list[ConnectionImportTask]


class StartImportResponse(TypedDict):
    message: str
    result: ConnectionImport


def get_connection(connection_id: uuid.UUID) -> Optional[Connection]:
    """
    Get an existing Connection from SmoothIntegration.

    :param connection_id: The ID of the connection to retrieve.

    :returns: The Connection object.
    :raises SIError: if the request failed for any reason.
    """
    response = cast(
        GetConnectionResponse,
        _http.request("/v1/connections/" + str(connection_id), method="GET"),
    )

    return response["result"]


def start_import(connection_id: uuid.UUID) -> ConnectionImport:
    """
    Start a new import for the given connection.

    :param connection_id: The ID of the connection to start importing the latest data for.

    :returns: An object describing the started import.
    :raises SIError: if the request failed for any reason.
    """
    response = cast(
        StartImportResponse,
        _http.request(
            "/v1/connections/" + str(connection_id) + "/import", method="POST"
        ),
    )

    return response["result"]
