"""
Enterprise Monitoring Module for ALACTIC AGI Framework
=====================================================

This module provides comprehensive monitoring, metrics collection, and observability
features for production deployments.
"""

import time
import psutil
import threading
from collections import defaultdict, deque
from typing import Dict, Any, Optional, List, Callable
import logging
from functools import wraps
import json

try:
    from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server, CollectorRegistry, CONTENT_TYPE_LATEST, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Create mock classes for graceful degradation
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
        def time(self): return MockContextManager()
    
    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    
    class Info:
        def __init__(self, *args, **kwargs): pass
        def info(self, *args, **kwargs): pass
    
    class MockContextManager:
        def __enter__(self): return self
        def __exit__(self, *args): pass
    
    def start_http_server(*args, **kwargs): pass

class MetricsCollector:
    """
    Enterprise-grade metrics collection system with Prometheus integration.
    
    Collects business metrics, performance data, and system health indicators
    for production monitoring and alerting.
    """
    
    def __init__(self, registry=None):
        """Initialize metrics collector with optional custom registry."""
        self.registry = registry or (CollectorRegistry() if PROMETHEUS_AVAILABLE else None)
        self.enabled = PROMETHEUS_AVAILABLE
        self._init_metrics()
        
    def _init_metrics(self):
        """Initialize Prometheus metrics."""
        if not self.enabled:
            return
            
        # Business metrics
        self.query_counter = Counter(
            'alactic_queries_total',
            'Total number of queries processed',
            ['query_type', 'status'],
            registry=self.registry
        )
        
        self.document_counter = Counter(
            'alactic_documents_processed_total',
            'Total number of documents processed',
            ['source', 'status'],
            registry=self.registry
        )
        
        # Performance metrics
        self.query_duration = Histogram(
            'alactic_query_duration_seconds',
            'Time spent processing queries',
            ['query_type'],
            registry=self.registry
        )
        
        self.api_response_time = Histogram(
            'alactic_api_response_time_seconds',
            'API response time',
            ['endpoint', 'method'],
            registry=self.registry
        )
        
        # System metrics
        self.system_cpu = Gauge(
            'alactic_system_cpu_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory = Gauge(
            'alactic_system_memory_percent',
            'System memory usage percentage',
            registry=self.registry
        )
        
        self.processing_queue_size = Gauge(
            'alactic_processing_queue_size',
            'Current processing queue size',
            registry=self.registry
        )
        
        # Error tracking
        self.error_counter = Counter(
            'alactic_errors_total',
            'Total number of errors',
            ['component', 'error_type'],
            registry=self.registry
        )
        
        # Framework info
        self.framework_info = Info(
            'alactic_framework_info',
            'ALACTIC AGI Framework information',
            registry=self.registry
        )
        
        self.framework_info.info({
            'version': '1.0.0',
            'company': 'Alactic Inc.',
            'author': 'Yash Parashar'
        })
    
    def record_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Record a counter metric."""
        if not self.enabled:
            return
            
        labels = labels or {}
        
        if name == 'queries':
            self.query_counter.labels(**labels).inc(value)
        elif name == 'documents_processed':
            self.document_counter.labels(**labels).inc(value)
        elif name == 'errors':
            self.error_counter.labels(**labels).inc(value)
    
    def record_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a gauge metric."""
        if not self.enabled:
            return
            
        labels = labels or {}
        
        if name == 'system_cpu':
            self.system_cpu.set(value)
        elif name == 'system_memory':
            self.system_memory.set(value)
        elif name == 'processing_queue_size':
            self.processing_queue_size.set(value)
    
    def record_timer(self, name: str, duration: float, labels: Optional[Dict[str, str]] = None):
        """Record a timing metric."""
        if not self.enabled:
            return
            
        labels = labels or {}
        
        if name == 'query_duration':
            self.query_duration.labels(**labels).observe(duration)
        elif name == 'api_response_time':
            self.api_response_time.labels(**labels).observe(duration)
    
    def get_metrics(self) -> str:
        """Get Prometheus-formatted metrics."""
        if not self.enabled or not self.registry:
            return "# Metrics not available\n"
        return generate_latest(self.registry).decode('utf-8')

