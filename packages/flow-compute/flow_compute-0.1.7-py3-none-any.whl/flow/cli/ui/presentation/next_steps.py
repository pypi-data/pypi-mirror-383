"""Helpers for building and rendering context-aware "Next steps" panels.

This module centralizes construction and presentation of follow-up
recommendations across CLI commands to ensure a consistent UX.

Design goals:
- Opinionated, minimal, context-aware suggestions
- One rendering style (panel) with muted border
- No command-specific knowledge beyond simple task state heuristics
"""

from collections.abc import Iterable

from rich.console import Console
from rich.panel import Panel

from flow.cli.utils.icons import prefix_with_flow_icon
from flow.cli.utils.theme_manager import theme_manager
from flow.sdk.models import Task


def _get_labels():
    """Late-bind nomenclature labels with a safe default.

    Avoids hard import dependency at module import time to prevent
    partial-install/import-order issues.
    """
    try:
        from flow.cli.ui.presentation.nomenclature import (
            get_entity_labels as _labels,
        )

        return _labels()
    except Exception:  # noqa: BLE001

        class _L:
            header = "Task"
            title_plural = "Tasks"
            empty_plural = "tasks"
            singular = "task"
            article = "a"

        return _L()


def _get_command_prefix() -> str:
    """Return the appropriate command prefix based on mode.

    Returns "flow instance" in compute mode, "flow" otherwise.
    """
    try:
        from flow.cli.ui.presentation.nomenclature import is_compute_mode

        return "flow instance" if is_compute_mode() else "flow"
    except Exception:  # noqa: BLE001
        return "flow"


def _get_create_command() -> str:
    """Return the appropriate create command based on mode.

    Returns "create" in compute mode, "run" otherwise.
    """
    try:
        from flow.cli.ui.presentation.nomenclature import is_compute_mode

        return "create" if is_compute_mode() else "run"
    except Exception:  # noqa: BLE001
        return "run"


def _get_list_command() -> str:
    """Return the appropriate list command based on mode.

    Returns "instance list" in compute mode, "status" otherwise.
    """
    try:
        from flow.cli.ui.presentation.nomenclature import is_compute_mode

        return "instance list" if is_compute_mode() else "status"
    except Exception:  # noqa: BLE001
        return "status"


def build_empty_state_next_steps(has_history: bool) -> list[str]:
    """Recommendations when there are no active tasks.

    Args:
        has_history: True if any tasks exist historically (even if not recent)

    Returns:
        A short, ordered list of next steps to present to the user.
    """

    steps: list[str] = []

    # Always offer the fastest path to success
    labels = _get_labels()
    noun = labels.empty_plural[:-1] if labels.empty_plural.endswith("s") else labels.empty_plural
    cmd_prefix = _get_command_prefix()
    create_cmd = _get_create_command()
    # Create a <noun> (quick)
    steps.append(
        f"[accent][bold]{cmd_prefix}[/bold][/accent] {create_cmd} -- 'nvidia-smi' [muted]— Create {labels.article} {noun} (quick)[/muted]"
    )
    steps.append(
        "[accent][bold]flow[/bold][/accent] template task -o task.yaml [muted]— Generate YAML template[/muted]"
    )

    # If they already have history, nudge discovery; otherwise nudge examples
    if has_history:
        list_cmd = _get_list_command()
        steps.append(
            f"[accent][bold]flow[/bold][/accent] {list_cmd} 1 [muted]— View {labels.empty_plural[:-1] if labels.empty_plural.endswith('s') else labels.empty_plural} details (by index)[/muted]"
        )
        noun_name = f"{labels.singular}-name"
        steps.append(
            f"[accent][bold]flow[/bold][/accent] {list_cmd} [task.name]<{noun_name}>[/task.name] [muted]— View {labels.empty_plural[:-1] if labels.empty_plural.endswith('s') else labels.empty_plural} details (by name)[/muted]"
        )
    else:
        steps.append("[accent][bold]flow[/bold][/accent] example [muted]— Explore starters[/muted]")

    return steps


def build_generic_recommendations(*, index_help: str, active_tasks: int) -> list[str]:
    """Generic recommendations to append beneath listings.

    Args:
        index_help: A human-friendly index range (e.g., "1" or "1-5")
        active_tasks: Number of active (running/pending) tasks displayed

    Returns:
        A list of recommendations suitable for a compact "Next steps" panel.
    """

    recs: list[str] = []
    # Drill-down affordance – useful in every state
    labels = _get_labels()
    noun = labels.empty_plural[:-1] if labels.empty_plural.endswith("s") else labels.empty_plural
    list_cmd = _get_list_command()
    recs.append(
        f"[accent][bold]flow[/bold][/accent] {list_cmd} {index_help} [muted]— View {noun} details (by index)[/muted]"
    )
    noun_name = f"{labels.singular}-name"
    recs.append(
        f"[accent][bold]flow[/bold][/accent] {list_cmd} [task.name]<{noun_name}>[/task.name] [muted]— View {labels.empty_plural[:-1] if labels.empty_plural.endswith('s') else labels.empty_plural} details (by name)[/muted]"
    )

    # If nothing is running, offer a one-liner to create work
    if active_tasks == 0:
        cmd_prefix = _get_command_prefix()
        create_cmd = _get_create_command()
        recs.insert(
            0,
            f"[accent][bold]{cmd_prefix}[/bold][/accent] {create_cmd} -- 'nvidia-smi' [muted]— Create {labels.article} {noun} (quick)[/muted]",
        )

    return recs


