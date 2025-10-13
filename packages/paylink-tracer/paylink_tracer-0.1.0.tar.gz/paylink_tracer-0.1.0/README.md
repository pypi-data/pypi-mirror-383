# Paylink Tracer SDK

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A simple and lightweight tracing SDK for Paylink payment operations. Automatically capture and send payment tool execution data to your Paylink API with just one decorator!

## ✨ Features

- 🎯 **Super Simple** - Just set 4 env vars and add `@paylink_tracer`
- 🌍 **Auto-Configuration** - Reads from environment variables automatically
- 🚀 **Zero Dependencies** - Pure Python, no external dependencies
- 📊 **Automatic Tracing** - Captures arguments, responses, duration, errors
- 🔄 **Async Support** - Works with async functions
- 🛡️ **Error Tracking** - Automatically captures and reports errors
- ⚡ **Non-Blocking** - Doesn't slow down your operations

## 📦 Installation

```bash
pip install paylink-tracer
```

## 🚀 Quick Start (Environment Variables)

### Step 1: Set Environment Variables

```bash
export PAYLINK_API_KEY="plk_live_chYjfBob2mVZcnOjE0yst0Sq9yysmuYwewrCJ3NGzhzD3tQ"
export PAYLINK_PROJECT="Demo Project"
export PAYMENT_PROVIDER='["mpesa"]'
export PAYLINK_TRACING="enabled"
```

### Step 2: Use Decorator

```python
from paylink_tracer import paylink_tracer
import json

@paylink_tracer
async def call_tool(name: str, arguments: dict):
    # Your payment logic
    return json.dumps({"status": "success", ...})

# That's it! Automatically traced!
result = await call_tool(name="stk_push", arguments={...})
```

**No configure() needed! Base URL is hardcoded to `https://api.paylink.co.ke`**

## 🔐 Using .env File (Recommended)

Create `.env` file:

```bash
PAYLINK_API_KEY=plk_live_chYjfBob2mVZcnOjE0yst0Sq9yysmuYwewrCJ3NGzhzD3tQ
PAYLINK_PROJECT=Demo Project
PAYMENT_PROVIDER=["mpesa"]
PAYLINK_TRACING=enabled
```

Use with python-dotenv:

```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file

from paylink_tracer import paylink_tracer

@paylink_tracer
async def call_tool(name: str, arguments: dict):
    # Your code
    return result

# Automatically traced from .env config!
```

## 📤 What Gets Sent

The SDK automatically sends this JSON to `https://api.paylink.co.ke/api/v1/trace`:

```json
{
    "trace_id": "e4f1a2b3-5678-90ab-cdef-1234567890a6",
    "tool_name": "stk_push",
    "project_name": "Demo Project",
    "arguments": {
        "amount": "200000",
        "phone_number": "254704020370",
        "account_reference": "ORDER123",
        "transaction_desc": "iPhone 15"
    },
    "response": {
        "status": "success",
        "message": "Request accepted for processing",
        "checkout_request_id": "ws_CO_123456",
        ...
    },
    "status": "success",
    "duration_ms": 1850.32,
    "payment_provider": "mpesa",
    "request_id": "req_12345"
}
```

## 📖 Configuration

### Environment Variables (Automatic)

The tracer automatically reads these environment variables:

| Variable           | Required | Description          | Example                                            |
| ------------------ | -------- | -------------------- | -------------------------------------------------- |
| `PAYLINK_API_KEY`  | Yes      | Your Paylink API key | `plk_live_chYjfBob2mVZcnOjE0yst0Sq9yysmuYwewrC...` |
| `PAYLINK_PROJECT`  | Yes      | Your project name    | `Demo Project`                                     |
| `PAYMENT_PROVIDER` | Yes      | Payment provider     | `["mpesa"]` or `mpesa`                             |
| `PAYLINK_TRACING`  | No       | Enable/disable       | `enabled` (default) or `disabled`                  |

**Base URL is hardcoded to `https://api.paylink.co.ke` - no need to configure it!**

### Manual Configuration (Optional)

```python
from paylink_tracer import configure

configure(
    api_key="plk_live_abc123...",
    project_name="My Project",
    payment_provider="mpesa",
)
```

Manual configuration **overrides** environment variables.

## 🎯 Complete Example

