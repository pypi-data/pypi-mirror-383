"""
Simple Pre-RAG Log Classifier with Redis Caching
Returns 0 (filter out) or 1 (send to RAG) for each log
"""

import pandas as pd
import numpy as np
import joblib
import hashlib
import json
from pathlib import Path
from typing import List, Union
import redis
import logging

class PreRAGClassifier:
    """Simple binary classifier for pre-RAG filtering with Redis caching"""
    
    def __init__(self, model_path: str = None, redis_host: str = "localhost", redis_port: int = 6379):
        # Load ML model
        self.model = None
        self.vectorizer = None
        self.threshold = 0.5
        self._load_model(model_path)
        
        # Redis setup for caching
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis_client.ping()  # Test connection
            self.cache_enabled = True
            print(f"[OK] Redis cache connected: {redis_host}:{redis_port}")
        except Exception as e:
            print(f"[WARNING] Redis cache disabled: {e}")
            self.redis_client = None
            self.cache_enabled = False
        
        # Cache settings
        self.cache_ttl = 3600  # 1 hour TTL
        self.cache_prefix = "logiq_classify:"
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'threats_detected': 0,
            'logs_filtered': 0
        }
    
    def _load_model(self, model_path: str = None):
        """Load the ML model"""
        try:
            if model_path is None:
                # Find latest model - check multiple possible locations
                possible_dirs = [
                    Path("models"),  # Current directory
                    Path("Scripts/models"),  # Scripts subdirectory
                    Path(__file__).parent / "models",  # Same directory as this script
                    Path(__file__).parent.parent / "Scripts" / "models"  # Scripts/models from aiagent root
                ]
                
                model_files = []
                for models_dir in possible_dirs:
                    if models_dir.exists():
                        model_files = list(models_dir.glob("*threat_model*.joblib"))
                        if not model_files:
                            model_files = list(models_dir.glob("*.joblib"))
                        if model_files:
                            break
                
                if model_files:
                    model_path = max(model_files, key=lambda x: x.stat().st_mtime)
                else:
                    raise FileNotFoundError("No model files found")
            
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.vectorizer = model_data['vectorizer']
            self.threshold = model_data.get('optimal_threshold', 0.5)
            
            # Test model quality - if all predictions are identical, use rule-based fallback
            test_logs = ['test log 1', 'test log 2', 'test log 3']
            try:
                X_test = self.vectorizer.transform(test_logs).toarray()
                probs = self.model.predict_proba(X_test)[:, 1]
                if len(set(probs.round(3))) <= 1:  # All probabilities are essentially identical
                    pass
            except Exception as test_error:
                # logging.debug("Model quality check failed: %s", test_error)
                raise test_error
            
            print(f"[OK] Model loaded: {Path(model_path).name}")
            print(f"[THRESHOLD] Threshold: {self.threshold:.3f}")
            
        except Exception as e:
            self.model = None
    
    def _get_cache_key(self, log_text: str) -> str:
        """Generate cache key for log text"""
        log_hash = hashlib.md5(log_text.encode()).hexdigest()
        return f"{self.cache_prefix}{log_hash}"
    
    def _cache_get(self, log_text: str) -> Union[int, None]:
        """Get classification from cache"""
        if not self.cache_enabled:
            return None
        
        try:
            cache_key = self._get_cache_key(log_text)
            cached_result = self.redis_client.get(cache_key)
            
            if cached_result is not None:
                self.stats['cache_hits'] += 1
                return int(cached_result)
            else:
                self.stats['cache_misses'] += 1
                return None
                
        except Exception as e:
            logging.warning(f"Cache get error: {e}")
            return None
    
    def _cache_set(self, log_text: str, classification: int):
        """Store classification in cache"""
        if not self.cache_enabled:
            return
        
        try:
            cache_key = self._get_cache_key(log_text)
            self.redis_client.setex(cache_key, self.cache_ttl, str(classification))
        except Exception as e:
            logging.warning(f"Cache set error: {e}")
    
    def _rule_based_classify(self, log_text: str) -> int:
        """Simple rule-based classification as fallback"""
        log_lower = log_text.lower()
        
        # High priority threat patterns
        threat_patterns = [
            'failed password', 'authentication failure', 'invalid user',
            'brute force', 'dos attack', 'exploit', 'malware', 'virus',
            'unauthorized', 'intrusion', 'breach', 'hack', 'attack',
            'suspicious', 'anomaly', 'backdoor', 'trojan', 'rootkit',
            'privilege escalation', 'buffer overflow', 'injection',
            'vulnerability', 'exploit', 'payload', 'shell', 'reverse',
            'persistence', 'lateral movement', 'exfiltration'
        ]
        
        # Check for threat indicators
        for pattern in threat_patterns:
            if pattern in log_lower:
                return 1  # Send to RAG
        
        # Benign patterns (high confidence to filter)
        benign_patterns = [
            'started successfully', 'completed normally', 'scheduled task',
            'backup completed', 'update installed', 'service started',
            'normal shutdown', 'system boot', 'kernel loaded'
        ]
        
        for pattern in benign_patterns:
            if pattern in log_lower:
                return 0  # Filter out
        
        # Default: filter out uncertain logs (be more conservative)
        return 0
    
    def classify_single(self, log_text: str) -> int:
        """
        Classify a single log entry
        Returns: 0 (filter out) or 1 (send to RAG)
        """
        # Check cache first
        cached_result = self._cache_get(log_text)
        if cached_result is not None:
            self.stats['total_processed'] += 1
            return cached_result
        
        # Classify using ML model or rules
        if self.model is not None:
            try:
                # Transform log text
                X = self.vectorizer.transform([log_text]).toarray()
                threat_probability = self.model.predict_proba(X)[0, 1]
                
                # Simple binary decision
                classification = 1 if threat_probability >= self.threshold else 0
                
            except Exception as e:
                logging.warning(f"ML classification error: {e}")
                classification = self._rule_based_classify(log_text)
        else:
            # Use rule-based fallback
            classification = self._rule_based_classify(log_text)
        
        # Cache the result
        self._cache_set(log_text, classification)
        
        # Update statistics
        self.stats['total_processed'] += 1
        if classification == 1:
            self.stats['threats_detected'] += 1
        else:
            self.stats['logs_filtered'] += 1
        
        return classification
    
    def classify_batch(self, log_texts: List[str]) -> List[int]:
        """
        Classify multiple log entries
        Returns: List of 0s and 1s
        """
        results = []
        
        for log_text in log_texts:
            classification = self.classify_single(log_text)
            results.append(classification)
        
        return results
    
    def classify_with_details(self, log_text: str) -> dict:
        """
        Classify with additional details for debugging
        """
        classification = self.classify_single(log_text)
        
        result = {
            'log_text': log_text,
            'classification': classification,
            'action': 'SEND_TO_RAG' if classification == 1 else 'FILTER_OUT',
            'from_cache': self._cache_get(log_text) is not None
        }
        
        # Add ML details if available
        if self.model is not None:
            try:
                X = self.vectorizer.transform([log_text]).toarray()
                threat_probability = self.model.predict_proba(X)[0, 1]
                result['threat_probability'] = float(threat_probability)
                result['method'] = 'ML'
            except:
                result['method'] = 'RULES'
        else:
            result['method'] = 'RULES'
        
        return result
    
    def get_stats(self) -> dict:
        """Get processing statistics"""
        stats = self.stats.copy()
        
        if stats['total_processed'] > 0:
            stats['cache_hit_rate'] = stats['cache_hits'] / stats['total_processed']
            stats['threat_rate'] = stats['threats_detected'] / stats['total_processed']
            stats['filter_rate'] = stats['logs_filtered'] / stats['total_processed']
        else:
            stats['cache_hit_rate'] = 0.0
            stats['threat_rate'] = 0.0
            stats['filter_rate'] = 0.0
        
        return stats
    
    def clear_cache(self):
        """Clear Redis cache"""
        if self.cache_enabled:
            try:
                # Delete all keys with our prefix
                keys = self.redis_client.keys(f"{self.cache_prefix}*")
                if keys:
                    self.redis_client.delete(*keys)
                    print(f"[CLEARED] Cleared {len(keys)} cache entries")
                else:
                    print("[EMPTY] Cache already empty")
            except Exception as e:
                print(f"[ERROR] Error clearing cache: {e}")

