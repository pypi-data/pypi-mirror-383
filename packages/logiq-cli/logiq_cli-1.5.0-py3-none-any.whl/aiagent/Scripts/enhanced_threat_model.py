"""
Enhanced Threat Detection with Rule-Based Post-Processing
Combines ML model with pattern matching for better real-world performance
"""

import joblib
import re
from typing import Dict, Any, List
from pathlib import Path

class EnhancedThreatDetector:
    def __init__(self, model_path: str = "models/improved_threat_model.joblib"):
        """Load ML model and initialize rule-based patterns"""
        self.load_model(model_path)
        self.setup_security_patterns()
    
    def load_model(self, model_path: str):
        """Load the trained ML model"""
        try:
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.vectorizer = model_data['vectorizer']
            print(f"✅ Enhanced model loaded from: {model_path}")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
    
    def setup_security_patterns(self):
        """Define security patterns that indicate threats"""
        self.threat_patterns = {
            'ssh_attacks': [
                r'Failed password for (?:invalid user|root|admin)',
                r'sshd.*Failed password.*from.*port',
                r'authentication failure.*ssh',
                r'Invalid user.*from.*ssh'
            ],
            'privilege_escalation': [
                r'sudo.*COMMAND.*(?:/tmp/|/var/tmp/|\.py|\.sh|\.exe)',
                r'sudo.*root.*TTY.*COMMAND',
                r'su.*authentication failure',
                r'usermod.*-G.*root'
            ],
            'suspicious_processes': [
                r'nc\.exe.*-l.*-p',
                r'netcat.*-l.*-p',
                r'/bin/nc.*-l',
                r'python.*(?:/tmp/|/var/tmp/).*\.py',
                r'sh.*(?:/tmp/|/var/tmp/)',
                r'bash.*(?:/tmp/|/var/tmp/)'
            ],
            'file_operations': [
                r'audit.*syscall.*(?:open|write|unlink).*(?:/etc/passwd|/etc/shadow)',
                r'audit.*comm="nc".*path=".*\.tar\.gz"',
                r'audit.*exe="/bin/nc"',
                r'useradd.*backdoor.*user'
            ],
            'network_exfiltration': [
                r'audit.*syscall=42.*nc',
                r'netstat.*ESTABLISHED.*:(?:4444|1234|8080|9999)',
                r'connection.*suspicious.*port',
                r'data transfer.*unusual.*volume'
            ],
            'system_modification': [
                r'useradd.*new user.*backdoor',
                r'usermod.*shell.*(?:/bin/bash|/bin/sh)',
                r'passwd.*changed.*for.*suspicious',
                r'crontab.*modified.*(?:/tmp/|/var/tmp/)'
            ]
        }
        
        # Compile patterns for performance
        self.compiled_patterns = {}
        for category, patterns in self.threat_patterns.items():
            self.compiled_patterns[category] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def check_security_patterns(self, log_text: str) -> Dict[str, Any]:
        """Check log against security patterns"""
        matches = {}
        threat_score = 0.0
        
        for category, patterns in self.compiled_patterns.items():
            category_matches = []
            for pattern in patterns:
                if pattern.search(log_text):
                    category_matches.append(pattern.pattern)
                    threat_score += 0.15  # Each pattern match adds threat score
            
            if category_matches:
                matches[category] = category_matches
        
        return {
            'pattern_matches': matches,
            'pattern_threat_score': min(threat_score, 1.0),  # Cap at 1.0
            'has_patterns': len(matches) > 0
        }
    
    def predict_log(self, log_text: str) -> Dict[str, Any]:
        """Enhanced prediction combining ML and pattern matching"""
        # Get ML prediction
        text_features = self.vectorizer.transform([log_text]).toarray()
        ml_prediction = self.model.predict(text_features)[0]
        ml_probabilities = self.model.predict_proba(text_features)[0]
        ml_threat_prob = float(ml_probabilities[1])
        
        # Get pattern-based analysis
        pattern_analysis = self.check_security_patterns(log_text)
        
        # Enhanced threat calculation
        enhanced_threat_prob = ml_threat_prob
        
        # Boost probability if security patterns detected
        if pattern_analysis['has_patterns']:
            pattern_boost = pattern_analysis['pattern_threat_score'] * 0.4  # 40% boost weight
            enhanced_threat_prob = min(ml_threat_prob + pattern_boost, 1.0)
        
        # Final prediction based on enhanced probability
        enhanced_prediction = 1 if enhanced_threat_prob > 0.5 else 0
        
        return {
            'prediction': int(enhanced_prediction),
            'ml_prediction': int(ml_prediction),
            'threat_probability': enhanced_threat_prob,
            'ml_threat_probability': ml_threat_prob,
            'pattern_analysis': pattern_analysis,
            'is_threat': bool(enhanced_prediction == 1),
            'confidence': float(max(enhanced_threat_prob, 1 - enhanced_threat_prob)),
            'enhancement_applied': pattern_analysis['has_patterns']
        }
    
    def analyze_log_batch(self, logs: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple logs efficiently"""
        results = []
        for log in logs:
            result = self.predict_log(log)
            results.append({**result, 'log_text': log})
        return results

def test_enhanced_detector():
    """Test the enhanced detector on problematic system logs"""
    detector = EnhancedThreatDetector()
    
    # Test logs that the original model missed
    test_logs = [
        "Oct 11 13:45:01 sshd[2541]: Failed password for invalid user admin from 103.20.10.5 port 51234 ssh2",
        "Oct 11 14:02:15 sudo: user root : TTY=pts/0 ; PWD=/home/user ; COMMAND=/usr/bin/python /tmp/revshell.py",
        "Oct 11 15:10:30 kernel: Audit: type=1300 msg=audit(1665501030.123:456): arch=c000003e syscall=42 success=yes exit=0 a0=3 a1=7fffb7a421a0 a2=10 a3=7fffb7a41230 items=1 ppid=1 uid=1001 auid=1001 ses=2 msg='comm=\"nc\" exe=\"/bin/nc\" path=\"/tmp/exfil.tar.gz\"'",
        "Oct 11 17:01:10 useradd: new user: name=backdoor_user, UID=1005, GID=1005, home=/home/backdoor_user, shell=/bin/bash",
        # Benign logs that should stay benign
        "Oct 11 08:00:05 kernel: Initializing cgroup subsys cpuset",
        "Oct 11 09:15:20 sshd[1200]: Accepted password for regular_user from 192.168.1.5 port 45000 ssh2"
    ]
    
    print("🔧 ENHANCED THREAT DETECTION TEST")
    print("="*50)
    
    for i, log in enumerate(test_logs):
        result = detector.predict_log(log)
        
        # Status indicators
        if result['enhancement_applied']:
            status = "🔧 ENHANCED"
        else:
            status = "🤖 ML-ONLY"
        
        threat_level = "🚨 THREAT" if result['is_threat'] else "✅ BENIGN"
        
        print(f"\n{i+1}. {status} | {threat_level}")
        print(f"   ML Prob: {result['ml_threat_probability']:.3f} → Enhanced: {result['threat_probability']:.3f}")
        
        if result['pattern_analysis']['pattern_matches']:
            print(f"   🎯 Patterns: {list(result['pattern_analysis']['pattern_matches'].keys())}")
        
        print(f"   📝 {log[:80]}...")

if __name__ == "__main__":
    test_enhanced_detector()