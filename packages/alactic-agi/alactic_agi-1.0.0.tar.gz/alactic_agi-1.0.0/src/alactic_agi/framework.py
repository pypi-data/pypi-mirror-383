"""
ALACTIC AGI Framework - Legacy Compatibility Module
=================================================

This module provides compatibility with the original alactic_framework.py
and serves as the main framework interface.
"""

from .core import AlacticAGI, Crawler, Cleaner, Indexer, AsyncRetriever, AsyncAPIClient
from .monitoring import MetricsCollector, PerformanceProfiler, MonitoringDashboard, AlertManager
from .__version__ import __version__

# Legacy compatibility
AlacticFramework = AlacticAGI

# Export all main classes for backward compatibility
__all__ = [
    'AlacticAGI',
    'AlacticFramework',
    'Crawler',
    'Cleaner', 
    'Indexer',
    'AsyncRetriever',
    'AsyncAPIClient',
    'MetricsCollector',
    'PerformanceProfiler',
    'MonitoringDashboard',
    'AlertManager'
]