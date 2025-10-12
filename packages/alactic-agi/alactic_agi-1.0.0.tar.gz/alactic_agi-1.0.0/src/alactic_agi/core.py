"""
Core ALACTIC AGI Framework Module
================================

This module contains the main AlacticAGI class and core framework functionality.
"""

from pysolr import Solr
import subprocess
import json
import logging
import configparser
import os
from abc import ABC, abstractmethod
import asyncio
import aiohttp
from cachetools import TTLCache
import pandas as pd
import time
from typing import Dict, List, Optional, Any, Union

# Import monitoring system
try:
    from .monitoring import get_monitoring_stack, timed, PerformanceProfiler
    MONITORING_ENABLED = True
except ImportError:
    # Fallback if monitoring dependencies not available
    MONITORING_ENABLED = False
    def timed(operation_name: Optional[str] = None):
        def decorator(func):
            return func
        return decorator

# Setup logging
logging.basicConfig(
    filename='alactic_agi.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Component(ABC):
    """Abstract base class for framework components."""
    
    @abstractmethod
    def run(self) -> bool:
        """Abstract method to execute the component."""
        pass

class Crawler(Component):
    """Web crawler component for data acquisition."""
    
    def __init__(self, crawler_path: str, output_file: str):
        self.crawler_path = crawler_path
        self.output_file = output_file

    def run(self) -> bool:
        """Execute the web crawler."""
        logging.info("Starting crawler...")
        print("Running crawler...")
        try:
            spider_rel_path = os.path.join('spiders', 'source_spider.py')
            spider_file = os.path.join(self.crawler_path, spider_rel_path)
            
            if not os.path.exists(spider_file):
                print(f"Spider file not found: {spider_file}")
                logging.error(f"Spider file not found: {spider_file}")
                return False
            
            # Find scrapy executable
            scrapy_cmd = self._find_scrapy_executable()
            if not scrapy_cmd:
                print("Scrapy executable not found. Please ensure Scrapy is installed.")
                logging.error("Scrapy executable not found.")
                return False
            
            print(f"Using Scrapy at: {scrapy_cmd}")
            
            # Build command list
            if isinstance(scrapy_cmd, list):
                cmd = scrapy_cmd + ['runspider', spider_rel_path, '-o', self.output_file]
            else:
                cmd = [scrapy_cmd, 'runspider', spider_rel_path, '-o', self.output_file]
                
            result = subprocess.run(cmd, cwd=self.crawler_path, capture_output=True, text=True)
            if result.returncode == 0:
                print("Crawler completed successfully.")
                logging.info("Crawler completed successfully.")
            else:
                print(f"Crawler failed with code {result.returncode}. Error: {result.stderr}")
                logging.error(f"Crawler failed with code {result.returncode}. Error: {result.stderr}")
            return result.returncode == 0
        except Exception as e:
            print(f"Crawler exception: {e}")
            logging.error(f"Crawler exception: {e}")
            return False

    def _find_scrapy_executable(self) -> Optional[Union[str, List[str]]]:
        """Find the scrapy executable in various common locations."""
        import shutil
        import sys
        
        # Try to find scrapy in PATH first
        scrapy_cmd = shutil.which('scrapy')
        if scrapy_cmd:
            return scrapy_cmd
        
        # Try Python module execution
        try:
            result = subprocess.run([sys.executable, '-m', 'scrapy', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return [sys.executable, '-m', 'scrapy']
        except Exception:
            pass
        
        return None

class Cleaner(Component):
    """Data cleaning component."""
    
    def __init__(self, clean_script: str):
        self.clean_script = clean_script

    def run(self) -> bool:
        """Execute the data cleaner."""
        logging.info("Starting cleaner...")
        print("Running cleaner...")
        try:
            result = subprocess.run(['python', self.clean_script], 
                                  cwd=os.path.dirname(self.clean_script), 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logging.info("Cleaner completed successfully.")
                print("Cleaner completed successfully.")
            else:
                logging.error(f"Cleaner failed with code {result.returncode}. Error: {result.stderr}")
                print(f"Cleaner failed with code {result.returncode}. Error: {result.stderr}")
                return False
            return True
        except Exception as e:
            logging.error(f"Cleaner error: {e}")
            print(f"Cleaner error: {e}")
            return False

class Indexer(Component):
    """Data indexing component for Solr."""
    
    def __init__(self, index_script: str, solr: Solr):
        self.index_script = index_script
        self.solr = solr

    def run(self) -> bool:
        """Execute the data indexer."""
        logging.info("Starting indexer...")
        print("Running indexer...")
        try:
            result = subprocess.run(['python', self.index_script], 
                                  cwd=os.path.dirname(self.index_script), 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logging.info("Indexer completed successfully.")
                print("Indexer completed successfully.")
            else:
                logging.error(f"Indexer failed with code {result.returncode}. Error: {result.stderr}")
                print(f"Indexer failed with code {result.returncode}. Error: {result.stderr}")
                return False
            return True
        except Exception as e:
            logging.error(f"Indexer error: {e}")
            print(f"Indexer error: {e}")
            return False

class Retriever(ABC):
    """Abstract base class for data retrieval."""
    
    def __init__(self, solr: Solr):
        self.solr = solr
        self.cache = TTLCache(maxsize=100, ttl=300)

    @abstractmethod
    async def query(self, query: str, rows: int = 10) -> List[Dict[str, Any]]:
        """Asynchronous method to query the retrieval system."""
        pass

class AsyncRetriever(Retriever):
    """Asynchronous data retriever with caching."""
    
    async def query(self, query: str, rows: int = 10) -> List[Dict[str, Any]]:
        """Execute asynchronous query with caching."""
        cache_key = f"{query}:{rows}"
        if cache_key in self.cache:
            logging.info(f"Cache hit for query: {query}")
            return self.cache[cache_key]
            
        logging.info(f"Querying Solr asynchronously for: {query}")
        print(f"Querying Solr asynchronously for: {query}")
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, 
            lambda: self.solr.search(
                f"id:*{query}* OR content:*{query}* OR text:*{query}*", 
                rows=rows
            )
        )
        
        docs = [
            {
                'id': doc['id'], 
                'text': doc.get('text', [doc.get('content', ['No content'])[0]])[0]
            } 
            for doc in results.docs
        ]
        
        unique_docs = {doc['id']: doc for doc in docs}.values()
        self.cache[cache_key] = list(unique_docs)
        return self.cache[cache_key]

class APIClient(ABC):
    """Abstract base class for API clients."""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.cache = TTLCache(maxsize=100, ttl=300)

    @abstractmethod
    async def query(self, query: str) -> Dict[str, Any]:
        """Asynchronous method to query the API."""
        pass

class AsyncAPIClient(APIClient):
    """Asynchronous API client with caching."""
    
    async def query(self, query: str) -> Dict[str, Any]:
        """Execute asynchronous API query with caching."""
        cache_key = query
        if cache_key in self.cache:
            logging.info(f"Cache hit for API query: {query}")
            return self.cache[cache_key]
            
        logging.info(f"Sending API query asynchronously for: {query}")
        print(f"Sending API query asynchronously for: {query}")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.api_url, 
                    json={'query': query}, 
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    unique_sources = list(dict.fromkeys(result.get('sources', [])))
                    result['sources'] = unique_sources
                    self.cache[cache_key] = result
                    return result
            except Exception as e:
                logging.error(f"API query error: {e}")
                print(f"API query error: {e}")
                return {"answer": "API query failed", "sources": []}

class AlacticAGI:
    """
    Main ALACTIC AGI Framework class for enterprise AI dataset processing.
    
    This class orchestrates the complete pipeline including web crawling,
    data cleaning, indexing, and retrieval with enterprise monitoring.
    """
    
    def __init__(self, config_file: str = 'config.ini', retriever_type: str = 'async'):
        """
        Initialize the ALACTIC AGI framework.
        
        Args:
            config_file: Path to configuration file
            retriever_type: Type of retriever ('async' or 'metadata')
        """
        config = configparser.ConfigParser()
        config.read(config_file)
        
        # Configuration
        self.solr_url = os.getenv('SOLR_URL', config.get('Solr', 'url', fallback='http://localhost:8983/solr/super_rag'))
        self.api_url = os.getenv('API_URL', config.get('API', 'url', fallback='http://localhost:3000/query'))
        self.crawler_path = os.path.join(os.getcwd(), 'crawler')
        self.output_file = os.path.join(os.getcwd(), 'data', 'samples', 'output.json')
        self.clean_script = os.path.join(os.getcwd(), 'indexer', 'scripts', 'clean_jsonl.py')
        self.index_script = os.path.join(os.getcwd(), 'indexer', 'scripts', 'index.py')
        
        # Initialize components
        self.solr = Solr(self.solr_url)
        self.crawler = Crawler(self.crawler_path, self.output_file)
        self.cleaner = Cleaner(self.clean_script)
        self.indexer = Indexer(self.index_script, self.solr)
        self.retriever = AsyncRetriever(self.solr)
        self.api_client = AsyncAPIClient(self.api_url)
        
        # Initialize monitoring
        if MONITORING_ENABLED:
            self.metrics, self.alerts, self.profiler, self.dashboard = get_monitoring_stack()
            self.metrics.record_counter("framework_initialized", 1, {"retriever_type": retriever_type})
        else:
            self.metrics = self.alerts = self.profiler = self.dashboard = None
        
        logging.info(f"ALACTIC AGI initialized with config from {config_file} and retriever {retriever_type}")

    @timed("pipeline_execution")
    async def run_pipeline(self, query: str) -> tuple:
        """
        Execute the complete data processing pipeline.
        
        Args:
            query: Search query for data acquisition
            
        Returns:
            Tuple of (solr_documents, api_results)
        """
        if MONITORING_ENABLED and self.metrics:
            self.metrics.record_counter("pipeline_started", 1)
        
        print("Pipeline: starting crawler...", flush=True)
        success = True
        
        # Execute pipeline stages
        if MONITORING_ENABLED and self.profiler:
            with self.profiler.profile_operation("crawler_execution"):
                success &= self.crawler.run()
        else:
            success &= self.crawler.run()
            
        print("Pipeline: starting cleaner...", flush=True)
        success &= self.cleaner.run()
        
        print("Pipeline: starting indexer...", flush=True)
        success &= self.indexer.run()
        
        print("Pipeline: querying Solr...", flush=True)
        solr_docs = await self.retriever.query(query)
        
        print("Pipeline: querying API...", flush=True)
        api_result = await self.api_client.query(query)
        
        # Log results
        evaluation_score = len(api_result.get('answer', '')) + len(api_result.get('sources', [])) * 10
        print(f"Evaluation Score: {evaluation_score}", flush=True)
        print(f"Retrieved {len(solr_docs)} unique documents from Solr", flush=True)
        print(f"API Response: {json.dumps(api_result, indent=2)}", flush=True)
        
        if success:
            logging.info("Pipeline completed successfully!")
            print("Pipeline completed successfully!", flush=True)
        else:
            logging.error("Pipeline failed in one or more steps.")
            print("Pipeline failed in one or more steps.", flush=True)
            
        return solr_docs, api_result

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of all components.
        
        Returns:
            Dictionary with health status of each component
        """
        status = {
            "status": "healthy",
            "components": {
                "solr": "unknown",
                "crawler": "operational",
                "indexer": "operational",
                "monitoring": "enabled" if MONITORING_ENABLED else "disabled"
            },
            "version": "1.0.0"
        }
        
        # Check Solr connectivity
        try:
            self.solr.ping()
            status["components"]["solr"] = "online"
        except Exception:
            status["components"]["solr"] = "offline"
            status["status"] = "degraded"
        
        return status

# Legacy compatibility - maintain the original class name
AlacticFramework = AlacticAGI

# Main execution for standalone use
if __name__ == "__main__":
    agi = AlacticAGI(retriever_type='async')
    asyncio.run(agi.run_pipeline("torch"))