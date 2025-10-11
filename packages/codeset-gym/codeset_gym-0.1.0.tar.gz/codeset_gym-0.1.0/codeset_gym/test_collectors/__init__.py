"""Test result collectors for different programming languages."""

# Container-based collectors (backward compatibility)
from .factory import TestResultCollectorFactory

# Core collectors (container-agnostic)
from .core_factory import CoreTestResultCollectorFactory
from .core_collector import CoreTestResultCollector

# Container adapter
from .collector import TestResultCollector

__all__ = [
    # Backward compatibility - container-based
    "TestResultCollectorFactory",

    # Core - container-agnostic
    "CoreTestResultCollectorFactory",
    "CoreTestResultCollector",

    # Container adapter
    "TestResultCollector",
]