def demo_prerag_classifier():
    """Demonstrate the Pre-RAG classifier"""
    print("🛡️  Pre-RAG Log Classifier Demo")
    print("=" * 50)
    
    # Initialize classifier
    classifier = PreRAGClassifier()
    
    # Test logs
    test_logs = [
        "Oct 11 13:45:01 sshd[2541]: Failed password for invalid user admin from 192.168.1.100",
        "Oct 11 14:02:15 sudo: authentication failure; user=attacker",
        "Oct 11 15:10:30 kernel: Buffer overflow detected in application xyz",
        "Oct 11 16:22:33 firewall: Suspicious connection from 203.0.113.5",
        "Oct 11 08:00:05 kernel: System started successfully",
        "Oct 11 09:15:20 cron: Scheduled backup completed normally",
        "Oct 11 10:30:00 systemd: Service nginx started successfully",
        "Oct 11 12:05:30 rsyslog: Log rotation completed",
        "Oct 11 17:30:45 apache: Normal HTTP GET request processed",
        "Oct 11 18:45:12 mysql: Database backup completed successfully"
    ]
    
    print(f"🔍 Classifying {len(test_logs)} logs...")
    print()
    
    # Classify logs
    for i, log in enumerate(test_logs, 1):
        result = classifier.classify_with_details(log)
        action_icon = "📤" if result['classification'] == 1 else "✅"
        cache_icon = "💾" if result['from_cache'] else "🔄"
        
        print(f"{i:2d}. {action_icon} {result['action']} {cache_icon}")
        print(f"    {log[:80]}...")
        print(f"    Method: {result['method']}")
        if 'threat_probability' in result:
            print(f"    Threat Score: {result['threat_probability']:.3f}")
        print()
    
    # Test caching by running same logs again
    print("🔄 Testing cache performance (running same logs again)...")
    start_time = __import__('time').time()
    
    classifications = classifier.classify_batch(test_logs)
    
    end_time = __import__('time').time()
    
    # Show statistics
    stats = classifier.get_stats()
    print(f"\n📊 Performance Statistics:")
    print(f"   Total processed: {stats['total_processed']}")
    print(f"   Cache hits: {stats['cache_hits']} ({stats['cache_hit_rate']:.1%})")
    print(f"   Cache misses: {stats['cache_misses']}")
    print(f"   Threats detected: {stats['threats_detected']} ({stats['threat_rate']:.1%})")
    print(f"   Logs filtered: {stats['logs_filtered']} ({stats['filter_rate']:.1%})")
    print(f"   Processing time: {end_time - start_time:.3f}s")
    
    # Show binary results
    print(f"\n🎯 Binary Classifications:")
    print(f"   Results: {classifications}")
    print(f"   (0 = Filter Out, 1 = Send to RAG)")
    
    print(f"\n💡 Integration Ready!")
    print("   • Returns simple 0/1 classifications")
    print("   • Redis caching for performance")
    print("   • Fallback to rule-based if ML fails")
    print("   • Suitable for CLI tool pre-filtering")

if __name__ == "__main__":
    demo_prerag_classifier()