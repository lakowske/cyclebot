# OpenRouter.ai API Documentation

## Table of Contents

1. [Overview](#overview)
1. [Authentication](#authentication)
1. [API Endpoints](#api-endpoints)
1. [Sending Text Prompts](#sending-text-prompts)
1. [Sending Images (Vision)](#sending-images-vision)
1. [Model Selection](#model-selection)
1. [Request/Response Format](#requestresponse-format)
1. [Rate Limits](#rate-limits)
1. [Pricing](#pricing)
1. [Python Code Examples](#python-code-examples)

______________________________________________________________________

## Overview

OpenRouter is a unified API gateway that provides access to 300+ AI models from 60+ providers through a single API endpoint. It's OpenAI SDK-compatible and supports multimodal inputs including text, images, PDFs, audio, and video.

**Base URL:** `https://openrouter.ai/api/v1`

**Key Features:**

- OpenAI SDK compatibility
- Auto-routing and fallback support
- No markup on provider pricing
- Unified response format across all models
- Support for streaming responses
- Multimodal capabilities (vision, audio, etc.)

______________________________________________________________________

## Authentication

### Getting an API Key

1. Visit https://openrouter.ai/keys to create an API key
1. Assign a name to your key
1. Optionally set a credit limit for cost management

### Using the API Key

Include your API key in the Authorization header as a Bearer token:

```
Authorization: Bearer <OPENROUTER_API_KEY>
```

### Security Best Practices

**Critical:** Never commit API keys to public repositories. OpenRouter partners with GitHub for secret scanning and will notify you by email if your key is exposed.

Best practices:

- Store API keys in environment variables
- Keep keys out of version control
- Monitor for exposure notifications
- Immediately delete and replace compromised keys at https://openrouter.ai/settings/keys

______________________________________________________________________

## API Endpoints

### Main Endpoints

| Endpoint                                   | Method | Description                                     |
| ------------------------------------------ | ------ | ----------------------------------------------- |
| `/api/v1/chat/completions`                 | POST   | Chat completions (primary endpoint)             |
| `/api/v1/completions`                      | POST   | Text completions                                |
| `/api/v1/models`                           | GET    | List all available models                       |
| `/api/v1/generation?id={id}`               | GET    | Get generation details with native token counts |
| `/api/v1/key`                              | GET    | Get current API key info and usage stats        |
| `/api/v1/credits`                          | GET    | Get credit balance                              |
| `/api/v1/models/{author}/{slug}/endpoints` | GET    | List endpoints for specific model               |

### Optional Headers

For improved visibility on OpenRouter leaderboards:

```
HTTP-Referer: https://your-site.com
X-Title: Your App Name
```

______________________________________________________________________

## Sending Text Prompts

### Basic Text Request

**Endpoint:** `POST https://openrouter.ai/api/v1/chat/completions`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer <OPENROUTER_API_KEY>
```

**Request Body:**

```json
{
  "model": "openai/gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": "Hello! How are you?"
    }
  ]
}
```

**Response:**

```json
{
  "id": "gen-abc123",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "I'm doing well, thank you for asking!"
      },
      "finish_reason": "stop"
    }
  ],
  "created": 1700000000,
  "model": "openai/gpt-4o",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```

______________________________________________________________________

## Sending Images (Vision)

### Image Format Support

OpenRouter supports multimodal requests through the `/api/v1/chat/completions` endpoint.

**Supported MIME Types:**

- `image/png`
- `image/jpeg`
- `image/webp`
- `image/gif`

**Two Ways to Send Images:**

1. **Direct URLs** - Better for publicly accessible images (no encoding overhead)
1. **Base64 Encoding** - Required for local files or private images

### Image URL Format

```json
{
  "model": "openai/gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What's in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "https://example.com/image.jpg"
          }
        }
      ]
    }
  ]
}
```

### Base64 Encoded Image Format

```json
{
  "model": "openai/gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What's in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
          }
        }
      ]
    }
  ]
}
```

### Best Practices for Images

- **Ordering:** Send text prompt first, then images. If images must come first, place them in the system prompt.
- **Multiple Images:** Can send multiple images in separate content array entries (limits vary by model/provider)
- **Data URI Format:** `data:{mime_type};base64,{encoded_image}`

### Popular Vision Models

- `openai/gpt-4o` (supports vision)
- `openai/gpt-4-vision-preview`
- `meta-llama/llama-3.2-90b-vision-instruct`
- `meta-llama/llama-3.2-11b-vision-instruct`
- `01-ai/yi-vision`
- `google/gemini-2.5-pro-preview` (supports vision)

______________________________________________________________________

## Model Selection

### Model Naming Convention

Models use the format: `{provider}/{model-name}`

Examples:

- `openai/gpt-4o`
- `anthropic/claude-3.5-sonnet`
- `google/gemini-2.5-pro-preview`
- `meta-llama/llama-3.2-90b-vision-instruct`

### Free Models

Free models have IDs ending in `:free`:

- `google/gemini-flash-1.5:free`
- `meta-llama/llama-3.1-8b-instruct:free`

### Listing Available Models

**Endpoint:** `GET https://openrouter.ai/api/v1/models`

