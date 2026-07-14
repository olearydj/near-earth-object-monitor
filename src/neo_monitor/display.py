from __future__ import annotations

from collections.abc import Sequence

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from neo_monitor.summarize import NeoObject, NeoSummary, SortBy


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


def print_rich_bar_chart(
    console: Console, objects: Sequence[NeoObject], sort_by: SortBy
) -> None:
    """Print a ranked, scaled chart while preserving exact object values."""

    if not objects:
        console.print("[yellow]No near-earth objects matched.[/yellow]")
        return

    title, metric_label, note, values, value_labels, color = _chart_details(
        objects, sort_by
    )
    maximum = max(values) or 1
    table = Table(
        box=box.SIMPLE_HEAVY,
        expand=True,
        show_header=True,
        header_style="bold bright_cyan",
        row_styles=["", "dim"],
    )
    table.add_column("Rank", justify="right", style="bright_cyan", width=5)
    table.add_column("Object", ratio=3)
    table.add_column(metric_label, justify="right", width=14)
    table.add_column("Comparison", ratio=4)

    for rank, (obj, value, value_label) in enumerate(
        zip(objects, values, value_labels, strict=True), start=1
    ):
        name = Text(obj.name, style="bold red" if obj.hazardous else "bold white")
        if obj.hazardous:
            name.append("  HAZARDOUS", style="bold red")
        table.add_row(
            str(rank),
            name,
            value_label,
            ProgressBar(
                total=maximum,
                completed=value,
                width=28,
                complete_style=color,
                finished_style=color,
            ),
        )

    caption = Text(note, style="dim")
    console.print(
        Panel(
            Group(table, caption),
            title=f"[bold]{title}[/bold]",
            border_style=color,
            padding=(1, 2),
        )
    )


def _chart_details(
    objects: Sequence[NeoObject], sort_by: SortBy
) -> tuple[str, str, str, list[float], list[str], str]:
    """Return labels and values for one ranked bar-chart view."""

    if sort_by == "closest":
        values = [obj.miss_distance_lunar for obj in objects]
        return (
            "Closest Approaches",
            "Miss (LD)",
            "Lower distance means a closer approach. Bars are scaled to this list.",
            values,
            [f"{value:.2f} LD" for value in values],
            "bright_cyan",
        )
    if sort_by == "fastest":
        values = [obj.velocity_kph for obj in objects]
        return (
            "Fastest Objects",
            "Speed",
            "Bars are scaled to the fastest object in this list.",
            values,
            [f"{value:,.0f} km/h" for value in values],
            "bright_yellow",
        )

    values = [obj.diameter_meters for obj in objects]
    return (
        "Largest Estimated Objects",
        "Diameter",
        "Bars are scaled to the largest object in this list.",
        values,
        [f"{value:,.0f} m" for value in values],
        "bright_magenta",
    )
