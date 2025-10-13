"""Error handling example."""

from paylink_tracer import configure, paylink_tracer
import asyncio
import json


configure(
    api_key="plk_live_chYjfBob2mVZcnOjE0yst0Sq9yysmuYwewrCJ3NGzhzD3tQ",
    project_name="Demo Project",
    payment_provider="mpesa",
)


@paylink_tracer
async def risky_payment(name: str, arguments: dict):
    """Payment that might fail."""
    await asyncio.sleep(0.3)

    amount = int(arguments["amount"])

    # Simulate validation error
    if amount > 150000:
        return json.dumps(
            {
                "status": "error",
                "message": f"Amount {amount} exceeds maximum limit of 150000",
                "code": "AMOUNT_LIMIT_EXCEEDED",
            }
        )

    return json.dumps(
        {
            "status": "success",
            "amount": str(amount),
            "phone_number": arguments["phone_number"],
        }
    )


async def main():
    """Demonstrate error tracing."""

    print("⚠️  Paylink Tracer - Error Handling Example\n")

    # Example 1: Successful payment
    print("1️⃣  Successful payment:")
    result1 = await risky_payment(
        name="risky_payment", arguments={"amount": "50000", "phone_number": "254700000000"}
    )
    data1 = json.loads(result1)
    print(f"   ✅ Status: {data1['status']}\n")

    # Example 2: Failed payment (error will be traced)
    print("2️⃣  Failed payment (exceeds limit):")
    result2 = await risky_payment(
        name="risky_payment", arguments={"amount": "200000", "phone_number": "254700000000"}
    )
    data2 = json.loads(result2)
    print(f"   ❌ Status: {data2['status']}")
    print(f"   ❌ Message: {data2['message']}")
    print(f"   📊 Error trace sent to API\n")

    print("=" * 60)
    print("✅ Both success and error traces were sent to the API")
    print(f"   API Endpoint: https://api.paylink.co.ke/api/v1/trace")


if __name__ == "__main__":
    asyncio.run(main())
