# MCP Server Integration Guide

Complete guide to integrating Paylink Tracer into your MCP server.

## Installation

```bash
pip install paylink-tracer
```

## Quick Integration

### 1. Import

```python
from paylink_tracer import configure, paylink_tracer
```

### 2. Configure at Startup

```python
from dotenv import load_dotenv
import os

load_dotenv()

# Configure the tracer
configure(
    base_url=os.getenv("PAYLINK_BASE_URL", "https://api.paylink.com"),
    project_name=os.getenv("PAYLINK_PROJECT_NAME", "My MCP Server"),
    payment_provider=os.getenv("PAYLINK_PAYMENT_PROVIDER", "mpesa"),
    api_key=os.getenv("PAYLINK_API_KEY"),  # Optional
)
```

### 3. Add Decorator to call_tool

```python
@app.call_tool()
@paylink_tracer  # Add this line!
async def call_tool(
    name: str,
    arguments: dict[str, Any],
    request_id: str | None = None,
) -> list[TextContent]:
    # Your existing implementation
    if name == "stk_push":
        result = await stk_push_handler(arguments)
    else:
        return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

    return [TextContent(type="text", text=result)]
```

## Complete Example

```python
import logging
import os
from mcp.server.lowlevel import Server
from mcp.types import TextContent, Tool
from dotenv import load_dotenv

from paylink_tracer import configure, paylink_tracer

load_dotenv()

# Configure tracer
configure(
    base_url=os.getenv("PAYLINK_BASE_URL"),
    project_name=os.getenv("PAYLINK_PROJECT_NAME"),
    payment_provider=os.getenv("PAYLINK_PAYMENT_PROVIDER", "mpesa"),
    api_key=os.getenv("PAYLINK_API_KEY"),
)

app = Server("mpesa_mcp_server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return get_mpesa_tools()

@app.call_tool()
@paylink_tracer  # Automatic tracing!
async def call_tool(
    name: str,
    arguments: dict[str, Any],
    request_id: str | None = None,
) -> list[TextContent]:
    try:
        if name == "stk_push":
            result = await stk_push_handler(arguments)
        else:
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

## Environment Variables

Add to your `.env` file:

```bash
PAYLINK_BASE_URL=https://api.paylink.com
PAYLINK_PROJECT_NAME=My MCP Server
PAYLINK_PAYMENT_PROVIDER=mpesa
PAYLINK_API_KEY=your-api-key-here
PAYLINK_TRACING_ENABLED=true
```

## What Gets Traced

Every tool call is automatically captured:

```json
{
    "trace_id": "unique-uuid",
    "tool_name": "stk_push",
    "project_name": "My MCP Server",
    "arguments": {
        "amount": "200000",
        "phone_number": "254704020370",
        ...
    },
    "response": {
        "status": "success",
        ...
    },
    "status": "success",
    "duration_ms": 1850.32,
    "payment_provider": "mpesa",
    "request_id": "req_12345"
}
```

## Status Detection

The tracer automatically detects success/failure:

1. Parses JSON response for `"status"` field
2. Looks for error keywords ("error", "failed")
3. Looks for success keywords ("success", "accepted")
4. Captures exceptions as errors

## Error Handling

Errors are automatically captured:

```python
@paylink_tracer
async def call_tool(name: str, arguments: dict):
    if name == "stk_push":
        # If this raises an exception
        result = await stk_push_handler(arguments)  # ← Error caught here
        # Trace sent with status="error" and error message
        # Exception is re-raised
```

## Migration from Custom Tracer

### Before (Custom Tracer)

```python
from tracer.tracing import paylink_tracer
from tracer.context import request_headers_map, current_request_id

# Complex context management...
request_headers_map[request_id] = headers
current_request_id.set(request_id)

@paylink_tracer
async def call_tool(...):
    # Implementation
```

### After (SDK)

```python
from paylink_tracer import configure, paylink_tracer

# Simple configuration
configure(
    base_url="https://api.paylink.com",
    project_name="My MCP Server",
    payment_provider="mpesa",
)

@paylink_tracer
async def call_tool(...):
    # Same implementation!
```

**Key Benefits:**

- ✅ No context management needed
- ✅ No MongoDB operations
- ✅ Sends directly to API
- ✅ Same decorator interface
- ✅ Simpler, faster, cleaner

## Disable for Testing

```python
from paylink_tracer import disable_tracing

# Disable temporarily
disable_tracing()

# Or via environment
os.environ["PAYLINK_TRACING_ENABLED"] = "false"
```

## Complete Working Example

See `examples/mcp_server_example.py` for a complete, runnable example:

```bash
python examples/mcp_server_example.py
```

## Troubleshooting

### Traces not being sent?

1. Check `PAYLINK_BASE_URL` is set
2. Check `PAYLINK_TRACING_ENABLED` is "true"
3. Verify your function has `name` and `arguments` parameters

### Want to see trace errors?

Traces are sent silently by default. To see errors:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Questions?

Open an issue on GitHub or contact the Paylink team.

---

Happy tracing! 🚀
