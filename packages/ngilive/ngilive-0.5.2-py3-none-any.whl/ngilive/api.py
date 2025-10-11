import logging
from datetime import datetime
from io import BytesIO
from typing import Any, ParamSpec
from uuid import UUID


from ngilive.auth import Auth, AuthorizationCode
from ngilive.config import BASE_URL
from ngilive.httpx_wrapper import HTTPXWrapper
from ngilive.log import default_handler
from ngilive.schema import (
    EventFiles,
    EventResponse,
    JsonDataResponse,
    LoggerMetaResponse,
    SensorMetaResponse,
)


P = ParamSpec("P")


class NGILive:
    def __init__(
        self,
        base_url: str = BASE_URL,
        loglevel: str = "INFO",
        auth: Auth | None = None,
    ) -> None:
        """
        Creates a client for the API, which can later be used make more requests.

        This is a thin wrapper with python bindings for our
        <a href="https://api.ngilive.no" target="_blank">HTTP Web API</a>,
        which simplifies usage of the API from Python.

        Example:
        ```python
        from ngilive import NGILive

        nl = NGILive()

        sensors = nl.sensor_search(project=20200001, name="S1")

        ```
        """
        self._logger = logging.getLogger("ngilive.api")
        self._logger.setLevel(loglevel)
        if not self._logger.handlers:
            self._logger.addHandler(default_handler())

        self._base = base_url
        self._logger.debug(f"Initialized api with base url {base_url}")

        if auth is not None:
            self._logger.debug(f"Using user specified auth provider {type(auth)}")
            self._auth = auth
        else:
            self._auth = AuthorizationCode(loglevel=loglevel)
            self._logger.debug(f"Using default Auth provider {type(self._auth)}")

        self._httpx = HTTPXWrapper(loglevel)

    def _get_token(self) -> str:
        return self._auth.get_token()

    def logger_search(
        self,
        project_number: int,
        names: str | list[str] | None = None,
    ) -> LoggerMetaResponse:
        """
        Retrieve loggers within a project.

        **Parameters:**
        - `project` (`int`): Project number.
        - `names` (`str | list[str] | None`, optional):
          Filter the response by logger name.
        """
        params: dict[str, Any] = {**_filter_null_to_dict(names=names)}

        res = self._httpx.get(
            f"{self._base}/projects/{project_number}/logger",
            params=params,
            headers={"Authorization": f"Bearer {self._get_token()}"},
        )
        res.raise_for_status()

        return LoggerMetaResponse.model_validate(res.json())

    def sensor_search(
        self,
        project: int,
        name: str | list[str] | None = None,
        type: str | list[str] | None = None,
        unit: str | list[str] | None = None,
        logger: str | list[str] | None = None,
    ) -> SensorMetaResponse:
        """
        Retrieve sensors within a project.

        This endpoint returns the sensors configured for a given project.
        The response can be filtered by sensor name, type, unit, or logger.
        Note that the same sensor may exist in multiple loggers.

        **Parameters:**
        - `project` (`int`): Project number.
        - `name` (`str | list[str] | None`, optional):
          Filter by sensor name. Note that the same sensor may exist in multiple loggers.
        - `type` (`str | list[str] | None`, optional):
          Filter by sensor type (e.g., `"Infiltrasjonstrykk"`).
        - `unit` (`str | list[str] | None`, optional):
          Filter by configured sensor unit (e.g., `"mm"`, `"kPa"`).
        - `logger` (`str | list[str] | None`, optional):
          Filter by logger name.
        """
        res = self._httpx.get(
            f"{self._base}/projects/{project}/sensors",
            params={
                **_filter_null_to_dict(
                    name=name,
                    type=type,
                    unit=unit,
                    logger=logger,
                ),
            },
            headers={"Authorization": f"Bearer {self._get_token()}"},
        )
        res.raise_for_status()

        return SensorMetaResponse.model_validate(res.json())

    def datapoint_search(
        self,
        project_number: int,
        start: datetime,
        end: datetime,
        offset: int | None = None,
        limit: int | None = None,
        name: str | list[str] | None = None,
        type: str | list[str] | None = None,
        unit: str | list[str] | None = None,
        logger: str | list[str] | None = None,
    ) -> JsonDataResponse:
        """
        Retrieve datapoints within a project.

        This endpoint returns datapoints for a given project within the specified time interval.
        Results can be paginated using `offset` and `limit`, and filtered by sensor attributes such as name, type, unit, or logger.

        **Parameters:**
        - `project_number` (`int`): Project number.
        - `start` (`datetime`): Start time of the datapoints time series.
        - `end` (`datetime`): End time of the datapoints time series.
        - `offset` (`int | None`, optional):
          Number of points to skip before returning data.
          Used in conjunction with `limit` for pagination.
          Example: `offset=5000&limit=2000` returns points 5000–7000.
        - `limit` (`int | None`, optional):
          Number of points to return in the query.
          Used in conjunction with `offset` for pagination.
          Example: `offset=5000&limit=2000` returns points 5000–7000.
        - `name` (`str | list[str] | None`, optional):
          Filter by sensor name. Note that the same sensor might exist in multiple loggers.
        - `type` (`str | list[str] | None`, optional):
          Filter by sensor type, for example `"Infiltrasjonstrykk"`.
        - `unit` (`str | list[str] | None`, optional):
          Filter by configured sensor unit, for example `"mm"` or `"kPa"`.
        - `logger` (`str | list[str] | None`, optional):
          Filter by logger name.
        """
        res = self._httpx.get(
            f"{self._base}/projects/{project_number}/datapoints/json_array_v0",
            params={
                "start": start.isoformat(),
                "end": end.isoformat(),
                **_filter_null_to_dict(
                    offset=offset,
                    limit=limit,
                    name=name,
                    type=type,
                    unit=unit,
                    logger=logger,
                ),
            },
            headers={"Authorization": f"Bearer {self._get_token()}"},
        )
        res.raise_for_status()

        return JsonDataResponse.model_validate(res.json())

    def events_for_logger(
        self,
        logger_id: int,
        offset: int = 0,
        limit: int = 100,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
        tags: list[str] | None = None,
        include_tags: bool = False,
    ) -> list[EventResponse]:
        """
        Retrieve events associated with a specific logger.

        This endpoint returns a list of events for the specified logger.
        Events can be filtered by time range, tags, and pagination parameters.

        **Parameters:**
        - `logger_id` (`int`): The unique identifier of the logger.
        - `offset` (`int`, optional):
          Number of events to skip before returning results. Used for pagination. Defaults to `0`.
        - `limit` (`int`, optional):
          Maximum number of events to return. Defaults to `100`.
        - `time_from` (`datetime | None`, optional):
          Start of the time range filter. Only events occurring after this time are returned.
        - `time_to` (`datetime | None`, optional):
          End of the time range filter. Only events occurring before this time are returned.
        - `tags` (`list[str] | None`, optional):
          Filter events by one or more tags.
        - `include_tags` (`bool`, optional):
          Whether to include the tags for each event in the response. Defaults to `False`.
        """
        res = self._httpx.get(
            f"{self._base}/logger/{logger_id}/events",
            params={
                "offset": offset,
                "limit": limit,
                **_filter_null_to_dict(
                    time_from=time_from,
                    time_to=time_to,
                    tags=tags,
                    include_tags=include_tags,
                ),
            },
            headers={"Authorization": f"Bearer {self._get_token()}"},
        )
        res.raise_for_status()

        return [EventResponse.model_validate(e) for e in res.json()]

    def event_from_id(self, event_id: UUID) -> EventResponse:
        """
        Get a single event from its unique identifier.
        """
        res = self._httpx.get(
            f"{self._base}/event/{event_id}",
            headers={"Authorization": f"Bearer {self._get_token()}"},
        )
        res.raise_for_status()

        return EventResponse.model_validate(res.json())

    def event_list_files(self, event_id: str) -> EventFiles:
        """
        Returns only Metadata about the files of the event.
        To actually download a file, use `event_file` instead.
        """
        res = self._httpx.get(
            f"{self._base}/event/{event_id}/files",
            headers={"Authorization": f"Bearer {self._get_token()}"},
        )
        res.raise_for_status()

        return EventFiles.model_validate(res.json())

    def event_file(self, event_id: str, file_name: str) -> BytesIO:
        """
        Download a file associated with a given event and return it as a file-like object.

        **Arguments:**
        - `event_id` (`str`): The unique identifier of the event.
        - `file_name` (`str`): The name of the file to download.

        **Returns:**
        - `BytesIO`: A file-like object containing the file's contents.

        **Example:**
        ```python
        file = client.event_file("abc123", "report.csv")
        with open("report.csv", "wb") as f:
            f.write(file_obj.read())
        ```
        """
        res = self._httpx.get(
            f"{self._base}/event/{event_id}/download/{file_name}",
            headers={"Authorization": f"Bearer {self._get_token()}"},
        )
        res.raise_for_status()
        download_link = res.json()["link"]
        assert isinstance(download_link, str)

        response = self._httpx.get(download_link)

        return BytesIO(response.content)


def _filter_null_to_dict(**kwargs) -> dict[str, Any]:
    """Return a dict excluding None values."""
    return {k: v for k, v in kwargs.items() if v is not None}
