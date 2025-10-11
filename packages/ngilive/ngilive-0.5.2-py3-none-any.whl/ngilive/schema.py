from datetime import datetime

from pydantic import AwareDatetime, BaseModel, Field


class EventResponse(BaseModel):
    event_id: str
    time_from: AwareDatetime
    time_to: AwareDatetime | None = None
    type: str
    tags: list[str] | None = None


class CoordinateSystem(BaseModel):
    authority: str
    srid: str | int | None = None


class SensorLocation(BaseModel):
    north: float | None = None
    east: float | None = None
    mash: float | None = None
    coordinateSystem: CoordinateSystem | None = None


class SensorMeta(BaseModel):
    name: str | None = None
    unit: str | None = None
    logger: str | None = None
    type: str
    pos: SensorLocation


class LoggerMeta(BaseModel):
    id: int
    name: str


class SensorMetaResponse(BaseModel):
    sensors: list[SensorMeta]


class LoggerMetaResponse(BaseModel):
    loggers: list[LoggerMeta]


class SensorName(BaseModel):
    name: str


class Datapoint(BaseModel):
    timestamp: AwareDatetime
    value: float


class JsonData(BaseModel):
    sensor: SensorName
    data: list[Datapoint]


class JsonDataResponse(BaseModel):
    # {
    #   "data": [
    #     {
    #       "sensor": {
    #         "name": "string"
    #       },
    #       "data": [
    #         {
    #           "timestamp": "2025-10-04T15:26:34.172Z",
    #           "value": 0
    #         }
    #       ]
    #     }
    #   ]
    # }

    data: list[JsonData]


class Event(BaseModel):
    device_id: str
    event_id: str
    time_from: datetime
    time_to: datetime | None
    type: str


class EventWithTags(Event):
    tags: list[str]


class EventMetadata(BaseModel):
    logger_id: int
    logger_name: str
    project_id: int


class EventFile(BaseModel):
    name: str
    last_modified: datetime
    size: int


class EventFiles(BaseModel):
    event: EventWithTags
    metadata: EventMetadata
    files: list[EventFile] = Field(default_factory=lambda: [])