**Response:**

```json
{
  "data": [
    {
      "id": "openai/gpt-4o",
      "name": "GPT-4o",
      "description": "OpenAI's most advanced multimodal model",
      "context_length": 128000,
      "pricing": {
        "prompt": "0.000005",
        "completion": "0.000015"
      },
      "architecture": {
        "modality": "text+image->text",
        "tokenizer": "GPT"
      },
      "supported_parameters": ["temperature", "top_p", "max_tokens"]
    }
  ]
}
```

### Model Routing and Fallbacks

You can specify fallback models for resilience:

```json
{
  "models": [
    "openai/gpt-4o",
    "anthropic/claude-3.5-sonnet",
    "google/gemini-2.5-pro-preview"
  ],
  "route": "fallback"
}
```

OpenRouter tries your primary choice first, then alternatives in order if the first fails.

______________________________________________________________________

## Request/Response Format

### Request Parameters

#### Required Parameters

- `model` (string): Model identifier (unless default is set)
- `messages` (array) OR `prompt` (string): Content to process

#### Core Parameters

- `stream` (boolean): Enable Server-Sent Events streaming
- `max_tokens` (integer): Maximum tokens to generate \[1, context_length)
- `temperature` (float): Sampling temperature \[0, 2\]
- `top_p` (float): Nucleus sampling parameter
- `top_k` (integer): Top-k sampling parameter
- `frequency_penalty` (float): Penalize frequent tokens
- `presence_penalty` (float): Penalize tokens based on presence
- `repetition_penalty` (float): Penalize repetitive tokens
- `seed` (integer): For reproducible outputs

#### Response Control

- `response_format` (object): `{ "type": "json_object" }` for structured outputs
- `stop` (string | array): Termination sequences

#### Tool Integration

- `tools` (array): Function definitions for tool calling
- `tool_choice` (string | object): Control tool usage ('none', 'auto', or specific function)

#### OpenRouter-Specific

- `transforms` (array): Prompt transformation options
- `models` (array): Model routing array for fallbacks
- `route` (string): Fallback routing strategy
- `provider` (object): Provider preference settings

### Response Format

All responses follow OpenAI's Chat API format:

```json
{
  "id": "gen-abc123",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Response text here"
      },
      "finish_reason": "stop"
    }
  ],
  "created": 1700000000,
  "model": "openai/gpt-4o",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```

#### Finish Reasons

Normalized across all providers:

- `stop`: Natural completion
- `length`: Hit max_tokens limit
- `tool_calls`: Model wants to call a function
- `content_filter`: Blocked by content policy
- `error`: Error occurred

### Token Accounting

**Default:** Token counts use GPT-4o's tokenizer for normalization.

**Native Counts:** For accurate token counts using the model's native tokenizer, query:

```
GET /api/v1/generation?id={generation_id}
```

**Important:** Token counts (and costs) vary between models, even with identical inputs/outputs.

______________________________________________________________________

## Rate Limits

### Free Tier Limits

**Without Purchased Credits:**

- 50 requests per day
- 20 requests per minute
- Access to 25+ free models

**With $10+ in Credits:**

- 1,000 requests per day on free models
- 20 requests per minute

### Paid Tier Limits

**Pay-as-you-go and Enterprise:**

- No platform-level rate limits
- 1 request per credit per second
- Up to 500 requests per second (surge limit)
- Higher limits available on request

### Important Notes

