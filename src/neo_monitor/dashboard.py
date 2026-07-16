"""Streamlit browser interface for exploring NEO monitor results."""

from __future__ import annotations

from datetime import date
import logging
import os
from typing import Any, cast

import streamlit as st
from dotenv import load_dotenv

from neo_monitor.api import NasaApiError
from neo_monitor.logging_config import configure_logging
from neo_monitor.output import objects_csv_text, raw_json_text
from neo_monitor.summarize import NeoDataValidationError, NeoObject, SortBy
from neo_monitor.workflow import (
    MonitorRequest,
    MonitorResult,
    build_monitor_result,
    fetch_monitor_feed,
)


logger = logging.getLogger(__name__)
SORT_OPTIONS: tuple[SortBy, ...] = ("closest", "fastest", "largest")


def main() -> None:
    """Render the small browser interface without duplicating NEO logic."""

    st.set_page_config(page_title="NEO Explorer", page_icon="☄️", layout="wide")
    load_dotenv()
    configure_logging(verbose=True, log_file=None)

    st.title("Near-Earth Object Explorer")
    st.write(
        "Explore NASA close-approach data using the same validation and analysis "
        "workflow as the NEO command-line tool."
    )

    with st.form("neo-request"):
        dates, options = st.columns(2)
        with dates:
            start_date = _date_input("Start date", date.today())
            end_date = _date_input("End date", start_date)
        with options:
            hazardous_only = st.checkbox("Potentially hazardous objects only")
            sort_by = cast(
                SortBy,
                st.selectbox("Rank selected objects by", SORT_OPTIONS),
            )
            top = int(
                st.number_input(
                    "Maximum rows to show",
                    min_value=1,
                    max_value=50,
                    value=10,
                    step=1,
                )
            )
        submitted = st.form_submit_button("Load near-Earth object data")

    if submitted:
        _load_result(
            MonitorRequest(
                start_date=start_date,
                end_date=end_date,
                hazardous_only=hazardous_only,
                sort_by=sort_by,
                top=top,
            )
        )

    if "monitor_result" not in st.session_state:
        st.info("Choose a date range and select **Load near-Earth object data**.")
        return

    result = cast(MonitorResult, st.session_state["monitor_result"])
    request = cast(MonitorRequest, st.session_state["monitor_request"])
    _render_result(result, request)


def _date_input(label: str, value: date) -> date:
    """Return the single date selected by a Streamlit date input."""

    selected = st.date_input(label, value=value)
    if isinstance(selected, tuple):
        return cast(date, selected[0])
    return cast(date, selected)


def _load_result(request: MonitorRequest) -> None:
    """Fetch one feed and keep only a successful result in the browser session."""

    if request.end_date is not None and request.end_date < request.start_date:
        st.error("End date cannot be before start date.")
        return

    api_key = os.environ.get("NASA_API_KEY", "")
    if not api_key:
        st.error(
            "NASA_API_KEY is required. Add it to your environment or local .env file "
            "before loading data."
        )
        return

    try:
        with st.spinner("Requesting and validating NASA data..."):
            feed = fetch_monitor_feed(api_key, request)
            result = build_monitor_result(feed, request)
    except (NasaApiError, NeoDataValidationError, ValueError) as exc:
        logger.warning("Dashboard request could not be completed: %s", exc)
        st.error(str(exc))
        return

    st.session_state["monitor_result"] = result
    st.session_state["monitor_request"] = request


def _render_result(result: MonitorResult, request: MonitorRequest) -> None:
    """Display summary, visual comparisons, details, and explicit downloads."""

    st.subheader(f"Results for {result.label}")
    st.caption("Summary values describe the full requested feed before filters.")
    _render_summary(result)

    raw_download, selected_download = st.columns(2)
    file_stem = _file_stem(request)
    raw_download.download_button(
        "Download raw NASA JSON",
        data=raw_json_text(result.raw_feed),
        file_name=f"{file_stem}-raw.json",
        mime="application/json",
    )
    selected_download.download_button(
        "Download selected rows as CSV",
        data=objects_csv_text(result.selected_objects),
        file_name=f"{file_stem}-selected.csv",
        mime="text/csv",
    )

    if not result.selected_objects:
        st.warning("No near-Earth objects match the selected filters.")
        return

    rows = _object_rows(result.selected_objects)
    sort_by = request.sort_by or "closest"
    st.subheader("Compare the selected objects")
    st.caption(
        "Each point represents one object. Position shows miss distance and speed; "
        "size shows estimated diameter; color marks potentially hazardous objects."
    )
    st.vega_lite_chart(rows, _comparison_chart(), width="stretch")

    st.subheader(_ranked_view_title(sort_by))
    st.vega_lite_chart(rows, _ranked_chart(sort_by), width="stretch")

    st.subheader("Selected object details")
    st.dataframe(
        _table_rows(rows),
        width="stretch",
        hide_index=True,
        column_config={
            "approach_date": "Approach date",
            "name": "Object",
            "hazardous": "Potentially hazardous",
            "diameter_meters": st.column_config.NumberColumn(
                "Estimated diameter (m)", format="%.1f"
            ),
            "miss_distance_lunar": st.column_config.NumberColumn(
                "Miss distance (LD)", format="%.2f"
            ),
            "miss_distance_km": st.column_config.NumberColumn(
                "Miss distance (km)", format="%,.0f"
            ),
            "velocity_kph": st.column_config.NumberColumn(
                "Velocity (km/h)", format="%,.0f"
            ),
        },
    )