class PerformanceProfiler:
    """
    Performance profiling and analysis tool for identifying bottlenecks
    and optimizing system performance.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        """Initialize performance profiler."""
        self.metrics = metrics_collector
        self.profiles = defaultdict(list)
        self.active_profiles = {}
    
    def profile_operation(self, operation_name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager for profiling operations."""
        return ProfileContext(self, operation_name, labels)
    
    def start_profile(self, operation_name: str, labels: Optional[Dict[str, str]] = None):
        """Start profiling an operation."""
        profile_id = f"{operation_name}_{time.time()}"
        self.active_profiles[profile_id] = {
            'name': operation_name,
            'start_time': time.time(),
            'start_memory': psutil.Process().memory_info().rss,
            'labels': labels or {}
        }
        return profile_id
    
    def end_profile(self, profile_id: str):
        """End profiling an operation."""
        if profile_id not in self.active_profiles:
            return
        
        profile = self.active_profiles.pop(profile_id)
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        duration = end_time - profile['start_time']
        memory_delta = end_memory - profile['start_memory']
        
        profile_data = {
            'operation': profile['name'],
            'duration': duration,
            'memory_delta': memory_delta,
            'labels': profile['labels'],
            'timestamp': end_time
        }
        
        self.profiles[profile['name']].append(profile_data)
        
        # Record metrics
        if self.metrics:
            self.metrics.record_timer('operation_duration', duration, profile['labels'])
    
    def get_profile_summary(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance profile summary."""
        if operation_name:
            profiles = self.profiles.get(operation_name, [])
        else:
            profiles = []
            for op_profiles in self.profiles.values():
                profiles.extend(op_profiles)
        
        if not profiles:
            return {"message": "No profile data available"}
        
        durations = [p['duration'] for p in profiles]
        memory_deltas = [p['memory_delta'] for p in profiles]
        
        return {
            'total_operations': len(profiles),
            'average_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'average_memory_delta': sum(memory_deltas) / len(memory_deltas),
            'operations': profiles[-10:]  # Last 10 operations
        }

class ProfileContext:
    """Context manager for performance profiling."""
    
    def __init__(self, profiler: PerformanceProfiler, operation_name: str, labels: Optional[Dict[str, str]] = None):
        self.profiler = profiler
        self.operation_name = operation_name
        self.labels = labels
        self.profile_id = None
    
    def __enter__(self):
        self.profile_id = self.profiler.start_profile(self.operation_name, self.labels)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.profile_id:
            self.profiler.end_profile(self.profile_id)

class AlertManager:
    """
    Alert management system for monitoring critical conditions
    and triggering notifications.
    """
    
    def __init__(self):
        """Initialize alert manager."""
        self.alerts = deque(maxlen=1000)  # Keep last 1000 alerts
        self.alert_handlers = {}
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'error_rate': 0.05,
            'response_time': 5.0
        }
    
    def register_handler(self, alert_type: str, handler: Callable):
        """Register an alert handler function."""
        self.alert_handlers[alert_type] = handler
    
    def check_thresholds(self, metrics: Dict[str, float]):
        """Check metrics against thresholds and trigger alerts."""
        for metric, value in metrics.items():
            threshold = self.thresholds.get(metric)
            if threshold and value > threshold:
                self.trigger_alert(
                    alert_type='threshold_exceeded',
                    message=f"{metric} exceeded threshold: {value} > {threshold}",
                    severity='warning',
                    metadata={'metric': metric, 'value': value, 'threshold': threshold}
                )
    
    def trigger_alert(self, alert_type: str, message: str, severity: str = 'info', metadata: Optional[Dict] = None):
        """Trigger an alert."""
        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': time.time(),
            'metadata': metadata or {}
        }
        
        self.alerts.append(alert)
        
        # Call registered handler
        handler = self.alert_handlers.get(alert_type)
        if handler:
            try:
                handler(alert)
            except Exception as e:
                logging.error(f"Alert handler error: {e}")
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        return list(self.alerts)[-count:]

class MonitoringDashboard:
    """
    Simple monitoring dashboard for displaying system status and metrics.
    """
    
    def __init__(self, metrics_collector: MetricsCollector, alert_manager: AlertManager):
        """Initialize monitoring dashboard."""
        self.metrics = metrics_collector
        self.alerts = alert_manager
        self.system_stats = deque(maxlen=100)  # Keep last 100 readings
        self._update_system_stats()
    
    def _update_system_stats(self):
        """Update system statistics."""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        stats = {
            'timestamp': time.time(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available': memory.available,
            'disk_percent': disk.percent,
            'disk_free': disk.free
        }
        
        self.system_stats.append(stats)
        
        # Update metrics
        if self.metrics:
            self.metrics.record_gauge('system_cpu', cpu_percent)
            self.metrics.record_gauge('system_memory', memory.percent)
        
        # Check thresholds
        self.alerts.check_thresholds({
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent
        })
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for display."""
        self._update_system_stats()
        
        current_stats = self.system_stats[-1] if self.system_stats else {}
        recent_alerts = self.alerts.get_recent_alerts(5)
        
        return {
            'system': current_stats,
            'alerts': recent_alerts,
            'status': 'healthy' if current_stats.get('cpu_percent', 0) < 80 else 'warning',
            'uptime': time.time(),  # Simplified uptime
            'version': '1.0.0'
        }

def timed(operation_name: Optional[str] = None):
    """
    Decorator for automatically timing function execution.
    
    Args:
        operation_name: Name of the operation for metrics
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                op_name = operation_name or func.__name__
                logging.info(f"Operation '{op_name}' completed in {duration:.3f} seconds")
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                op_name = operation_name or func.__name__
                logging.info(f"Async operation '{op_name}' completed in {duration:.3f} seconds")
        
        return async_wrapper if hasattr(func, '__code__') and 'async' in str(func.__code__) else wrapper
    return decorator

def get_monitoring_stack(port: int = 8080) -> tuple:
    """
    Get a complete monitoring stack with all components initialized.
    
    Args:
        port: Port for Prometheus metrics server
        
    Returns:
        Tuple of (metrics_collector, alert_manager, profiler, dashboard)
    """
    metrics = MetricsCollector()
    alerts = AlertManager()
    profiler = PerformanceProfiler(metrics)
    dashboard = MonitoringDashboard(metrics, alerts)
    
    # Start metrics server
    if PROMETHEUS_AVAILABLE:
        try:
            start_http_server(port, registry=metrics.registry)
            logging.info(f"Prometheus metrics server started on port {port}")
        except Exception as e:
            logging.warning(f"Failed to start metrics server: {e}")
    
    return metrics, alerts, profiler, dashboard

def start_monitoring(port: int = 8080):
    """Start the monitoring system as a standalone service."""
    metrics, alerts, profiler, dashboard = get_monitoring_stack(port)
    
    print(f"🚀 ALACTIC AGI Monitoring System Started")
    print(f"📊 Metrics available at: http://localhost:{port}/metrics")
    print(f"📈 Dashboard available at: http://localhost:{port}/")
    print(f"✅ All monitoring components initialized")
    
    # Keep the service running
    try:
        while True:
            time.sleep(60)  # Update every minute
            dashboard._update_system_stats()
    except KeyboardInterrupt:
        print("🛑 Monitoring system stopped")

if __name__ == "__main__":
    start_monitoring()