- Rate limits are global per account (multiple API keys don't increase limits)
- Different models have varying limits (can distribute load across models)
- Accounts with negative credit balance get 402 Payment Required errors (even for free models)
- DDoS protection via Cloudflare blocks excessive usage

### Monitoring Usage

Check usage via: `GET /api/v1/key`

Returns:

- All-time usage
- Daily, weekly, monthly usage
- Remaining credits
- Rate limit status
- BYOK (Bring Your Own Key) usage tracking

______________________________________________________________________

## Pricing

### Pricing Tiers

| Plan              | Models          | Providers     | Platform Fee | Rate Limits              |
| ----------------- | --------------- | ------------- | ------------ | ------------------------ |
| **Free**          | 25+ free models | 4 providers   | 0%           | 50 req/day, 20 req/min   |
| **Pay-as-you-go** | 300+ models     | 60+ providers | 5.5%         | No limits (with credits) |
| **Enterprise**    | 300+ models     | 60+ providers | Custom       | Custom, with SLAs        |

### Key Pricing Points

**No Markup:** OpenRouter does not mark up provider pricing. Prices shown are exactly what you'd pay on provider websites.

**Per-Token Billing:** Input and output tokens are billed per model at posted rates.

**Free Models:** Available with `:free` suffix (e.g., `google/gemini-flash-1.5:free`)

**Failed Requests:** Requests that fail and route to fallback models are not billed for the failed portion.

**BYOK (Bring Your Own Key):**

- First 1M requests/month: Free
- Subsequent usage: 5% fee of what the model would normally cost

### Feature Comparison

**Free Plan Includes:**

- Activity logs
- Chat access
- Basic API functionality

**Pay-as-you-go Adds:**

- Budgets & spend controls
- Prompt caching
- Auto-routing
- Provisioning API keys
- Data policy-based routing

**Enterprise Adds:**

- Admin controls
- SSO/SAML
- Provider data explorer
- Contractual SLAs
- Dedicated support (shared Slack)
- Optional dedicated rate limits

### Taxes

Prices do not include taxes. VAT/GST added where required.

______________________________________________________________________

## Python Code Examples

### Example 1: Basic Text Chat

```python
from openai import OpenAI
import os

# Initialize client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

# Send a simple text prompt
response = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[
        {"role": "user", "content": "Hello! What can you help me with?"}
    ]
)

print(response.choices[0].message.content)
```

### Example 2: Streaming Response

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

# Stream the response
stream = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[
        {"role": "user", "content": "Tell me a story about a robot."}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end='', flush=True)
```

### Example 3: Vision - Image from URL

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

response = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What's in this image? Describe it in detail."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image.jpg"
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

### Example 4: Vision - Local Image with Base64

```python
from openai import OpenAI
import os
import base64

def encode_image_to_base64(image_path):
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_mime_type(image_path):
    """Determine MIME type from file extension."""
    extension = os.path.splitext(image_path)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    return mime_types.get(extension, 'image/jpeg')

# Initialize client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

# Encode image
image_path = "path/to/your/image.jpg"
base64_image = encode_image_to_base64(image_path)
mime_type = get_mime_type(image_path)

# Send request with base64 image
response = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What objects do you see in this image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}"
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

### Example 5: Multiple Images with Error Handling

```python
from openai import OpenAI
import os
import base64
from typing import Optional, Tuple

def encode_image_to_base64(image_path: str) -> Optional[Tuple[str, str]]:
    """
    Encode an image to base64 with error handling.

    Returns:
        Tuple of (base64_string, mime_type) or None if error occurs
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None

    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

        # Determine MIME type
        extension = os.path.splitext(image_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(extension, 'image/jpeg')

        return encoded_string, mime_type
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None

# Initialize client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

# Encode multiple images
image_paths = ["image1.jpg", "image2.png"]
content = [
    {"type": "text", "text": "Compare these images and describe the differences."}
]

for image_path in image_paths:
    result = encode_image_to_base64(image_path)
    if result:
        base64_image, mime_type = result
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{base64_image}"
            }
        })

# Send request
response = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": content}]
)

print(response.choices[0].message.content)
```

### Example 6: Model Fallback

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

# Use model fallback for reliability
response = client.chat.completions.create(
    extra_body={
        "models": [
            "openai/gpt-4o",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-2.5-pro-preview"
        ],
        "route": "fallback"
    },
    messages=[
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ]
)

print(f"Model used: {response.model}")
print(response.choices[0].message.content)
```

### Example 7: JSON Response Format

```python
from openai import OpenAI
import os
import json

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

response = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[
        {
            "role": "user",
            "content": "List 3 programming languages with their use cases in JSON format."
        }
    ],
    response_format={"type": "json_object"}
)

# Parse JSON response
result = json.loads(response.choices[0].message.content)
print(json.dumps(result, indent=2))
```

### Example 8: Using Direct HTTP Requests

```python
import requests
import os

def call_openrouter(prompt: str, model: str = "openai/gpt-4o"):
    """Call OpenRouter API using direct HTTP requests."""
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-site.com",  # Optional
        "X-Title": "Your App Name"  # Optional
    }

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()

# Example usage
result = call_openrouter("What is the capital of France?")
print(result['choices'][0]['message']['content'])
```

### Example 9: List Available Models

```python
import requests
import os

def list_models():
    """Fetch and display available models."""
    url = "https://openrouter.ai/api/v1/models"

    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    models = response.json()['data']

    # Print free models
    print("Free Models:")
    for model in models:
        if model['id'].endswith(':free'):
            print(f"  - {model['id']}: {model['name']}")

    print("\nVision Models:")
    for model in models:
        if 'vision' in model['id'].lower() or 'image' in model.get('architecture', {}).get('modality', ''):
            print(f"  - {model['id']}: {model['name']}")

