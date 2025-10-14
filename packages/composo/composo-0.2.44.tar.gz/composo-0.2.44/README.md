[//]: # (##############################)

[//]: # (N.B. recommend keeping sdk/readme.md and docs/pages/sdk/overview - docs overview and pypi cover page - identical to minimise maintenance)
[//]: # (N.B. SDK docs should contain only SDK-specifc features e.g. multiple criteria, async, etc. General tool calling or RAG docs should be elsewhere)

[//]: # (##############################)

Composo provides a Python SDK for Composo evaluation, with:
- **Dual Client Support**: Both synchronous and asynchronous clients
- **Convenient Format**: Compatible with python dictionaries and results objects from OpenAI and Anthropic
- **HTTP Goodies**: Connection pooling + retry logic

> **Note:** This SDK is for Python users. If you're using TypeScript, JavaScript, or other languages, please refer to the [REST API Reference](https://docs.composo.ai/rest-api-reference) to call the API directly.

## Installation

Install the SDK using pip:

```bash wrap
pip install composo
```

# Quick Start

Let's run a simple *Hello World* evaluation to get started with Composo evaluation.

```python Python
from composo import Composo

composo_client = Composo()

result = composo_client.evaluate(
    messages=[
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ],
    criteria="Reward responses that are friendly"
)

print(f"Score: {result.score}")
print(f"Explanation: {result.explanation}")
```

# Reference

### Client Parameters

Both `Composo` and `AsyncComposo` clients accept the following parameters during instantiation:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | `str` | No* | `None` | Your Composo API key. If not provided, will use `COMPOSO_API_KEY` environment variable |
| `num_retries` | `int` | No | `1` | Number of retry attempts for failed requests |

*Required if `COMPOSO_API_KEY` environment variable is not set.

### Evaluation Method Parameters

The `evaluate()` method accepts the following parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `messages` | `List[Dict]` | Yes | List of message dictionaries with 'role' and 'content' keys |
| `criteria` | `str` or `List[str]` | Yes | Evaluation criteria (single string or list of criteria) |
| `tools` | `List[Dict]` | No | Tool definitions for evaluating tool calls |
| `result` | `OpenAI/Anthropic Result Object` | No | Pre-computed LLM result object to evaluate |

#### Environment Variables

The SDK supports the following environment variables:

- `COMPOSO_API_KEY`: Your Composo API key (used when `api_key` parameter is not provided)

### Response Format

The `evaluate` method returns an `EvaluationResponse` object:

```python Python
class EvaluationResponse:
    score: Optional[float]      # Score from 0-1
    explanation: str            # Evaluation explanation
```

# Async Evaluation

Use the async client when you need to run multiple evaluations concurrently or integrate with async workflows.

```python Python
import asyncio
from composo import AsyncComposo

async def main():
    composo_client = AsyncComposo()
    result = await composo_client.evaluate(
        messages=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ],
        criteria="Reward responses that are friendly"
    )
    
    print(f"Score: {result.score}")
    print(f"Explanation: {result.explanation}")

asyncio.run(main())
```


# Multiple Criteria Evaluation

When evaluating against multiple criteria, the async client runs all evaluations concurrently for better performance.

```python Python
import os
from composo import Composo

composo_client = Composo()

messages = [
    {"role": "user", "content": "Explain quantum computing in simple terms"},
    {"role": "assistant", "content": "Quantum computing uses quantum mechanics to process information..."}
]

criteria = [
    "Reward responses that explain complex topics in simple terms",
    "Reward responses that provide accurate technical information",
    "Reward responses that are engaging and easy to understand"
]

results = composo_client.evaluate(messages=messages, criteria=criteria)

for i, result in enumerate(results):
    print(f"Criteria {i+1}: Score = {result.score}")
    print(f"Explanation: {result.explanation}\n")
```

# Evaluating OpenAI/Anthropic Outputs

You can directly evaluate the result of a call to the OpenAI SDK by passing the return of completions.create to composo evaluate. N.B. Composo will always evaluate choices[0].

```python Python
import os
import openai
from composo import Composo

composo_client = Composo()

openai_composo_client = openai.OpenAI(api_key="your-openai-key")
openai_result = openai_composo_client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is machine learning?"}]
)

result = composo_client.evaluate(
    messages=[{"role": "user", "content": "What is machine learning?"}],
    result=openai_result,
    criteria="Reward accurate technical explanations"
)

print(f"Score: {result.score}")
```


# Error Handling

The SDK provides specific exception types:

```python Python
from composo import (
    ComposoError,
    RateLimitError,
    MalformedError,
    APIError,
    AuthenticationError
)

try:
    result = composo_client.evaluate(messages=messages, criteria=criteria)
except RateLimitError:
    print("Rate limit exceeded")
except AuthenticationError:
    print("Invalid API key")
except ComposoError as e:
    print(f"Composo error: {e}")
```

## Logging

The SDK uses Python's standard logging module. Configure logging level:

```python Python
import logging
logging.getLogger("composo").setLevel(logging.INFO)
```
