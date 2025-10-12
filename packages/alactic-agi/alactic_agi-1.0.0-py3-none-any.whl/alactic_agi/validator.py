"""
Data Validator Module for ALACTIC AGI Framework
==============================================

This module provides data validation and quality scoring capabilities.
"""

from typing import Dict, Any, List, Optional
import re
import logging
from abc import ABC, abstractmethod

class DataValidator:
    """Data validation system for quality assurance."""
    
    def __init__(self):
        self.rules = []
        self.stats = {'validated': 0, 'passed': 0, 'failed': 0}
    
    def add_rule(self, rule_func, description: str = ""):
        """Add a validation rule."""
        self.rules.append({'func': rule_func, 'description': description})
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single data item."""
        self.stats['validated'] += 1
        results = {'valid': True, 'errors': [], 'warnings': []}
        
        for rule in self.rules:
            try:
                result = rule['func'](data)
                if not result:
                    results['valid'] = False
                    results['errors'].append(rule['description'])
            except Exception as e:
                results['warnings'].append(f"Rule validation error: {e}")
        
        if results['valid']:
            self.stats['passed'] += 1
        else:
            self.stats['failed'] += 1
        
        return results
    
    def validate_batch(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate a batch of data items."""
        return [self.validate(item) for item in data_list]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        total = self.stats['validated']
        if total > 0:
            pass_rate = (self.stats['passed'] / total) * 100
        else:
            pass_rate = 0
        
        return {
            **self.stats,
            'pass_rate': pass_rate
        }

class QualityScorer:
    """Quality scoring system for data items."""
    
    def __init__(self):
        self.scoring_rules = []
        self.weights = {}
    
    def add_scoring_rule(self, rule_func, weight: float = 1.0, description: str = ""):
        """Add a quality scoring rule."""
        rule_id = len(self.scoring_rules)
        self.scoring_rules.append({
            'id': rule_id,
            'func': rule_func,
            'description': description
        })
        self.weights[rule_id] = weight
    
    def score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality score for a data item."""
        scores = {}
        weighted_sum = 0
        total_weight = 0
        
        for rule in self.scoring_rules:
            try:
                score = rule['func'](data)
                rule_id = rule['id']
                weight = self.weights[rule_id]
                
                scores[rule['description']] = score
                weighted_sum += score * weight
                total_weight += weight
            except Exception as e:
                logging.warning(f"Scoring rule error: {e}")
                scores[rule['description']] = 0
        
        final_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        return {
            'quality_score': final_score,
            'component_scores': scores,
            'grade': self._get_grade(final_score)
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 0.9:
            return 'A'
        elif score >= 0.8:
            return 'B'
        elif score >= 0.7:
            return 'C'
        elif score >= 0.6:
            return 'D'
        else:
            return 'F'

# Common validation rules
def has_required_fields(required_fields: List[str]):
    """Create a validation rule for required fields."""
    def rule(data: Dict[str, Any]) -> bool:
        return all(field in data and data[field] for field in required_fields)
    return rule

def min_length(field: str, min_len: int):
    """Create a validation rule for minimum field length."""
    def rule(data: Dict[str, Any]) -> bool:
        value = data.get(field, '')
        return len(str(value)) >= min_len
    return rule

def valid_url(field: str):
    """Create a validation rule for URL format."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    def rule(data: Dict[str, Any]) -> bool:
        url = data.get(field, '')
        return bool(url_pattern.match(str(url)))
    return rule

# Common scoring rules
def content_length_score(field: str, target_length: int = 500):
    """Create a scoring rule based on content length."""
    def rule(data: Dict[str, Any]) -> float:
        content = str(data.get(field, ''))
        length = len(content)
        if length == 0:
            return 0.0
        # Score based on how close to target length
        ratio = min(length, target_length) / target_length
        return min(ratio, 1.0)
    return rule

def uniqueness_score(field: str, seen_values: set):
    """Create a scoring rule for content uniqueness."""
    def rule(data: Dict[str, Any]) -> float:
        value = str(data.get(field, ''))
        if value in seen_values:
            return 0.0
        seen_values.add(value)
        return 1.0
    return rule

def keyword_relevance_score(field: str, keywords: List[str]):
    """Create a scoring rule for keyword relevance."""
    def rule(data: Dict[str, Any]) -> float:
        content = str(data.get(field, '')).lower()
        found_keywords = sum(1 for keyword in keywords if keyword.lower() in content)
        return found_keywords / len(keywords) if keywords else 0.0
    return rule

# Legacy compatibility
__all__ = [
    'DataValidator',
    'QualityScorer',
    'has_required_fields',
    'min_length',
    'valid_url',
    'content_length_score',
    'uniqueness_score',
    'keyword_relevance_score'
]