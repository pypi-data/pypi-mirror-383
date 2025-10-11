import time
from typing import Generator, List, Optional, cast

from typing_extensions import TypedDict

from smoothintegration import _http


class Event(TypedDict):
    company_id: str
    connection_id: str
    event_id: str
    document_id: str
    event: str
    document: dict
    raw_document: dict


class CDCResponse(TypedDict):
    message: str
    last_event_id: Optional[str]
    has_more: bool
    next_page: str
    result: List[Event]


def get(
    from_event_id: str,
    limit: Optional[int] = None,
    company_id: Optional[str] = None,
    connection_id: Optional[str] = None,
    event: Optional[List[str]] = None,
    include_raw: Optional[bool] = None,
) -> CDCResponse:
    """
    Retrieves a batch of Continuous Data Capture (CDC) events from the API.

    Args:
        - from_event_id (str): The starting event ID to retrieve data from.
        - limit (int, optional): Maximum number of results to retrieve per request.
        - company_id (str, optional): Company ID to filter results.
        - connection_id (str, optional): Connection ID to filter results.
        - event (List[str], optional): List of event types to filter by.
        - include_raw (bool, optional): Flag to include raw data in results.

    Returns:
        CDCResponse: A dictionary containing the API response, including a list of events,
                     pagination details, and message metadata.
            - message (str): A message indicating the success or failure of the request.
            - last_event_id (str): The ID of the last event retrieved.
            - has_more (bool): Flag indicating whether there are more results to fetch.
            - next_page (str): URL to fetch the next page of results.
            - result (List[Event]): List of CDC events retrieved.

    """
    request_params: dict = {
        "from": from_event_id,
    }
    if limit is not None:
        request_params["limit"] = limit
    if company_id is not None:
        request_params["company_id"] = company_id
    if connection_id is not None:
        request_params["connection_id"] = connection_id
    if event is not None:
        request_params["event"] = ",".join(event)
    if include_raw is not None:
        request_params["include_raw"] = "true" if include_raw else "false"

    return cast(CDCResponse, _http.request("/v1/data/cdc", params=request_params))


def stream(
    from_event_id: str,
    limit: Optional[int] = None,
    company_id: Optional[str] = None,
    connection_id: Optional[str] = None,
    event: Optional[List[str]] = None,
    include_raw: Optional[bool] = None,
    wait_for_new_events: bool = True,
) -> Generator[Event, None, None]:
    """
    Streams Continuous Data Capture (CDC) events in real-time by repeatedly fetching
    data from the API while handling pagination and retries.

    Args:
        - from_event_id (str): The starting event ID to begin streaming from.
        - limit (int, optional): Maximum number of results to retrieve per request.
        - company_id (str, optional): Company ID to filter results.
        - connection_id (str, optional): Connection ID to filter results.
        - event (List[str], optional): List of event types to filter results.
        - include_raw (bool, optional): Whether to include raw data in results.
        - wait_for_new_events (bool, optional): Flag to wait for new events when last event is reached, or terminate the generator.
            if True (default), generator indefinitely polls, waiting for new events.
            if False, generator terminates when "has_more" is false.

    Yields:
        Event: The next CDC event in the stream.
    """

    next_from_event_id = from_event_id
    while True:
        try:
            # Request the next page of data
            response = get(
                from_event_id=next_from_event_id,
                limit=limit,
                company_id=company_id,
                connection_id=connection_id,
                event=event,
                include_raw=include_raw,
            )
        except Exception as e:
            # On any exception, log it and wait 5 seconds
            print(f"Error while fetching CDC data: {e}")
            time.sleep(5)
            continue

        # If we received results, move the pagination forward
        if response["last_event_id"] is not None:
            next_from_event_id = response["last_event_id"]

        # Yield every retrieved event
        for event_result in response["result"]:
            yield event_result

        if response["has_more"]:
            # If there is more data, immediately make the next request
            continue
        else:
            if wait_for_new_events:
                # If there were no results, wait 5 seconds and poll again to see if there are new events available
                time.sleep(5)
                continue
            else:
                # We're not waiting for new events, so terminate the generator
                return
