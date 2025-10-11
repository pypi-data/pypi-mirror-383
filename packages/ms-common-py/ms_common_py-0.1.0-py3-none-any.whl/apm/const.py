import logging
import os
import threading
from enum import Enum
from typing import Optional

LOG = logging.getLogger(__name__)


class APMProvider(str, Enum):
    DATADOG = "datadog"
    NONE = "none"
    # Future providers can be added here
    # NEW_RELIC = "newrelic"

APM_VERSION_DEFAULT = "1.0.0"


_ENV_KEYS = [
    "APM_PROVIDER",
    "DD_SERVICE",
    "DD_ENV",
    "APM_VERSION",
    "DD_APM_ENABLED",
]

class ResponseMessageList():
    OK = 'OK'
    ERROR = 'ERROR'


# Configuration from environment variables
APM_VERSION = os.getenv("APM_VERSION", "1.0.0")
DEFAULT_SERVICE_NAME = os.getenv("DD_SERVICE", "datadog")
# Datadog specific configuration
DATADOG_AGENT_HOST = os.getenv("DD_AGENT_HOST", "localhost")
DATADOG_TRACE_AGENT_PORT = int(os.getenv("DD_TRACE_AGENT_PORT", "8126"))


class APMConfig:
    """
    Thread-safe lazy singleton accessed only via:
        cfg = APMConfig.get()
    Refresh logic:
        APMConfig.get(refresh=True)  # reload only if env changed
        APMConfig.get(force=True)    # always reload
        APMConfig.refresh()          # alias for force refresh
    """

    _lock = threading.RLock()
    _instance: "APMConfig | None" = None

    def __init__(self):
        # Instance fields
        self.provider: Optional[str] = None
        self.service_name: Optional[str] = None
        self.environment: Optional[str] = None
        self.version: Optional[str] = None
        self.enabled: bool = False
        self._fingerprint = None
        # Initial load
        self._load()

    # -------- Public class API (singleton access) --------
    @classmethod
    def get(cls, refresh: bool = False, force: bool = False) -> "APMConfig":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
                LOG.debug("APMConfig created: service=%s provider=%s env=%s enabled=%s",
                          cls._instance.service_name, cls._instance.provider,
                          cls._instance.environment, cls._instance.enabled)
                return cls._instance

            if force:
                cls._instance._load()
                LOG.debug("APMConfig force reloaded")
            elif refresh and (cls._instance.service_name is None or cls._instance._needs_refresh()):
                cls._instance._load()
                LOG.debug("APMConfig auto reload (environment change detected)")
            return cls._instance

    @classmethod
    def refresh(cls) -> "APMConfig":
        """Explicit force refresh."""
        return cls.get(force=True)

    # -------- Instance helpers --------
    def _load(self):
        self.provider = os.getenv("APM_PROVIDER", APMProvider.DATADOG.value)
        self.service_name = os.getenv("DD_SERVICE", "datadog")
        self.environment = os.getenv("DD_ENV", "development")
        self.version = os.getenv("APM_VERSION", APM_VERSION_DEFAULT)
        self.enabled = self._is_apm_enabled()
        self._fingerprint = self._compute_fingerprint()

    def _compute_fingerprint(self):
        return tuple((k, os.getenv(k)) for k in _ENV_KEYS)

    def _needs_refresh(self) -> bool:
        return self._fingerprint != self._compute_fingerprint()

    def _is_apm_enabled(self) -> bool:
        if self.provider == APMProvider.NONE.value:
            return False
        if self.provider == APMProvider.DATADOG.value:
            return os.getenv("DD_APM_ENABLED", "true").lower() == "true"
        return True

    @property
    def is_datadog(self) -> bool:
        return self.provider == APMProvider.DATADOG.value


__all__ = [
    "APMProvider",
    "APMConfig",
    "ResponseMessageList",
]