def _is_flow_origin(task: Task) -> bool:
    """Return True if a task is from Flow CLI origin.

    Falls back to False when metadata is unavailable.
    """
    try:
        meta = getattr(task, "provider_metadata", {}) or {}
        return meta.get("origin") == "flow-cli"
    except Exception:  # noqa: BLE001
        return False


def _status_value(task: Task) -> str:
    """Return task status value resiliently (handles enums/mocks)."""
    try:
        status = getattr(task, "status", None)
        return getattr(status, "value", str(status))
    except Exception:  # noqa: BLE001
        return ""


def build_status_recommendations(
    tasks: Iterable[Task],
    *,
    max_count: int,
    index_example_single: str,
    index_example_multi: str,
) -> list[str]:
    """Build context-aware recommendations for the status view.

    Args:
        tasks: Tasks displayed to the user (already ordered as shown).
        max_count: Maximum number of recommendations to return.
        index_example_single: Index shortcut example for a single selection (e.g., "1").
        index_example_multi: Index shortcut example for multi/range (e.g., "1-3" or "1-3,5").

    Returns:
        A list of concise recommendation strings (top-N by priority).
    """

    task_list = list(tasks)

    # Use display status when possible so we can differentiate "starting"
    try:
        from flow.cli.ui.presentation.task_formatter import TaskFormatter as _TF

        def _display_status(t: Task) -> str:
            try:
                return str(_TF.get_display_status(t)).lower()
            except Exception:  # noqa: BLE001
                return _status_value(t)

    except Exception:  # graceful fallback  # noqa: BLE001

        def _display_status(t: Task) -> str:
            return _status_value(t)

    has_running = any(_display_status(t) == "running" for t in task_list)
    # Treat both pending and starting as not-ready
    has_pending = any(_display_status(t) in ("pending", "starting") for t in task_list)
    has_active = has_running or has_pending
    has_flow_running = any(_is_flow_origin(t) and _status_value(t) == "running" for t in task_list)

    recs: list[str] = []

    # If anything is pending/starting, lead with readiness-first guidance
    labels = _get_labels()
    noun_lower = labels.singular
    noun_name = f"{noun_lower}-name"
    list_cmd = _get_list_command()
    if has_pending:
        recs.append(
            f"[accent][bold]flow[/bold][/accent] {list_cmd} {index_example_single} [muted]— View {noun_lower} details (readiness)[/muted]"
        )
        recs.append(
            f"[accent][bold]flow[/bold][/accent] logs {index_example_single} -f [muted]— Follow startup logs[/muted]"
        )

    # State-aware, highest value next
    if has_flow_running:
        recs.append(
            f"[accent][bold]flow[/bold][/accent] ssh {index_example_single} [muted]— SSH into {noun_lower} (by index)[/muted]"
        )
        recs.append(
            f"[accent][bold]flow[/bold][/accent] ssh [task.name]<{noun_name}>[/task.name] [muted]— SSH into {noun_lower} (by name)[/muted]"
        )
        recs.append(
            f"[accent][bold]flow[/bold][/accent] logs {index_example_single} [muted]— View logs (by index)[/muted]"
        )
        recs.append(
            f"[accent][bold]flow[/bold][/accent] logs [task.name]<{noun_name}>[/task.name] [muted]— View logs (by name)[/muted]"
        )

    if has_active:
        recs.append(
            f"[accent][bold]flow[/bold][/accent] cancel {index_example_multi} [muted]— Cancel {labels.empty_plural} by range[/muted]"
        )
        recs.append(
            f"[accent][bold]flow[/bold][/accent] {list_cmd} --watch [muted]— Watch updates[/muted]"
        )

    # Always include a creation path, but keep list short
    recs.append(
        "[accent][bold]flow[/bold][/accent] template task -o task.yaml [muted]— Generate YAML template[/muted]"
    )

    # When no active tasks, pivot to getting-started paths
    if not has_active:
        recs.append(
            "[accent][bold]flow[/bold][/accent] dev [muted]— Start development environment[/muted]"
        )
        recs.append("[accent][bold]flow[/bold][/accent] example [muted]— Explore starters[/muted]")

    # Deduplicate while preserving order
    deduped: list[str] = []
    seen = set()
    for r in recs:
        if r not in seen:
            deduped.append(r)
            seen.add(r)

    return deduped[: max(0, int(max_count))]


def render_next_steps_panel(
    console: Console,
    recommendations: Iterable[str],
    *,
    title: str = "Next Steps",
    max_items: int = 3,
) -> None:
    """Render a compact panel listing recommendations.

    Args:
        console: Rich console to render into.
        recommendations: Lines to display; each will be bullet-prefixed.
        title: Panel title (plain text; styling handled internally).
    """
    # Width-aware formatting: prefer em-dash on wider terminals; fall back to colon on narrow
    try:
        width = getattr(console, "width", None) or getattr(console, "size", None).width  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        width = 80

    bullet_char = "•" if width >= 60 else "-"

    def _compact_desc(text: str) -> str:
        if width < 80:
            # Replace the leading em-dash in muted description with a colon to save width
            return text.replace("[muted]—", "[muted]:")
        return text

    # Enforce a concise set of top actions
    recs = [str(r).strip() for r in recommendations if str(r).strip()]
    if max_items and max_items > 0:
        recs = recs[:max_items]

    lines = [f"  [muted]{bullet_char}[/muted] {_compact_desc(r)}" for r in recs]
    body = "\n".join(lines)
    # Prefix the panel title with the Flow icon to match overall CLI branding
    branded_title = prefix_with_flow_icon(title)
    panel = Panel(
        body,
        title=f"[accent][bold]{branded_title}[/bold][/accent]",
        border_style=theme_manager.get_color("table.border"),
        padding=(1, 2),
        expand=False,
    )
    console.print("\n")
    console.print(panel)
