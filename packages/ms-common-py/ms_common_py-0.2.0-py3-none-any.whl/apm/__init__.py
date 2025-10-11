"""
MS Common Python APM Library

A comprehensive Application Performance Monitoring (APM) and instrumentation library
for Python microservices at FinAccel.
"""

from .instrumentation import trace, instrument_class, Instrumentation, ServiceType
from .const import APMConfig, APMProvider, ResponseMessageList
from .exceptions import (
    ServiceException,
    AuthenticationFailure,
    ForbiddenException,
    BadRequestException,
    MissingParamException,
    InternalServerError,
    ValidateException,
    ProductClosedException,
    BusinessException,
    RequestFailure,
    NotFoundException,
    HTTPMethodException,
    BillNotValidException,
)

__version__ = "0.2.0"

__all__ = [
    # Main instrumentation functions
    "trace",
    "instrument_class",
    "Instrumentation",
    "ServiceType",
    
    # Configuration
    "APMConfig",
    "APMProvider",
    "ResponseMessageList",
    
    # Exceptions
    "ServiceException",
    "AuthenticationFailure",
    "ForbiddenException",
    "BadRequestException",
    "MissingParamException",
    "InternalServerError",
    "ValidateException",
    "ProductClosedException",
    "BusinessException",
    "RequestFailure",
    "NotFoundException",
    "HTTPMethodException",
    "BillNotValidException",
]