"""
OSDU Performance Testing Framework - Core Library
"""

from .core.base_service import BaseService
from .core.service_orchestrator import ServiceOrchestrator
from .core.input_handler import InputHandler
from .core.auth import AzureTokenManager
from .utils.environment import detect_environment
from .core.init_runner  import InitRunner

try:
    from .client_base.user_base import PerformanceUser
except ImportError:
    # Locust not available, skip import
    PerformanceUser = None

__version__ = "1.0.16"
__author__ = "Janraj CJ"
__email__ = "janrajcj@microsoft.com"

__all__ = [
    "InitRunner",
    "BaseService",
    "ServiceOrchestrator", 
    "InputHandler",
    "AzureTokenManager",
    "detect_environment"
]

# Add PerformanceUser to __all__ only if it was successfully imported
if PerformanceUser is not None:
    __all__.append("PerformanceUser")
