"""
Command Line Interface for ALACTIC AGI Framework
===============================================

This module provides CLI commands for the ALACTIC AGI framework.
"""

import click
import asyncio
import json
import sys
from typing import Optional
from .core import AlacticAGI
from .monitoring import start_monitoring, get_monitoring_stack
from .__version__ import __version__

@click.group()
@click.version_option(version=__version__, prog_name='ALACTIC AGI Framework')
@click.pass_context
def main(ctx):
    """
    ALACTIC AGI Framework - Enterprise AI Dataset Processing Platform
    
    A production-ready framework for scalable data acquisition, validation,
    and structuring with enterprise-grade monitoring.
    """
    ctx.ensure_object(dict)

@main.command()
@click.argument('query')
@click.option('--config', '-c', default='config.ini', help='Configuration file path')
@click.option('--retriever', '-r', default='async', type=click.Choice(['async', 'metadata']), 
              help='Retriever type')
@click.option('--output', '-o', help='Output file for results')
@click.option('--format', 'output_format', default='json', type=click.Choice(['json', 'csv']), 
              help='Output format')
def query(query: str, config: str, retriever: str, output: Optional[str], output_format: str):
    """Execute a query using the ALACTIC AGI pipeline."""
    click.echo(f"🚀 ALACTIC AGI Framework v{__version__}")
    click.echo(f"🔍 Processing query: {query}")
    
    try:
        # Initialize framework
        agi = AlacticAGI(config_file=config, retriever_type=retriever)
        
        # Run pipeline
        with click.progressbar(length=5, label='Processing pipeline') as bar:
            async def run_with_progress():
                bar.update(1)  # Crawler
                solr_docs, api_result = await agi.run_pipeline(query)
                bar.update(4)  # Complete
                return solr_docs, api_result
            
            solr_docs, api_result = asyncio.run(run_with_progress())
        
        # Format results
        results = {
            'query': query,
            'solr_documents': solr_docs,
            'api_result': api_result,
            'total_documents': len(solr_docs)
        }
        
        # Output results
        if output:
            if output_format == 'json':
                with open(output, 'w') as f:
                    json.dump(results, f, indent=2)
            elif output_format == 'csv':
                import pandas as pd
                df = pd.DataFrame(solr_docs)
                df.to_csv(output, index=False)
            click.echo(f"✅ Results saved to {output}")
        else:
            if output_format == 'json':
                click.echo(json.dumps(results, indent=2))
            else:
                click.echo(f"Found {len(solr_docs)} documents")
                for i, doc in enumerate(solr_docs[:10]):  # Show first 10
                    click.echo(f"{i+1}. {doc.get('id', 'N/A')}: {doc.get('text', 'N/A')[:100]}...")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@main.command()
@click.option('--port', '-p', default=8080, help='Port for monitoring server')
def monitor(port: int):
    """Start the monitoring system."""
    click.echo(f"🚀 Starting ALACTIC AGI Monitoring System on port {port}")
    click.echo("Press Ctrl+C to stop")
    
    try:
        start_monitoring(port)
    except KeyboardInterrupt:
        click.echo("\n🛑 Monitoring system stopped")

@main.command()
@click.option('--config', '-c', default='config.ini', help='Configuration file path')
def health(config: str):
    """Check system health."""
    click.echo("🏥 ALACTIC AGI Health Check")
    
    try:
        agi = AlacticAGI(config_file=config)
        status = agi.get_health_status()
        
        click.echo(f"Overall Status: {status['status']}")
        click.echo(f"Version: {status['version']}")
        click.echo("\nComponents:")
        
        for component, state in status['components'].items():
            icon = "✅" if state in ['online', 'operational', 'enabled'] else "❌"
            click.echo(f"  {icon} {component}: {state}")
        
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}", err=True)
        sys.exit(1)

@main.command()
@click.option('--config', '-c', default='config.ini', help='Configuration file path')
def demo(config: str):
    """Run a demonstration of the framework."""
    click.echo(f"🎯 ALACTIC AGI Framework Demo v{__version__}")
    click.echo("Running demonstration pipeline...")
    
    try:
        # Start monitoring in background
        click.echo("📊 Starting monitoring...")
        metrics, alerts, profiler, dashboard = get_monitoring_stack(8081)
        
        # Initialize framework
        agi = AlacticAGI(config_file=config)
        
        # Demo queries
        demo_queries = [
            "artificial intelligence",
            "machine learning datasets",
            "natural language processing"
        ]
        
        click.echo("\n🔍 Running demo queries...")
        for i, query in enumerate(demo_queries, 1):
            click.echo(f"\n{i}. Query: {query}")
            
            try:
                solr_docs, api_result = asyncio.run(agi.run_pipeline(query))
                click.echo(f"   ✅ Found {len(solr_docs)} documents")
                click.echo(f"   📄 API response: {api_result.get('answer', 'No answer')[:100]}...")
            except Exception as e:
                click.echo(f"   ❌ Error: {e}")
        
        # Show monitoring data
        dashboard_data = dashboard.get_dashboard_data()
        click.echo(f"\n📊 System Status: {dashboard_data['status']}")
        click.echo(f"💻 CPU: {dashboard_data['system'].get('cpu_percent', 0):.1f}%")
        click.echo(f"💾 Memory: {dashboard_data['system'].get('memory_percent', 0):.1f}%")
        
        click.echo(f"\n🎉 Demo completed! Monitoring available at http://localhost:8081/metrics")
        
    except Exception as e:
        click.echo(f"❌ Demo failed: {e}", err=True)
        sys.exit(1)

@main.command()
def info():
    """Show framework information."""
    click.echo(f"""
🚀 ALACTIC AGI Framework v{__version__}
=====================================

Enterprise AI Dataset Processing Platform

Company: Alactic Inc.
Author: Yash Parashar
Support: support@alacticai.com
Website: https://www.alacticai.com

Features:
✅ Automated data acquisition with web-scale scraping
✅ Intelligent data validation and quality scoring  
✅ Structured data output in multiple formats
✅ Enterprise monitoring with Prometheus + Grafana
✅ Production scalability for 100M+ sources
✅ Docker orchestration and cloud deployment

Documentation: https://docs.alacticai.com
Repository: https://github.com/AlacticAI/alactic-agi
""")

# Alias for monitoring
@main.command(name='start-monitoring')
@click.option('--port', '-p', default=8080, help='Port for monitoring server')
def start_monitoring_alias(port: int):
    """Start the monitoring system (alias for monitor)."""
    monitor.callback(port)

# Demo alias
@main.command(name='run-demo')
@click.option('--config', '-c', default='config.ini', help='Configuration file path')
def run_demo_alias(config: str):
    """Run a demonstration of the framework (alias for demo)."""
    demo.callback(config)

if __name__ == '__main__':
    main()