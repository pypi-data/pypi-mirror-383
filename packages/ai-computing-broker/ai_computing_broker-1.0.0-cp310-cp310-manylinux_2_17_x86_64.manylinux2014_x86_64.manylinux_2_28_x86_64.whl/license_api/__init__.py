"""
License API Package for GPU resource management.

This package provides license validation and GPU resource allocation
for gRPC services through AWS SQS and Lambda integration.
"""

from .exceptions import (
    HeartbeatFailedException,
    HTTPOperationException,
    LicenseException,
    ResourceNotAvailableException,
    SessionExpiredException,
    SQSOperationException,
)
from .manager import LicenseManager
from .models import GPUSpec, LicenseResponse

__version__ = "0.1.0"
__all__ = [
    "LicenseManager",
    "GPUSpec",
    "LicenseResponse",
    "LicenseException",
    "ResourceNotAvailableException",
    "SessionExpiredException",
    "HeartbeatFailedException",
    "HTTPOperationException",
    "SQSOperationException",
]
