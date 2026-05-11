from pydantic import BaseModel, Field
from datetime import datetime

class SatelliteReportRequest(BaseModel):
    satellite_name: str = Field(..., min_length=2, max_length=100,
        examples=['ISS', 'Hubble Space Telescope', 'JWST', 'Sentinel-3B'])
    include_news: bool = Field(True, description='Include recent news search')

class SatelliteReportResponse(BaseModel):
    satellite_name: str
    report:         str
    steps_taken:    int
    latency_ms:     float
    timestamp:      datetime = Field(default_factory=datetime.utcnow)
