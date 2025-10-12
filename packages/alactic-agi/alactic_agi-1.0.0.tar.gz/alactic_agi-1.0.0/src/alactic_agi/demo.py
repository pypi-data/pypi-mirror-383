"""
Demo Module for ALACTIC AGI Framework
====================================

This module provides demonstration capabilities for the framework.
"""

import asyncio
import time
from .core import AlacticAGI
from .monitoring import get_monitoring_stack
from .__version__ import __version__

def run_demo():
    """Run a comprehensive demonstration of the ALACTIC AGI framework."""
    print(f"🎯 ALACTIC AGI Framework Demo v{__version__}")
    print("=" * 50)
    
    # Start monitoring
    print("📊 Initializing monitoring system...")
    metrics, alerts, profiler, dashboard = get_monitoring_stack(8081)
    
    # Initialize framework
    print("🚀 Initializing ALACTIC AGI Framework...")
    agi = AlacticAGI()
    
    # Demo pipeline
    async def demo_pipeline():
        demo_queries = [
            "artificial intelligence research",
            "machine learning datasets", 
            "natural language processing",
            "computer vision benchmarks"
        ]
        
        print(f"\n🔍 Running {len(demo_queries)} demonstration queries...")
        print("-" * 40)
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n{i}. Processing: '{query}'")
            
            try:
                start_time = time.time()
                solr_docs, api_result = await agi.run_pipeline(query)
                duration = time.time() - start_time
                
                print(f"   ✅ Completed in {duration:.2f}s")
                print(f"   📄 Documents found: {len(solr_docs)}")
                print(f"   🎯 API response length: {len(api_result.get('answer', ''))}")
                
                # Record demo metrics
                if metrics:
                    metrics.record_counter('demo_queries', 1, {'status': 'success'})
                    metrics.record_timer('demo_query_duration', duration)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                if metrics:
                    metrics.record_counter('demo_queries', 1, {'status': 'error'})
        
        # Show system status
        print(f"\n📊 System Performance Summary:")
        print("-" * 30)
        
        dashboard_data = dashboard.get_dashboard_data()
        system_stats = dashboard_data.get('system', {})
        
        print(f"CPU Usage: {system_stats.get('cpu_percent', 0):.1f}%")
        print(f"Memory Usage: {system_stats.get('memory_percent', 0):.1f}%")
        print(f"System Status: {dashboard_data.get('status', 'unknown')}")
        
        # Show alerts if any
        alerts_list = dashboard_data.get('alerts', [])
        if alerts_list:
            print(f"\n🚨 Recent Alerts: {len(alerts_list)}")
            for alert in alerts_list[-3:]:  # Show last 3
                print(f"   - {alert.get('message', 'Unknown alert')}")
        else:
            print(f"\n✅ No active alerts")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"📈 Monitoring available at: http://localhost:8081/metrics")
        print(f"📊 Framework ready for production use")
    
    # Run the demo
    try:
        asyncio.run(demo_pipeline())
    except KeyboardInterrupt:
        print(f"\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == "__main__":
    run_demo()