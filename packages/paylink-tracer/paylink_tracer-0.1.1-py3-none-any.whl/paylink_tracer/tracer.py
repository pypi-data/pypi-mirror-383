"""Simple payment tracer for Paylink."""

import uuid
import time
import json
import urllib.request
import urllib.error
from typing import Any, Dict, Optional
from functools import wraps
import os


# Global configuration
_config = {
    "base_url": "http://127.0.0.1:8000",  # Local development server
    "api_key": None,
    "project_name": None,
    "payment_provider": None,
    "enabled": True,
}


def _extract_payment_provider(provider_value: Any) -> Optional[str]:
    """Extract payment provider from various formats (string, list, JSON string)."""
    if not provider_value:
        return None

    # Handle JSON string format like '["mpesa"]'
    if (
        isinstance(provider_value, str)
        and provider_value.startswith("[")
        and provider_value.endswith("]")
    ):
        try:
            parsed = json.loads(provider_value)
            return parsed[0] if isinstance(parsed, list) and parsed else None
        except (json.JSONDecodeError, IndexError):
            return provider_value

    # Handle actual list format
    if isinstance(provider_value, list):
        return provider_value[0] if provider_value else None

    # Handle string format
    return provider_value


def configure(
    api_key: str,
    project_name: str,
    payment_provider: str = "mpesa",
    enabled: bool = True,
) -> None:
    """Configure the tracer globally.

    Note: Base URL defaults to http://127.0.0.1:8000 (local development)

    Args:
        api_key: Your Paylink API key
        project_name: Name of your project
        payment_provider: Payment provider (e.g., "mpesa", "stripe")
        enabled: Whether tracing is enabled

    Example:
        configure(
            api_key="plk_live_abc123...",
            project_name="My E-Commerce App",
            payment_provider="mpesa",
        )
    """
    _config["api_key"] = api_key
    _config["project_name"] = project_name
    _config["payment_provider"] = payment_provider
    _config["enabled"] = enabled


def _get_config_value(key: str, default: Any = None) -> Any:
    """Get config value from config dict or environment variable."""
    # First check global config (but base_url always returns hardcoded value)
    if key == "base_url":
        return _config["base_url"]

    if _config.get(key):
        return _config[key]

    # Then check environment variables
    env_map = {
        "api_key": "PAYLINK_API_KEY",
        "project_name": "PAYLINK_PROJECT",
        "payment_provider": "PAYMENT_PROVIDER",
        "enabled": "PAYLINK_TRACING",
    }

    env_var = env_map.get(key)
    if env_var:
        value = os.getenv(env_var, default)
        if key == "enabled" and isinstance(value, str):
            return value.lower() == "enabled"
        if key == "payment_provider" and value:
            return _extract_payment_provider(value)
        return value

    return default


def _determine_trace_status(result: Any) -> str:
    """Determine if the trace represents a success or failure based on the result."""
    try:
        # Extract text content from result
        if isinstance(result, list) and len(result) > 0 and hasattr(result[0], "text"):
            text_content = result[0].text
        elif isinstance(result, str):
            text_content = result
        elif isinstance(result, dict):
            # Direct dict response
            status = result.get("status", "").lower()
            if status == "success":
                return "success"
            elif status in ["error", "failed", "failure"]:
                return "error"
            return "unknown"
        else:
            return "unknown"

        # Try to parse as JSON and check status
        parsed_result = json.loads(text_content)

        if isinstance(parsed_result, dict):
            status = parsed_result.get("status", "").lower()
            if status == "success":
                return "success"
            elif status in ["error", "failed", "failure"]:
                return "error"

        # Check for error indicators in the text
        text_lower = text_content.lower()
        if any(
            error_word in text_lower for error_word in ["error", "failed", "failure", "exception"]
        ):
            return "error"
        elif any(
            success_word in text_lower for success_word in ["success", "accepted", "completed"]
        ):
            return "success"

    except (json.JSONDecodeError, AttributeError, IndexError):
        # If we can't parse, check for basic error patterns
        if isinstance(result, str) and any(
            error_word in result.lower() for error_word in ["error", "failed", "exception"]
        ):
            return "error"

    return "unknown"


