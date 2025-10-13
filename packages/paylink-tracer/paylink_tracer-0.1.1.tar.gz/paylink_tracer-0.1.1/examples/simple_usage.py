"""Simple usage example for Paylink Tracer SDK."""

from paylink_tracer import configure, paylink_tracer
import asyncio
import json


# Step 1: Configure the tracer (or use environment variables)
configure(
    api_key="plk_live_chYjfBob2mVZcnOjE0yst0Sq9yysmuYwewrCJ3NGzhzD3tQ",
    project_name="Demo Project",
    payment_provider="mpesa",
)


# Step 2: Decorate your payment functions
@paylink_tracer
async def stk_push(name: str, arguments: dict):
    """Initiate STK Push payment."""
    # Your actual implementation here
    await asyncio.sleep(0.5)  # Simulate API call

    return json.dumps(
        {
            "status": "success",
            "message": "Success. Request accepted for processing",
            "merchant_request_id": "b8d3-4ce1-bd6b-5c9ce5bf25db28342",
            "checkout_request_id": "ws_CO_25092025130341530704020370",
            "amount": arguments["amount"],
            "phone_number": arguments["phone_number"],
            "reference": arguments["account_reference"],
        }
    )


@paylink_tracer
async def check_balance(name: str, arguments: dict):
    """Check account balance."""
    await asyncio.sleep(0.3)

    return json.dumps(
        {
            "status": "success",
            "account_number": arguments["account_number"],
            "balance": "50000",
            "currency": "KES",
        }
    )


@paylink_tracer
async def b2c_payment(name: str, arguments: dict):
    """Make B2C payment."""
    await asyncio.sleep(0.6)

    return json.dumps(
        {
            "status": "success",
            "transaction_id": "QRX123456789",
            "amount": arguments["amount"],
            "phone_number": arguments["phone_number"],
            "result_code": "0",
            "result_desc": "The service request is processed successfully.",
        }
    )


async def main():
    """Demonstrate simple tracing."""

    print("🎯 Paylink Tracer - Simple Usage Example\n")

    # Example 1: STK Push
    print("1️⃣  Making STK Push request...")
    result1 = await stk_push(
        name="stk_push",
        arguments={
            "amount": "200000",
            "phone_number": "254704020370",
            "account_reference": "ORDER123",
            "transaction_desc": "Iphone 15",
        },
    )
    data1 = json.loads(result1)
    print(f"   ✅ {data1['status']}: {data1['message']}\n")

    # Example 2: Check Balance
    print("2️⃣  Checking balance...")
    result2 = await check_balance(name="check_balance", arguments={"account_number": "ACC123456"})
    data2 = json.loads(result2)
    print(f"   ✅ Balance: {data2['balance']} {data2['currency']}\n")

    # Example 3: B2C Payment
    print("3️⃣  Making B2C payment...")
    result3 = await b2c_payment(
        name="b2c_payment",
        arguments={"amount": "5000", "phone_number": "254712345678", "remarks": "Salary payment"},
    )
    data3 = json.loads(result3)
    print(f"   ✅ {data3['status']}: {data3['result_desc']}\n")

    print("=" * 60)
    print("✅ All traces sent to: https://api.paylink.co.ke/api/v1/trace")


if __name__ == "__main__":
    asyncio.run(main())
