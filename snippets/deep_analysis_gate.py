# Sample: per-event Deep Analysis eligibility gating.
# Illustrates a real product decision enforced in the backend (not just the
# UI): eligibility is a per-EVENT flag rather than a blanket per-hazard rule,
# because within the same hazard a warning-only tornado candidate is
# ineligible while a confirmed one (backed by an SPC storm report) is
# eligible. Flood stays permanently ineligible because a warning zone is a
# coarse alert polygon, not a measured inundation extent.

# Auto-gate: direct intersection count must be >= 100 unless force=true.
# Adjacent buffer defaults to 1 mile (historical detail); does not affect the gate.

source_summary = event_row.get("source_summary") or {}
if source_summary.get("deep_analysis_eligible", True) is False:
    if event_row.get("hazard") == "flood":
        message = (
            "Deep Analysis isn't available for flood — the warning zone is a "
            "coarse alert polygon, not a measured inundation extent."
        )
    else:
        message = (
            "Deep Analysis isn't available yet — this is a warning-only tornado "
            "candidate, not yet confirmed by an SPC storm report."
        )
    raise HTTPException(
        status_code=422,
        detail=make_error(
            "DEEP_ANALYSIS_NOT_SUPPORTED", message, retryable=False
        ).model_dump(),
    )