list_models()
```

### Example 10: Complete Script Similar to hello.py

```python
#!/usr/bin/env python3
"""
OpenRouter API Demo - Similar to Claude Code SDK hello.py
Demonstrates text and vision capabilities with OpenRouter.
"""

import os
import sys
import base64
import logging
from typing import Optional, Tuple
from pathlib import Path
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key. If not provided, reads from OPENROUTER_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        logger.info("OpenRouter client initialized")

    def chat(self, message: str, model: str = "openai/gpt-4o", stream: bool = False) -> str:
        """
        Send a text message to the model.

        Args:
            message: The text prompt
            model: Model identifier
            stream: Whether to stream the response

        Returns:
            The model's response text
        """
        logger.info(f"Sending message to {model}")

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": message}],
                stream=stream
            )

            if stream:
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        print(content, end='', flush=True)
                        full_response += content
                print()  # New line after streaming
                return full_response
            else:
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise

    def analyze_image(
        self,
        image_path: str,
        prompt: str = "What's in this image?",
        model: str = "openai/gpt-4o"
    ) -> str:
        """
        Analyze an image with a text prompt.

        Args:
            image_path: Path to the image file
            prompt: Text prompt about the image
            model: Vision-capable model identifier

        Returns:
            The model's analysis of the image
        """
        logger.info(f"Analyzing image: {image_path}")

        # Encode image
        result = self._encode_image(image_path)
        if not result:
            raise ValueError(f"Failed to encode image: {image_path}")

        base64_image, mime_type = result

        # Create request
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error in analyze_image: {e}")
            raise

    def _encode_image(self, image_path: str) -> Optional[Tuple[str, str]]:
        """
        Encode an image to base64.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (base64_string, mime_type) or None if error
        """
        path = Path(image_path)

        if not path.exists():
            logger.error(f"Image file not found: {image_path}")
            return None

        try:
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

            # Determine MIME type
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(path.suffix.lower(), 'image/jpeg')

            logger.info(f"Image encoded successfully: {mime_type}")
            return encoded_string, mime_type

        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return None


def main():
    """Main demo function."""
    print("OpenRouter API Demo")
    print("=" * 50)

    try:
        # Initialize client
        client = OpenRouterClient()

        # Example 1: Simple text chat
        print("\n1. Simple Text Chat:")
        print("-" * 50)
        response = client.chat("Hello! Tell me a fun fact about space.")
        print(response)

        # Example 2: Streaming response
        print("\n2. Streaming Response:")
        print("-" * 50)
        client.chat(
            "Count from 1 to 5 and explain why each number is interesting.",
            stream=True
        )

        # Example 3: Using a free model
        print("\n3. Using Free Model (Gemini Flash):")
        print("-" * 50)
        response = client.chat(
            "What is Python?",
            model="google/gemini-flash-1.5:free"
        )
        print(response)

        # Example 4: Vision (if image provided)
        if len(sys.argv) > 1:
            image_path = sys.argv[1]
            print(f"\n4. Image Analysis ({image_path}):")
            print("-" * 50)
            response = client.analyze_image(
                image_path,
                "Describe this image in detail."
            )
            print(response)

        print("\n" + "=" * 50)
        print("Demo completed successfully!")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Running the Complete Example

```bash
# Set your API key
export OPENROUTER_API_KEY="your-api-key-here"

# Run without image
python openrouter_demo.py

# Run with image analysis
python openrouter_demo.py path/to/image.jpg
```

______________________________________________________________________

## Additional Resources

- **Official Documentation:** https://openrouter.ai/docs
- **API Reference:** https://openrouter.ai/docs/api-reference/overview
- **Models List:** https://openrouter.ai/models
- **Pricing:** https://openrouter.ai/pricing
- **API Keys:** https://openrouter.ai/keys
- **Community:** https://discord.gg/openrouter

______________________________________________________________________

## Summary

OpenRouter provides a unified, OpenAI-compatible API for accessing hundreds of AI models with:

1. **Simple Authentication:** Bearer token in Authorization header
1. **Text Prompts:** Standard chat completions endpoint
1. **Vision Support:** Base64 or URL images in message content
1. **Flexible Model Selection:** 300+ models with fallback support
1. **Transparent Pricing:** No markup, pay provider rates + 5.5% platform fee
1. **Generous Free Tier:** 25+ free models with reasonable limits
1. **Python Compatibility:** Works with OpenAI SDK or direct HTTP requests

The API is production-ready and suitable for building applications similar to the Claude Code SDK, with the advantage of accessing multiple providers and models through a single interface.
