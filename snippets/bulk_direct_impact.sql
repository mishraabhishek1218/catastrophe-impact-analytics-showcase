-- Sample: bulk PostGIS intersection check backing the "events with portfolio
-- impact" catalog filter.
--
-- weather_events.affected_policy_count is NOT a reliable "has impact" signal
-- -- it stays 0 until the Impact Analysis agent has actually run for that
-- event (gated behind the >=100-direct Deep Analysis threshold), so a
-- genuinely-impactful event that hasn't been analyzed yet would show 0. The
-- reliable, always-accurate signal is a live PostGIS intersection check.
--
-- This is the bulk variant: computes "has direct impact" for an entire page
-- of catalog events in one round trip instead of one HTTP call per event.

create or replace function bulk_event_has_direct_impact(
    p_org_id uuid,
    p_event_ids uuid[]
)
returns table (event_id uuid, has_direct_impact boolean)
language sql
stable
as $$
    select
        e.id,
        coalesce(
            g.geom is not null and exists (
                select 1
                from policies p
                where p.organization_id = p_org_id
                  and p.status = 'active'
                  and p.location is not null
                  and coalesce(p.geocode_confidence, 0) >= 0.80
                  and p.location && g.geom
                  and ST_Intersects(p.location, g.geom)
            ),
            false
        )
    from unnest(p_event_ids) as e(id)
    left join lateral (
        select resolve_event_layer_geom(e.id, p_org_id, null) as geom
    ) g on true;
$$;
