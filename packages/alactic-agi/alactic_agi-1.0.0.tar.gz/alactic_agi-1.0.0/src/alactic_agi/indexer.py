"""
Data Indexer Module for ALACTIC AGI Framework
============================================

This module provides data indexing capabilities for Apache Solr.
"""

from .core import Indexer as CoreIndexer
from pysolr import Solr
import json
import logging
from typing import List, Dict, Any, Optional

class SolrIndexer(CoreIndexer):
    """Enhanced Solr indexer with additional features."""
    
    def __init__(self, index_script: str, solr: Solr, **kwargs):
        super().__init__(index_script, solr)
        self.batch_size = kwargs.get('batch_size', 100)
        self.commit_within = kwargs.get('commit_within', 5000)
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Index a list of documents directly."""
        try:
            self.solr.add(documents, commit=True, commitWithin=self.commit_within)
            logging.info(f"Indexed {len(documents)} documents successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to index documents: {e}")
            return False
    
    def delete_all(self) -> bool:
        """Delete all documents from the index."""
        try:
            self.solr.delete(q='*:*')
            self.solr.commit()
            logging.info("All documents deleted from index")
            return True
        except Exception as e:
            logging.error(f"Failed to delete documents: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            response = self.solr.search('*:*', rows=0)
            return {
                'total_documents': response.hits,
                'index_size': 'unknown'  # Would need additional Solr API calls
            }
        except Exception as e:
            logging.error(f"Failed to get index stats: {e}")
            return {'total_documents': 0, 'index_size': 'unknown'}

class DataIndexer:
    """Generic data indexer interface."""
    
    def __init__(self, backend: str = 'solr'):
        self.backend = backend
    
    def index(self, data: List[Dict[str, Any]]) -> bool:
        """Index data using the specified backend."""
        # Implementation would depend on backend
        return True

# Legacy compatibility
__all__ = ['SolrIndexer', 'DataIndexer']