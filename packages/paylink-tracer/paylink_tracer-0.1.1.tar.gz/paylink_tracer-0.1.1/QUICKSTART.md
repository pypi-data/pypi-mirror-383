# Quick Start Guide

Get started with Paylink Tracer in 2 steps!

## Step 1: Set Environment Variables

```bash
export PAYLINK_API_KEY="plk_live_chYjfBob2mVZcnOjE0yst0Sq9yysmuYwewrCJ3NGzhzD3tQ"
export PAYLINK_PROJECT="Demo Project"
export PAYMENT_PROVIDER='["mpesa"]'
export PAYLINK_TRACING="enabled"
```

## Step 2: Use Decorator

```python
from paylink_tracer import paylink_tracer

@paylink_tracer
async def call_tool(name: str, arguments: dict):
    # Your payment logic
    return result
```

## That's It!

Every call is automatically traced and sent to `https://api.paylink.co.ke/api/v1/trace`

```python
result = await call_tool(
    name="stk_push",
    arguments={"amount": "200000", "phone": "254704020370"}
)
```

## Or Use .env File (Recommended!)

Create `.env`:

```bash
PAYLINK_API_KEY=plk_live_chYjfBob2mVZcnOjE0yst0Sq9yysmuYwewrCJ3NGzhzD3tQ
PAYLINK_PROJECT=Demo Project
PAYMENT_PROVIDER=["mpesa"]
PAYLINK_TRACING=enabled
```

Use it:

```python
from dotenv import load_dotenv
load_dotenv()

from paylink_tracer import paylink_tracer

@paylink_tracer
async def call_tool(name: str, arguments: dict):
    return result
```

## Full Example

```python
# Set environment variables or use .env file

from paylink_tracer import paylink_tracer
import asyncio
import json

@paylink_tracer
async def call_tool(name: str, arguments: dict):
    if name == "stk_push":
        return json.dumps({
            "status": "success",
            "checkout_id": "ws_CO_123456",
        })
    return json.dumps({"status": "error"})

async def main():
    result = await call_tool(
        name="stk_push",
        arguments={"amount": "1000", "phone": "254700000000"}
    )
    print(result)

asyncio.run(main())
```

## Run Examples

```bash
python examples/env_config_example.py
python examples/dotenv_example.py
```

## Only 4 Environment Variables Needed

1. `PAYLINK_API_KEY` - Your API key
2. `PAYLINK_PROJECT` - Your project name
3. `PAYMENT_PROVIDER` - Payment provider (e.g., `["mpesa"]`)
4. `PAYLINK_TRACING` - Optional: `enabled` or `disabled`

**Base URL is hardcoded - no need to configure it!**

Happy tracing! 🚀
