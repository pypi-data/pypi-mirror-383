"""
Paylink Tracer SDK - Simple tracing for payment operations.

This SDK provides simple tracing for payment tools, automatically capturing
execution details and sending them to your Paylink API endpoint.
"""

from paylink_tracer.tracer import (
    paylink_tracer,
    configure,
    set_base_url,
    enable_tracing,
    disable_tracing,
)

__version__ = "0.1.5"
__all__ = [
    "paylink_tracer",
    "configure",
    "set_base_url",
    "enable_tracing",
    "disable_tracing",
]
