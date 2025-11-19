"""Common chart directory and naming utilities.

This module provides shared functionality for chart capture and organization
across multiple scripts (chart_capture.py, openrouter_hello.py, etc.).
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union


def get_chart_directory(base_path: Optional[Union[str, Path]] = None) -> Path:
    """Get the timestamped chart directory for the current date.

    Creates directory structure: {base_path}/{YEAR}/{Month}/{YYYY-MM-DD}/

    Args:
        base_path: Base directory for charts. Defaults to ~/mnt/pi-share/Trading/charts

    Returns:
        Path object for today's chart directory
    """
    base_path = Path.home() / "mnt" / "pi-share" / "Trading" / "charts" if base_path is None else Path(base_path)

    now = datetime.now(timezone.utc).astimezone()
    year_dir = base_path / str(now.year)
    month_dir = year_dir / now.strftime("%b")  # e.g., "Nov"
    date_dir = month_dir / now.strftime("%Y-%m-%d")  # e.g., "2025-11-19"

    # Create directory if it doesn't exist
    date_dir.mkdir(parents=True, exist_ok=True)

    return date_dir


def get_chart_timestamp() -> str:
    """Get a timestamp string for chart filenames.

    Returns:
        Timestamp in format: YYYY-MM-DD_HH-MM-SS (e.g., "2025-11-19_15-30-45")
    """
    now = datetime.now(timezone.utc).astimezone()
    return now.strftime("%Y-%m-%d_%H-%M-%S")


def get_chart_filename(timeframe: str, timestamp: Optional[str] = None) -> str:
    """Generate a chart filename.

    Args:
        timeframe: Chart timeframe (e.g., "1h", "30m", "15m", "5m")
        timestamp: Optional timestamp. If None, generates current timestamp.

    Returns:
        Filename in format: {timestamp}-{timeframe}.png
    """
    if timestamp is None:
        timestamp = get_chart_timestamp()
    return f"{timestamp}-{timeframe}.png"


def get_latest_charts(chart_dir: Optional[Path] = None, timeframes: Optional[list[str]] = None) -> dict[str, Path]:
    """Get the most recent chart files for specified timeframes.

    Args:
        chart_dir: Directory to search. Defaults to today's chart directory.
        timeframes: List of timeframes to find (e.g., ["1h", "30m"]). Defaults to all timeframes.

    Returns:
        Dictionary mapping timeframe to Path of most recent chart file.
        Example: {"1h": Path(".../2025-11-19_15-30-45-1h.png"), ...}
    """
    if chart_dir is None:
        chart_dir = get_chart_directory()

    if timeframes is None:
        timeframes = ["1h", "30m", "15m", "5m"]

    result = {}
    for timeframe in timeframes:
        # Find all files matching pattern *-{timeframe}.png
        matching_files = sorted(chart_dir.glob(f"*-{timeframe}.png"), reverse=True)
        if matching_files:
            result[timeframe] = matching_files[0]  # Most recent

    return result