```python
# .env file:
# PAYLINK_API_KEY=plk_live_chYjfBob2mVZcnOjE0yst0Sq9yysmuYwewrCJ3NGzhzD3tQ
# PAYLINK_PROJECT=Demo Project
# PAYMENT_PROVIDER=["mpesa"]

from paylink_tracer import paylink_tracer
import asyncio
import json

@paylink_tracer
async def call_tool(name: str, arguments: dict):
    """Process payment - automatically traced!"""

    if name == "stk_push":
        # Your payment logic
        result = await process_stk_push(arguments)
        return json.dumps(result)

    return json.dumps({"status": "error", "message": "Unknown tool"})

async def main():
    result = await call_tool(
        name="stk_push",
        arguments={"amount": "1000", "phone": "254700000000"}
    )
    print(result)

asyncio.run(main())
```

## 📊 Status Detection

The tracer intelligently detects success/error status:

```python
# Checks JSON response
{"status": "success"} → status: "success"
{"status": "error"} → status: "error"

# Checks keywords
"Error: Payment failed" → status: "error"
"Success. Request accepted" → status: "success"

# Catches exceptions
raise ValueError("...") → status: "error"
```

## 🛡️ Error Handling

Errors are automatically captured and traced:

```python
@paylink_tracer
async def payment(name: str, arguments: dict):
    if amount > limit:
        # Error response - traced as error
        return json.dumps({"status": "error", "message": "Limit exceeded"})

    # Or raise exception - also traced as error
    if not valid:
        raise ValueError("Invalid payment")

    return json.dumps({"status": "success"})
```

## 🔧 Advanced Usage

### Temporarily Disable Tracing

```bash
export PAYLINK_TRACING=disabled
```

Or in code:

```python
from paylink_tracer import disable_tracing

disable_tracing()
```

### Change Base URL (Testing/Staging Only)

```python
from paylink_tracer import set_base_url

set_base_url("https://staging.paylink.co.ke")
```

## 🌐 MCP Server Integration

Perfect for MCP (Model Context Protocol) servers:

```python
# .env file:
# PAYLINK_API_KEY=plk_live_abc123...
# PAYLINK_PROJECT=Payment MCP Server
# PAYMENT_PROVIDER=["mpesa"]

from mcp.server.lowlevel import Server
from mcp.types import TextContent
from paylink_tracer import paylink_tracer
from dotenv import load_dotenv

load_dotenv()  # Load .env configuration

app = Server("mpesa_mcp_server")

# No configure() needed - auto-loads from .env!
@app.call_tool()
@paylink_tracer
async def call_tool(
    name: str,
    arguments: dict,
    request_id: str | None = None,
) -> list[TextContent]:
    result = await stk_push_handler(arguments)
    return [TextContent(type="text", text=result)]
```

## 📝 Examples

Run the examples:

```bash
# Environment variable configuration
python examples/env_config_example.py

# .env file configuration
python examples/dotenv_example.py

# Simple usage
python examples/simple_usage.py

# Error handling
python examples/error_handling.py

# MCP server integration
python examples/mcp_server_example.py
```

## 🔗 API Endpoint

Traces are sent via POST to:

```
https://api.paylink.co.ke/api/v1/trace
```

Headers:

```
Content-Type: application/json
Authorization: Bearer <PAYLINK_API_KEY>
```

## ❓ FAQ

### Q: Do I need to configure the base URL?

A: **No!** The base URL is hardcoded to `https://api.paylink.co.ke`. You only need to set 4 environment variables.

### Q: What environment variables do I need?

A: Just 4:

- `PAYLINK_API_KEY` (your API key)
- `PAYLINK_PROJECT` (your project name)
- `PAYMENT_PROVIDER` (e.g., `["mpesa"]`)
- `PAYLINK_TRACING` (optional, defaults to `enabled`)

### Q: Can I use a .env file?

A: **Yes!** Use `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()

from paylink_tracer import paylink_tracer
# Ready to use!
```

### Q: Do I need to call `configure()`?

A: **No!** Just set environment variables and use `@paylink_tracer`.

### Q: Does this slow down my operations?

A: No! The tracer is lightweight and non-blocking.

### Q: What if the API is down?

A: Failed traces are logged but won't crash your app.

### Q: Can I use this in production?

A: Yes! You can disable it with `PAYLINK_TRACING=disabled`.

### Q: What Python versions are supported?

A: Python 3.8+

## 🤝 Contributing

Contributions welcome! Please submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details.

## 📞 Support

Open an issue on GitHub or contact the Paylink team.

---

Made with ❤️ by the Paylink Team
