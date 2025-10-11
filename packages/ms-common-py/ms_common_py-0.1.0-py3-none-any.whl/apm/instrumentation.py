import logging
import traceback
from enum import Enum
from functools import wraps
from typing import Callable, Type, Optional, Any, Dict

from .const import APMConfig
from .exceptions import ServiceException

LOG = logging.getLogger(__name__)

def _get_tracer():
    cfg = APMConfig.get(refresh=True)
    if not (cfg.enabled and cfg.is_datadog):
        return None
    try:
        from ddtrace import tracer  # lazy import
        return tracer
    except ImportError:
        LOG.debug("ddtrace not installed; skipping tracing")
        return None



class ServiceType(Enum):
    CONSUMER = "consumer"
    CRON = "cron"
    DEFAULT = "service"
    API = "api"
    WORKER = "worker"
    SERVICE = "service"


class Instrumentation:
    @classmethod
    def _detect_service_type(cls, class_: Type) -> ServiceType:
        """Auto-detect service type based on class inheritance"""
        bases = [base.__name__ for base in class_.__mro__]
        if any(name in bases for name in ['BaseConsumer', 'Consumer']):
            return ServiceType.CONSUMER
        elif any(name in bases for name in ['BaseCommand', 'Command']):
            return ServiceType.CRON
        elif any(name in bases for name in ['APIView', 'ViewSet', 'Handler']):
            return ServiceType.API
        elif any(name in bases for name in ['Worker', 'Task']):
            return ServiceType.WORKER
        return ServiceType.DEFAULT

    @classmethod
    def trace(cls, name: Optional[str] = None, service: Optional[str] = None,
              handle_errors: bool = True, resource: Optional[str] = None,
              tags: Optional[Dict[str, Any]] = None):
        """
        Decorator to trace function execution

        Args:
            name: Span name (defaults to function name)
            service: Service name (defaults to DEFAULT_SERVICE_NAME)
            handle_errors: Whether to automatically handle exceptions
            resource: Resource name for the span
            tags: Additional tags to set on the span
        """

        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cfg = APMConfig.get(refresh=True)
                dd_tracer = _get_tracer()
                # Check if APM is enabled and is datadog
                if dd_tracer is None:
                    return func(*args, **kwargs)
                if service is None and cfg.service_name is None:
                    cfg = APMConfig.get(refresh=True)

                with dd_tracer.trace(
                        name=name or func.__name__,
                        service=service or cfg.service_name,
                        resource=resource
                ) as span:

                    if tags:
                        for key, value in tags.items():
                            span.set_tag(key, value)
                    # Set environment from apm_config
                    span.set_tag('env', cfg.environment)

                    try:
                        result = func(*args, **kwargs)
                        span.set_tag("success", True)
                        return result
                    except Exception as e:
                        span.set_tag("success", False)
                        if not isinstance(e, ServiceException) and handle_errors:
                            cls._set_error_tags(span, e)
                        raise

            return wrapper

        return decorator

    @classmethod
    def _set_error_tags(cls, span, exception: Exception):
        cfg = APMConfig.get(refresh=True)
        if not (cfg.enabled and cfg.is_datadog):
            return
        # Set error-related tags on span
        if span and cfg.is_datadog:
            span.set_tag('error', True)
            span.set_tag('error.type', exception.__class__.__name__)
            span.set_tag('error.message', str(exception))
            span.set_tag('error.stack', traceback.format_exc())

    @classmethod
    def _set_tag(cls, key: str, value):
        tracer = _get_tracer()
        if tracer and tracer.current_span():
            tracer.current_span().set_tag(key, value)

    @classmethod
    def _get_prefix(cls, prefix: Optional[str], class_name: str, service_type: ServiceType) -> str:
        # Generate the appropriate prefix based on service type
        if prefix:
            return prefix

        type_prefix_map = {
            ServiceType.CONSUMER: "Consumer",
            ServiceType.CRON: "Cron",
            ServiceType.API: "API",
            ServiceType.WORKER: "Worker",
            ServiceType.SERVICE: "Service"
        }

        return f"{type_prefix_map[service_type]}_{class_name}"

    @classmethod
    def instrument_class(cls, prefix: Optional[str] = None, service: Optional[str] = None,
                         exclude_methods: Optional[list] = None):
        """
        Class decorator to automatically instrument all public methods

        Args:
            prefix: Prefix for span names (auto-detected if None)
            service: Service name
            exclude_methods: List of method names to exclude from instrumentation
        """

        def decorator(class_):
            # Skip instrumentation if APM is disabled
            cfg = APMConfig.get(refresh=True)
            if not cfg.enabled:
                return class_

            service_type = cls._detect_service_type(class_)
            actual_prefix = cls._get_prefix(prefix, class_.__name__, service_type)
            excluded = exclude_methods or []

            for attr_name, attr_value in class_.__dict__.items():
                if (callable(attr_value) and
                        not attr_name.startswith('_') and
                        attr_name not in excluded):
                    instrumented_method = cls.trace(
                        name=f'{actual_prefix}_{attr_name}',
                        service=service or cfg.service_name,
                        tags={"class_name": class_.__name__, "service_type": service_type.value}
                    )(attr_value)

                    setattr(class_, attr_name, instrumented_method)
            return class_

        return decorator


# Convenience exports for common usage
trace = Instrumentation.trace
instrument_class = Instrumentation.instrument_class
