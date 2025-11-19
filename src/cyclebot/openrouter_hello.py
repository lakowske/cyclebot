#!/usr/bin/env python3
"""OpenRouter API demonstration script.

This script demonstrates two uses of OpenRouter.ai:
1. Basic text prompt (tell me a joke)
2. Vision analysis of trading chart images

Configuration is read from .env file.
"""

import base64
import os
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv

from cyclebot.chart import get_chart_directory, get_latest_charts


def load_config() -> dict[str, Optional[str]]:
    """Load configuration from .env file.

    Returns:
        Dictionary with configuration values
    """
    load_dotenv()

    config = {
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "model": os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        "vision_model": os.getenv("OPENROUTER_VISION_MODEL", "meta-llama/llama-3.2-90b-vision-instruct:free"),
        "chart_base_dir": os.getenv("CHART_BASE_DIR"),
    }

    if not config["api_key"]:
        msg = "OPENROUTER_API_KEY not found in .env file"
        raise ValueError(msg)

    return config


def send_text_prompt(api_key: str, model: str, prompt: str) -> str:
    """Send a text prompt to OpenRouter.

    Args:
        api_key: OpenRouter API key
        model: Model to use (e.g., "anthropic/claude-3.5-sonnet")
        prompt: Text prompt to send

    Returns:
        Model's response text
    """
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    response = requests.post(url, headers=headers, json=data, timeout=30)
    response.raise_for_status()

    result: dict[str, Any] = response.json()
    return str(result["choices"][0]["message"]["content"])


def encode_image_base64(image_path: Path) -> str:
    """Encode an image file as base64 data URL.

    Args:
        image_path: Path to image file

    Returns:
        Base64 data URL (e.g., "data:image/png;base64,...")
    """
    with image_path.open("rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")

    # Determine MIME type from extension
    ext = image_path.suffix.lower()
    mime_type = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(
        ext.lstrip("."), "image/png"
    )

    return f"data:{mime_type};base64,{encoded}"


def send_vision_prompt(api_key: str, model: str, prompt: str, images: list[Path]) -> str:
    """Send a vision prompt with images to OpenRouter.

    Args:
        api_key: OpenRouter API key
        model: Vision-capable model to use
        prompt: Text prompt to send
        images: List of image file paths

    Returns:
        Model's response text
    """
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Build content array with text first, then images
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]

    for image_path in images:
        image_url = encode_image_base64(image_path)
        content.append({"type": "image_url", "image_url": {"url": image_url}})

    data = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
    }

    response = requests.post(url, headers=headers, json=data, timeout=60)
    response.raise_for_status()

    result: dict[str, Any] = response.json()
    return str(result["choices"][0]["message"]["content"])


def example_basic_joke(config: dict[str, Optional[str]]) -> None:
    """Example 1: Basic text prompt - tell me a joke."""
    print("=== Example 1: Basic Text Prompt ===\n")
    print(f"Using model: {config['model']}\n")

    prompt = "Tell me a programming joke."

    print(f"Prompt: {prompt}\n")
    api_key = config["api_key"]
    model = config["model"]
    if not api_key or not model:
        print("Error: Missing API key or model configuration")
        return
    response = send_text_prompt(api_key, model, prompt)
    print(f"Response:\n{response}\n")


def example_chart_analysis(config: dict[str, Optional[str]]) -> None:
    """Example 2: Vision analysis of trading charts."""
    print("=== Example 2: Chart Analysis with Vision ===\n")
    print(f"Using model: {config['vision_model']}\n")

    # Get chart directory
    chart_base_dir = config.get("chart_base_dir")
    chart_dir = get_chart_directory(chart_base_dir if chart_base_dir else None)
    print(f"Chart directory: {chart_dir}\n")

    # Get latest charts for all timeframes
    latest_charts = get_latest_charts(chart_dir)

    if not latest_charts:
        print("No charts found! Please run chart_capture.py first.")
        return

    print(f"Found {len(latest_charts)} charts:")
    for timeframe, path in latest_charts.items():
        print(f"  {timeframe}: {path.name}")
    print()

    # Prepare images list in order: 1h, 30m, 15m, 5m
    timeframes = ["1h", "30m", "15m", "5m"]
    images = [latest_charts[tf] for tf in timeframes if tf in latest_charts]

    if not images:
        print("No charts available for analysis.")
        return

    # Create prompt for chart analysis
    prompt = """Analyze these TradingView charts (in order: 1 hour, 30 minute, 15 minute, 5 minute timeframes).

Please provide:
1. Overall trend across all timeframes
2. Key support and resistance levels visible
3. Any notable patterns or formations
4. Short-term vs long-term trend alignment
5. Your assessment of current market condition

Be concise but specific."""

    print(f"Analyzing {len(images)} chart images...\n")
    api_key = config["api_key"]
    vision_model = config["vision_model"]
    if not api_key or not vision_model:
        print("Error: Missing API key or vision model configuration")
        return
    response = send_vision_prompt(api_key, vision_model, prompt, images)
    print(f"Analysis:\n{response}\n")


def main() -> None:
    """Run OpenRouter demonstration examples."""
    try:
        # Load configuration
        config = load_config()

        # Example 1: Basic joke prompt
        example_basic_joke(config)

        print("\n" + "=" * 70 + "\n")

        # Example 2: Chart analysis with vision
        example_chart_analysis(config)

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nPlease create a .env file based on .env.example")
        print("Get your API key from: https://openrouter.ai/keys")
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
