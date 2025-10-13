"""
Example showing how to use paylink_tracer in an MCP server context.

This matches the usage pattern from your MCP server.
"""

import asyncio
from typing import Any
from paylink_tracer import paylink_tracer, configure


# Configure once at startup
configure(
    api_key="plk_live_chYjfBob2mVZcnOjE0yst0Sq9yysmuYwewrCJ3NGzhzD3tQ",
    project_name="Payment MCP Server",
    payment_provider="mpesa",
)


# Simulate MCP TextContent
class TextContent:
    def __init__(self, type: str, text: str):
        self.type = type
        self.text = text


async def stk_push_handler(arguments: dict) -> str:
    """Simulate STK Push handler."""
    await asyncio.sleep(0.1)  # Simulate API call

    import json

    return json.dumps(
        {
            "status": "success",
            "message": "Success. Request accepted for processing",
            "merchant_request_id": "b8d3-4ce1-bd6b-5c9ce5bf25db28342",
            "checkout_request_id": "ws_CO_25092025130341530704020370",
            "amount": arguments.get("amount"),
            "phone_number": arguments.get("phone_number"),
            "reference": arguments.get("account_reference"),
        }
    )


# Decorate your tool handler with @paylink_tracer
@paylink_tracer
async def call_tool(
    name: str,
    arguments: dict[str, Any],
    request_id: str | None = None,
) -> list[TextContent]:
    """Call a payment tool - automatically traced!"""

    try:
        if name == "stk_push":
            result = await stk_push_handler(arguments)
            return [TextContent(type="text", text=result)]
        else:
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

    except ValueError as e:
        return [TextContent(type="text", text=f"Invalid input: {str(e)}")]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Something went wrong while running tool '{name}'. Error: {str(e)}",
            )
        ]


async def main():
    """Run the example."""

    print("🚀 MCP Server Example with Paylink Tracer")
    print("=" * 60)
    print("✅ Tracer configured!")
    print("   API Endpoint: https://api.paylink.co.ke/api/v1/trace")
    print("   Project: Payment MCP Server")
    print("   Provider: mpesa\n")

    # Simulate multiple requests
    print("1️⃣  Processing STK Push payment...")
    result1 = await call_tool(
        name="stk_push",
        arguments={
            "amount": "200000",
            "phone_number": "254704020370",
            "account_reference": "ORDER123",
            "transaction_desc": "iPhone 15",
        },
    )
    print(f"   Result: {result1[0].text[:80]}...")

    print("\n2️⃣  Processing another payment...")
    result2 = await call_tool(
        name="stk_push",
        arguments={
            "amount": "50000",
            "phone_number": "254712345678",
            "account_reference": "ORDER456",
            "transaction_desc": "Samsung Galaxy",
        },
    )
    print(f"   Result: {result2[0].text[:80]}...")

    print("\n" + "=" * 60)
    print("✅ All traces sent to: https://api.paylink.co.ke/api/v1/trace")
    print("\n📊 Each trace includes:")
    print("  • trace_id (unique UUID)")
    print("  • tool_name (from function args)")
    print("  • project_name (from config)")
    print("  • arguments (from function args)")
    print("  • response (parsed from result)")
    print("  • status (auto-detected: success/error)")
    print("  • duration_ms (auto-measured)")
    print("  • payment_provider (from config)")
    print("  • request_id (auto-generated or from args)")


if __name__ == "__main__":
    asyncio.run(main())
