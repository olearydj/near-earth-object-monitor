from __future__ import annotations

from collections.abc import Sequence

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from neo_monitor.summarize import NeoObject, NeoSummary


def print_rich_summary(console: Console, summary: NeoSummary, label: str) -> None:
    """Print a readable Rich summary panel."""

    lines = [
        f"Date range: {label}",
        f"Objects observed: {summary.total_objects}",
        f"Potentially hazardous: {summary.hazardous_count}",
    ]

    if summary.closest is not None:
        lines.append(
            "Closest approach: "
            f"{summary.closest.name} "
            f"({summary.closest.miss_distance_lunar:.2f} lunar distances, "
            f"{summary.closest.miss_distance_km:,.0f} km)"
        )

    if summary.fastest is not None:
        lines.append(
            "Fastest object: "
            f"{summary.fastest.name} "
            f"({summary.fastest.velocity_kph:,.0f} km/h)"
        )

    if summary.largest is not None:
        lines.append(
            "Largest estimated diameter: "
            f"{summary.largest.name} "
            f"({summary.largest.diameter_meters:.0f} m)"
        )

    console.print(Panel("\n".join(lines), title="Near-Earth Object Summary"))


def print_rich_object_listing(console: Console, objects: Sequence[NeoObject]) -> None:
    """Print a readable Rich table of extracted objects."""

    if not objects:
        console.print("[yellow]No near-earth objects matched.[/yellow]")
        return

    table = Table(title="Near-Earth Object Listing")
    table.add_column("Date")
    table.add_column("Name")
    table.add_column("Hazardous")
    table.add_column("Diameter (m)", justify="right")
    table.add_column("Miss (LD)", justify="right")
    table.add_column("Velocity (km/h)", justify="right")

    for obj in objects:
        table.add_row(
            obj.approach_date,
            obj.name,
            "yes" if obj.hazardous else "no",
            f"{obj.diameter_meters:.0f}",
            f"{obj.miss_distance_lunar:.2f}",
            f"{obj.velocity_kph:.0f}",
            style="bold red" if obj.hazardous else None,
        )

    console.print(table)
