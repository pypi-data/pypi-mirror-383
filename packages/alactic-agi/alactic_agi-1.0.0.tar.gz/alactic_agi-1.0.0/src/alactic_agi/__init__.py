"""
ALACTIC AGI Framework
===================

Enterprise AI Dataset Processing Platform

A production-ready framework for scalable data acquisition, validation, and structuring 
with enterprise-grade monitoring and observability.

Key Features:
- Automated data acquisition with web-scale scraping
- Intelligent data validation and quality scoring
- Structured data output in multiple formats
- Enterprise monitoring with Prometheus + Grafana
- Production scalability for 100M+ sources
- Docker orchestration and cloud deployment

Example Usage:
    >>> from alactic_agi import AlacticAGI
    >>> agi = AlacticAGI()
    >>> results = agi.run_pipeline("machine learning datasets")
    >>> print(f"Found {len(results)} datasets")

For more information, visit: https://www.alacticai.com
Documentation: https://docs.alacticai.com
"""

# Import core classes with error handling for missing dependencies
try:
    from .core import AlacticAGI
    from .framework import AlacticFramework
    from .monitoring import MetricsCollector, PerformanceProfiler, MonitoringDashboard
    from .crawler import DataCrawler, SourceSpider
    from .indexer import SolrIndexer, DataIndexer
    from .validator import DataValidator, QualityScorer
    from .__version__ import __version__, __title__, __author__, __license__
except ImportError as e:
    # Graceful degradation if dependencies are missing
    import warnings
    warnings.warn(f"Some ALACTIC AGI components may not be available: {e}")
    
    # Provide minimal interface
    __version__ = "1.0.0"
    __title__ = "ALACTIC AGI Framework"
    __author__ = "Yash Parashar"
    __license__ = "MIT"

# Package metadata
__all__ = [
    # Core classes
    "AlacticAGI",
    "AlacticFramework",
    
    # Monitoring components
    "MetricsCollector", 
    "PerformanceProfiler", 
    "MonitoringDashboard",
    
    # Data processing
    "DataCrawler",
    "SourceSpider", 
    "SolrIndexer",
    "DataIndexer",
    "DataValidator",
    "QualityScorer",
    
    # Package info
    "__version__",
    "__title__",
    "__author__",
    "__license__"
]

# Package version and metadata
__package_name__ = "alactic-agi"
__package_url__ = "https://github.com/AlacticAI/alactic-agi"
__company__ = "Alactic Inc."
__support_email__ = "support@alacticai.com"

# Default configuration
DEFAULT_CONFIG = {
    "debug": False,
    "log_level": "INFO",
    "max_workers": 4,
    "solr_url": "http://localhost:8983/solr/super_rag",
    "monitoring_enabled": True,
    "prometheus_port": 8080
}

def get_version():
    """Return the current version of the package."""
    return __version__

def get_config():
    """Return the default configuration dictionary."""
    return DEFAULT_CONFIG.copy()

def health_check():
    """
    Perform a basic health check of the framework components.
    
    Returns:
        dict: Health status of each component
    """
    try:
        from .core import AlacticAGI
        agi = AlacticAGI()
        return agi.get_health_status()
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "components": {
                "core": "unknown",
                "monitoring": "unknown",
                "indexer": "unknown"
            }
        }

# Framework initialization message
def _display_startup_info():
    """Display framework startup information."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        startup_text = f"""
[bold blue]ALACTIC AGI Framework v{__version__}[/bold blue]
[cyan]Enterprise AI Dataset Processing Platform[/cyan]

[green]✓[/green] Framework initialized successfully
[green]✓[/green] Monitoring components loaded
[green]✓[/green] Ready for data processing

[dim]Company: {__company__}
Support: {__support_email__}
Documentation: https://docs.alacticai.com[/dim]
        """
        
        console.print(Panel.fit(startup_text, title="🚀 ALACTIC AGI", border_style="blue"))
    except ImportError:
        # Fallback if rich is not available
        print(f"ALACTIC AGI Framework v{__version__} - Enterprise AI Dataset Processing Platform")
        print(f"Company: {__company__} | Support: {__support_email__}")

# Display startup info when package is imported (optional)
# _display_startup_info()