from __future__ import annotations

from datetime import datetime
from typing import List, Tuple

from pydantic import BaseModel, Field


class TelemetryV1(BaseModel):
    device_id: str
    timestamp: datetime
    lat: float
    lon: float


class TripV1(BaseModel):
    trip_id: str
    vehicle_id: str
    start_time: datetime
    end_time: datetime | None = None
    route: List[Tuple[float, float]] = Field(default_factory=list)
