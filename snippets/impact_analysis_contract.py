# Sample: the Pydantic input/output contract for the Impact Analysis agent.
# Every domain agent in FACIA exposes a typed contract like this one — agents
# communicate through durable database records, not direct calls, and every
# field here is deliberate (e.g. buffer_miles differs between the Live and
# Historical modes; gapfill_intensity backs off gracefully under API quota).

from pydantic import BaseModel, Field


class ImpactAnalysisInput(BaseModel):
    weather_event_id: str
    organization_id: str
    workflow_run_id: str
    # Live path: single primary footprint. Historical: optional when layer_ids set.
    event_footprint_id: str | None = None
    # Historical multi-layer direct intersection (null = use is_default_on).
    layer_ids: list[str] | None = None
    # Adjacent buffer. Live default 5 mi. Historical deep analysis uses 1 mi.
    # Set include_adjacent=False to skip adjacent entirely (gate remains direct-only).
    buffer_miles: float = Field(default=5.0, ge=0.1, le=50.0)
    include_adjacent: bool = True
    sample_raster_intensity: bool = True
    gapfill_intensity: bool = True
    promote_event_active: bool = True
    batch_size: int = Field(default=500, ge=1, le=2000)


class ImpactAnalysisOutput(BaseModel):
    weather_event_id: str
    direct_count: int
    adjacent_count: int
    total_count: int
    intensity_sampled: int = 0
    intensity_coverage: float = 0.0
    gapfill_filled: int = 0
    gapfill_warning: str | None = None
    agent_run_id: str