def _render_summary(result: MonitorResult) -> None:
    """Display the core unfiltered summary values."""

    total, hazardous, closest, fastest = st.columns(4)
    total.metric("Objects observed", result.summary.total_objects)
    hazardous.metric("Potentially hazardous", result.summary.hazardous_count)
    closest.metric(
        "Closest approach",
        _object_metric(result.summary.closest, "miss_distance_lunar", " LD"),
    )
    fastest.metric(
        "Fastest object",
        _object_metric(result.summary.fastest, "velocity_kph", " km/h"),
    )


def _object_metric(obj: NeoObject | None, field: str, suffix: str) -> str:
    """Format one optional summary object for a compact metric display."""

    if obj is None:
        return "None"
    value = getattr(obj, field)
    if field == "miss_distance_lunar":
        return f"{value:.2f}{suffix}"
    return f"{value:,.0f}{suffix}"


def _object_rows(objects: tuple[NeoObject, ...]) -> list[dict[str, Any]]:
    """Convert trusted project records into chart and table rows."""

    return [
        {
            "approach_date": obj.approach_date,
            "name": obj.name,
            "hazardous": "Yes" if obj.hazardous else "No",
            "diameter_meters": obj.diameter_meters,
            "miss_distance_lunar": obj.miss_distance_lunar,
            "miss_distance_km": obj.miss_distance_km,
            "velocity_kph": obj.velocity_kph,
        }
        for obj in objects
    ]


def _table_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Select the stable, readable columns for the browser table."""

    fields = (
        "approach_date",
        "name",
        "hazardous",
        "diameter_meters",
        "miss_distance_lunar",
        "miss_distance_km",
        "velocity_kph",
    )
    return [{field: row[field] for field in fields} for row in rows]


def _comparison_chart() -> dict[str, Any]:
    """Build the primary multi-variable NEO comparison visualization."""

    return {
        "mark": {"type": "circle", "opacity": 0.8},
        "encoding": {
            "x": {
                "field": "miss_distance_lunar",
                "type": "quantitative",
                "title": "Miss distance (lunar distances; lower is closer)",
            },
            "y": {
                "field": "velocity_kph",
                "type": "quantitative",
                "title": "Velocity (km/h)",
            },
            "size": {
                "field": "diameter_meters",
                "type": "quantitative",
                "title": "Estimated diameter (m)",
            },
            "color": {
                "field": "hazardous",
                "type": "nominal",
                "title": "Potentially hazardous",
                "scale": {"domain": ["No", "Yes"], "range": ["#4c78a8", "#d62728"]},
            },
            "tooltip": [
                {"field": "name", "type": "nominal", "title": "Object"},
                {
                    "field": "approach_date",
                    "type": "nominal",
                    "title": "Approach date",
                },
                {
                    "field": "hazardous",
                    "type": "nominal",
                    "title": "Potentially hazardous",
                },
                {
                    "field": "miss_distance_lunar",
                    "type": "quantitative",
                    "title": "Miss distance (LD)",
                    "format": ".2f",
                },
                {
                    "field": "velocity_kph",
                    "type": "quantitative",
                    "title": "Velocity (km/h)",
                    "format": ",.0f",
                },
                {
                    "field": "diameter_meters",
                    "type": "quantitative",
                    "title": "Estimated diameter (m)",
                    "format": ".1f",
                },
            ],
        },
    }


def _ranked_view_title(sort_by: SortBy) -> str:
    """Return the user-facing title for the selected ranking."""

    return {
        "closest": "Closest selected objects",
        "fastest": "Fastest selected objects",
        "largest": "Largest selected objects",
    }[sort_by]


def _ranked_chart(sort_by: SortBy) -> dict[str, Any]:
    """Build a secondary ranked view with an honest distance encoding."""

    metric, title = {
        "closest": ("miss_distance_lunar", "Miss distance (LD; lower is closer)"),
        "fastest": ("velocity_kph", "Velocity (km/h)"),
        "largest": ("diameter_meters", "Estimated diameter (m)"),
    }[sort_by]

    return {
        "mark": {"type": "circle", "size": 120}
        if sort_by == "closest"
        else {"type": "bar"},
        "encoding": {
            "x": {"field": metric, "type": "quantitative", "title": title},
            "y": {"field": "name", "type": "nominal", "sort": None, "title": None},
            "color": {
                "field": "hazardous",
                "type": "nominal",
                "legend": None,
                "scale": {"domain": ["No", "Yes"], "range": ["#4c78a8", "#d62728"]},
            },
            "tooltip": [
                {"field": "name", "type": "nominal", "title": "Object"},
                {
                    "field": metric,
                    "type": "quantitative",
                    "title": title,
                    "format": ",.2f",
                },
            ],
        },
    }


def _file_stem(request: MonitorRequest) -> str:
    """Create a stable, readable filename base for browser downloads."""

    end_date = request.end_date or request.start_date
    return f"neo-{request.start_date.isoformat()}-to-{end_date.isoformat()}"


if __name__ == "__main__":
    main()
