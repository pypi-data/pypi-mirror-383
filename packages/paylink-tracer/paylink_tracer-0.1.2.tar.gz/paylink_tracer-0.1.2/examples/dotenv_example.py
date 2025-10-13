"""
Example using .env file with python-dotenv for configuration.

This is the cleanest approach - just create a .env file and use @paylink_tracer!
"""

import asyncio
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("✅ Loaded configuration from .env file\n")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Using default/environment variables instead\n")

# Import and use - NO configure() needed!
from paylink_tracer import paylink_tracer


@paylink_tracer
async def process_payment(name: str, arguments: dict):
    """Process payment - automatically traced from .env config!"""
    await asyncio.sleep(0.3)

    if name == "stk_push":
        return json.dumps(
            {
                "status": "success",
                "message": "Success. Request accepted for processing",
                "merchant_request_id": "mrq_123456",
                "checkout_request_id": "ws_CO_123456",
                "amount": arguments["amount"],
                "phone_number": arguments["phone_number"],
            }
        )

    return json.dumps({"status": "error", "message": f"Unknown tool: {name}"})


async def main():
    """Run the example."""

    print("🔐 .env File Configuration Example")
    print("=" * 60)
    print("\n📝 Create a .env file with:")
    print(
        """
    PAYLINK_API_KEY=plk_live_chYjfBob2mVZcnOjE0yst0Sq9yysmuYwewrCJ3NGzhzD3tQ
    PAYLINK_PROJECT=Demo Project
    PAYMENT_PROVIDER=["mpesa"]
    PAYLINK_TRACING=enabled
    """
    )
    print("Then just use @paylink_tracer - no configure() needed!")
    print("Base URL is hardcoded to: https://api.paylink.co.ke\n")

    print("💳 Processing payment...")
    result = await process_payment(
        name="stk_push",
        arguments={
            "amount": "50000",
            "phone_number": "254712345678",
            "account_reference": "ORDER456",
            "transaction_desc": "Payment for services",
        },
    )

    data = json.loads(result)
    print(f"✅ Status: {data['status']}")
    print(f"   Message: {data['message']}\n")

    print("=" * 60)
    print("📊 Trace sent to API using .env configuration!")


if __name__ == "__main__":
    asyncio.run(main())