def _extract_result_text(result: Any) -> Any:
    """Extract text content from result."""
    if isinstance(result, list) and len(result) > 0 and hasattr(result[0], "text"):
        # Extract text from TextContent objects
        texts = [item.text for item in result if hasattr(item, "text")]
        # Try to parse each text as JSON
        parsed_texts = []
        for text in texts:
            try:
                parsed_texts.append(json.loads(text))
            except (json.JSONDecodeError, TypeError):
                parsed_texts.append(text)
        return parsed_texts[0] if len(parsed_texts) == 1 else parsed_texts
    elif isinstance(result, str):
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError):
            return result
    else:
        return result


def _send_trace_to_api(
    base_url: str,
    trace_data: Dict[str, Any],
    api_key: Optional[str] = None,
) -> None:
    """Send trace data to the API endpoint.

    Args:
        base_url: Base URL for the API
        trace_data: Trace data to send
        api_key: Optional API key for authentication
    """
    endpoint = f"{base_url.rstrip('/')}/api/v1/trace"

    try:
        data = json.dumps(trace_data, default=str).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
        }

        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        request = urllib.request.Request(
            endpoint,
            data=data,
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=10.0) as resp:
            if resp.status >= 400:
                print(f"[Paylink Tracer] Failed to send trace: HTTP {resp.status}")
    except Exception as e:
        # Silently fail - don't break the application
        if _get_config_value("enabled", True):
            print(f"[Paylink Tracer] Error sending trace: {e}")


def paylink_tracer(func):
    """Decorator to automatically trace payment tool calls.

    Usage:
        # Configure once at startup
        configure(
            base_url="https://api.paylink.com",
            project_name="My Project",
            payment_provider="mpesa",
        )

        # Use decorator on your functions
        @paylink_tracer
        async def call_tool(name: str, arguments: dict):
            # Your implementation
            return result
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Check if tracing is enabled
        enabled = _get_config_value("enabled", True)
        if not enabled:
            return await func(*args, **kwargs)

        # Get configuration
        base_url = _get_config_value("base_url")
        if not base_url:
            # No base URL configured, skip tracing
            return await func(*args, **kwargs)

        api_key = _get_config_value("api_key")
        project_name = _get_config_value("project_name", "unknown")
        payment_provider = _get_config_value("payment_provider", "unknown")

        # Start time
        start_time = time.time()

        # Get tool name from kwargs or args
        tool_name = kwargs.get("name") or (args[0] if args else "unknown")

        # Get tool arguments from kwargs or args
        arguments = kwargs.get("arguments") or (args[1] if len(args) > 1 else {})

        # Generate trace and request IDs
        trace_id = str(uuid.uuid4())
        request_id = kwargs.get("request_id") or f"req_{uuid.uuid4().hex[:10]}"

        # Call the function
        status = "success"
        result = None
        error = None

        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            status = "error"
            error = str(e)
            raise
        finally:
            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)

            # Determine status from result if no error
            if status == "success" and result is not None:
                status = _determine_trace_status(result)

            # Extract clean response from result
            response = _extract_result_text(result) if result is not None else {}

            # Build trace payload
            trace_payload = {
                "trace_id": trace_id,
                "tool_name": tool_name,
                "project_name": project_name,
                "arguments": arguments,
                "response": response,
                "status": status,
                "duration_ms": duration_ms,
                "payment_provider": payment_provider,
                "request_id": request_id,
            }

            if error:
                trace_payload["error"] = error

            # Send trace to API
            _send_trace_to_api(
                base_url=base_url,
                trace_data=trace_payload,
                api_key=api_key,
            )

        return result

    return wrapper


def set_base_url(url: str) -> None:
    """Set the base URL for the API endpoint.

    Use this to override the default local development URL.

    Args:
        url: Base URL (e.g., "https://api.paylink.co.ke", "https://staging.paylink.co.ke")
    """
    _config["base_url"] = url


def enable_tracing() -> None:
    """Enable tracing."""
    _config["enabled"] = True


def disable_tracing() -> None:
    """Disable tracing."""
    _config["enabled"] = False
