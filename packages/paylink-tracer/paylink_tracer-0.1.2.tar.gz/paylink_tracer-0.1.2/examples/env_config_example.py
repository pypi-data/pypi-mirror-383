"""
Example showing automatic configuration from environment variables.

No configure() call needed - just set environment variables and use @paylink_tracer!
"""

import asyncio
import json
import os

# Set environment variables (or use .env file with python-dotenv)
os.environ["PAYLINK_API_KEY"] = "plk_live_chYjfBob2mVZcnOjE0yst0Sq9yysmuYwewrCJ3NGzhzD3tQ"
os.environ["PAYLINK_PROJECT"] = "Auto-Config Project"
os.environ["PAYMENT_PROVIDER"] = '["mpesa"]'
os.environ["PAYLINK_TRACING"] = "enabled"

# Import and use - NO configure() needed!
from paylink_tracer import paylink_tracer


@paylink_tracer
async def call_tool(name: str, arguments: dict):
    """Process payment - automatically traced!"""
    await asyncio.sleep(0.2)

    return json.dumps(
        {
            "status": "success",
            "message": "Request accepted for processing",
            "checkout_request_id": "ws_CO_123456",
            "amount": arguments["amount"],
        }
    )


async def main():
    """Run the example."""

    print("🌍 Environment Variable Configuration Example")
    print("=" * 60)
    print("\n✅ No configure() call needed!")
    print("   Tracer automatically reads from environment variables:\n")
    print(f"   PAYLINK_API_KEY: {os.environ['PAYLINK_API_KEY'][:20]}...")
    print(f"   PAYLINK_PROJECT: {os.environ['PAYLINK_PROJECT']}")
    print(f"   PAYMENT_PROVIDER: {os.environ['PAYMENT_PROVIDER']}")
    print(f"   PAYLINK_TRACING: {os.environ['PAYLINK_TRACING']}")
    print(f"   Base URL: https://api.paylink.co.ke (hardcoded)\n")

    print("📞 Making payment request...")
    result = await call_tool(
        name="stk_push",
        arguments={
            "amount": "100000",
            "phone_number": "254704020370",
            "account_reference": "ORDER789",
        },
    )

    data = json.loads(result)
    print(f"✅ Result: {data['status']}")
    print(f"   Checkout ID: {data['checkout_request_id']}\n")

    print("=" * 60)
    print("📊 Trace automatically sent to API!")
    print("   No configuration code needed - just environment variables!")


if __name__ == "__main__":
    asyncio.run(main())
