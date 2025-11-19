#!/usr/bin/env python3
"""Direct Playwright script to capture TradingView charts without LLM.

This script replicates the functionality of hello.py but uses Playwright directly
instead of going through the Claude Code SDK and MCP server.
"""

import asyncio
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import Page, async_playwright


async def capture_chart(page: Page, url: str, output_path: str, wait_time: int = 3000) -> None:
    """Navigate to a TradingView chart and capture a screenshot.

    Args:
        page: Playwright page object
        url: TradingView chart URL
        output_path: Path to save the screenshot
        wait_time: Time to wait for chart to load (milliseconds)
    """
    print(f"Navigating to {url}...")
    await page.goto(url)

    # Wait for chart to fully load
    print(f"Waiting {wait_time}ms for chart to load...")
    await page.wait_for_timeout(wait_time)

    # Take screenshot with high quality settings
    print(f"Capturing screenshot to {output_path}...")
    await page.screenshot(
        path=output_path,
        type="png",  # PNG format (lossless)
        full_page=False,  # Capture viewport only
    )
    print(f"✓ Saved {output_path}\n")


async def main() -> None:
    """Capture multiple TradingView charts using a persistent Chrome profile."""
    # Profile directory (same as used by hello.py)
    profile_dir = Path.home() / ".config" / "cyclebot" / "chrome-profile-tradingview"

    # Create timestamped directory structure: ~/mnt/pi-share/Trading/charts/{YEAR}/{Month}/{YYYY-MM-DD}/
    now = datetime.now(timezone.utc).astimezone()  # Get local time with timezone awareness
    base_dir = Path.home() / "mnt" / "pi-share" / "Trading" / "charts"
    year_dir = base_dir / str(now.year)
    month_dir = year_dir / now.strftime("%b")  # e.g., "Nov"
    date_dir = month_dir / now.strftime("%Y-%m-%d")  # e.g., "2025-11-19"

    # Create directory structure
    date_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamp for filenames
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")  # e.g., "2025-11-19_15-30-45"

    # Chart definitions: (URL, timeframe_suffix)
    charts = [
        ("https://www.tradingview.com/chart/obJz7jBz/", "1h"),
        ("https://www.tradingview.com/chart/gVH3aqxp/", "30m"),
        ("https://www.tradingview.com/chart/KXmakFlc/", "15m"),
        ("https://www.tradingview.com/chart/hCHhBALH/", "5m"),
    ]

    print("=== TradingView Chart Capture ===\n")
    print(f"Using Chrome profile: {profile_dir}")
    print(f"Output directory: {date_dir}")
    print(f"Timestamp: {timestamp}\n")

    async with async_playwright() as p:
        # Launch Chrome with persistent profile
        # Note: --password-store=basic is critical to avoid cookie encryption issues
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,  # Set to True for headless mode
            channel="chrome",  # Use Chrome instead of Chromium
            viewport={"width": 1920, "height": 1080},  # Full HD resolution
            args=[
                "--password-store=basic",  # Avoid keyring encryption issues on Linux
                "--no-sandbox",  # May be needed depending on environment
                "--window-size=1920,1080",  # Set window size to match viewport
            ],
        )

        # Get the first page (or create new one)
        page = browser.pages[0] if browser.pages else await browser.new_page()

        # Capture all charts using the same browser session
        for url, timeframe in charts:
            # Create filename: {timestamp}-{timeframe}.png
            filename = f"{timestamp}-{timeframe}.png"
            output_path = date_dir / filename
            await capture_chart(page, url, str(output_path))

        # Close browser
        await browser.close()

    print("All charts captured successfully!")


if __name__ == "__main__":
    asyncio.run(main())
