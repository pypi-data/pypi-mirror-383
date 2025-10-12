"""
Pure ML Model Test - No Pattern Enhancement
Tests only the machine learning model without any rule-based assistance
"""

import joblib
import numpy as np
from typing import List, Dict, Any

class PureMLTester:
    def __init__(self, model_path: str = "models/improved_threat_model.joblib"):
        """Load only the ML model, no enhancements"""
        self.load_model(model_path)
        
    def load_model(self, model_path: str):
        """Load the ML model components only"""
        try:
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.vectorizer = model_data['vectorizer']
            self.training_results = model_data.get('training_results', {}).get('ImprovedModel', {})
            print(f"✅ Pure ML model loaded from: {model_path}")
            print(f"📊 Training F1-Score: {self.training_results.get('f1_score', 0):.3f}")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
    
    def predict_pure_ml(self, log_text: str) -> Dict[str, Any]:
        """Make prediction using ONLY ML model - no enhancements"""
        text_features = self.vectorizer.transform([log_text]).toarray()
        prediction = self.model.predict(text_features)[0]
        probabilities = self.model.predict_proba(text_features)[0]
        
        return {
            'prediction': int(prediction),
            'threat_probability': float(probabilities[1]),
            'benign_probability': float(probabilities[0]),
            'is_threat': bool(prediction == 1),
            'confidence': float(max(probabilities))
        }
    
    def test_pure_ml_performance(self) -> Dict[str, Any]:
        """Test pure ML model on the same samples"""
        
        # Same threat samples from the enhanced test
        threat_logs = [
            "Oct 11 13:45:01 sshd[2541]: Failed password for invalid user admin from 103.20.10.5 port 51234 ssh2",
            "Oct 11 14:02:15 sudo: user root : TTY=pts/0 ; PWD=/home/user ; COMMAND=/usr/bin/python /tmp/revshell.py",
            "Oct 11 15:10:30 kernel: Audit: type=1300 msg=audit(1665501030.123:456): arch=c000003e syscall=42 success=yes exit=0 a0=3 a1=7fffb7a421a0 a2=10 a3=7fffb7a41230 items=1 ppid=1 uid=1001 auid=1001 ses=2 msg='comm=\"nc\" exe=\"/bin/nc\" path=\"/tmp/exfil.tar.gz\"'",
            "Oct 11 17:01:10 useradd: new user: name=backdoor_user, UID=1005, GID=1005, home=/home/backdoor_user, shell=/bin/bash",
            "Oct 12 08:15:42 sshd[3421]: Failed password for root from 45.67.89.123 port 22 ssh2",
            "Oct 12 08:16:01 sshd[3425]: Failed password for invalid user test from 45.67.89.123 port 22 ssh2",
            "Oct 12 09:22:15 auth.log: Failed password for admin from 192.168.1.200 port 2222 ssh2",
            "Oct 12 10:30:45 sudo: hacker : TTY=pts/2 ; PWD=/tmp ; USER=root ; COMMAND=/bin/bash /tmp/exploit.sh",
            "Oct 12 11:15:20 sudo: attacker : authentication failure ; TTY=pts/1 ; PWD=/home/attacker ; USER=root ; COMMAND=/bin/su",
            "Oct 12 12:05:33 su: FAILED SU (to root) alice on pts/0",
            "CVE-2021-44228 Log4j exploitation detected",
            "SQL injection attempt blocked - UNION SELECT detected",
            "Failed password for root from 192.168.1.100 port 22 ssh2",
            "MALWARE: Suspicious PowerShell execution - encoded command detected",
            "PROCESS: Suspicious process spawned - nc.exe -l -p 4444 detected"
        ]
        
        # Same benign samples
        benign_logs = [
            "Oct 11 08:00:05 kernel: Initializing cgroup subsys cpuset",
            "Oct 11 09:15:20 sshd[1200]: Accepted password for regular_user from 192.168.1.5 port 45000 ssh2",
            "Oct 12 11:20:45 sudo: admin : TTY=pts/0 ; PWD=/home/admin ; USER=root ; COMMAND=/usr/bin/apt update",
            "2024-01-15 INFO: System startup completed successfully in 45.2 seconds",
            "CRON: Daily backup job completed - 15.2GB archived to /backup/daily_20240115.tar.gz",
            "WEB: HTTP 200 GET /api/users/profile - response time 125ms",
            "MAINTENANCE: Log rotation completed - archived 5 files, freed 250MB",
            "NETWORK: Interface eth0 link up - 1Gbps full duplex",
            "User john.doe logged in successfully",
            "Backup job completed - 5GB archived"
        ]
        
        print("🤖 PURE ML MODEL TEST (NO ENHANCEMENTS)")
        print("="*60)
        print("Testing the raw machine learning model performance...")
        
        # Test threats
        print(f"\\n🚨 Testing {len(threat_logs)} THREAT samples:")
        print("-"*60)
        
        threats_detected = 0
        for i, log in enumerate(threat_logs):
            result = self.predict_pure_ml(log)
            
            if result['is_threat']:
                threats_detected += 1
                status = "✅ DETECTED"
            else:
                status = "❌ MISSED"
            
            print(f"{i+1:2d}. {status} | Prob: {result['threat_probability']:.3f} | {log[:60]}...")
        
        # Test benign
        print(f"\\n✅ Testing {len(benign_logs)} BENIGN samples:")
        print("-"*60)
        
        benign_correct = 0
        false_positives = 0
        for i, log in enumerate(benign_logs):
            result = self.predict_pure_ml(log)
            
            if not result['is_threat']:
                benign_correct += 1
                status = "✅ CORRECT"
            else:
                false_positives += 1
                status = "❌ FALSE POS"
            
            print(f"{i+1:2d}. {status} | Prob: {result['threat_probability']:.3f} | {log[:60]}...")
        
        # Calculate metrics
        total_samples = len(threat_logs) + len(benign_logs)
        total_correct = threats_detected + benign_correct
        
        accuracy = total_correct / total_samples
        precision = threats_detected / (threats_detected + false_positives) if (threats_detected + false_positives) > 0 else 0
        recall = threats_detected / len(threat_logs)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        threat_detection_rate = threats_detected / len(threat_logs)
        benign_recognition_rate = benign_correct / len(benign_logs)
        
        print(f"\\n📊 PURE ML MODEL PERFORMANCE:")
        print("="*60)
        print(f"Accuracy:           {accuracy:.3f} ({total_correct}/{total_samples})")
        print(f"Precision:          {precision:.3f}")
        print(f"Recall:             {recall:.3f}")
        print(f"F1-Score:           {f1_score:.3f}")
        print(f"\\nDetection Rates:")
        print(f"Threats Detected:   {threat_detection_rate:.3f} ({threats_detected}/{len(threat_logs)})")
        print(f"Benign Recognized:  {benign_recognition_rate:.3f} ({benign_correct}/{len(benign_logs)})")
        print(f"False Positives:    {false_positives}/{len(benign_logs)} ({false_positives/len(benign_logs):.1%})")
        
        # Compare with training
        training_f1 = self.training_results.get('f1_score', 0)
        performance_drop = training_f1 - f1_score
        
        print(f"\\n🔍 OVERFITTING ANALYSIS:")
        print("="*60)
        print(f"Training F1-Score:   {training_f1:.3f}")
        print(f"Pure ML Test F1:     {f1_score:.3f}")
        print(f"Performance Drop:    {performance_drop:.3f}")
        
        if performance_drop > 0.10:
            print("🔴 SIGNIFICANT OVERFITTING: Pure ML model fails on real data")
        elif performance_drop > 0.05:
            print("🟡 MILD OVERFITTING: Some degradation in pure ML performance")
        else:
            print("🟢 GOOD: Pure ML model generalizes well")
        
        print(f"\\n🎯 PURE ML MODEL ASSESSMENT:")
        print("="*60)
        
        if f1_score < 0.60:
            print("🔴 POOR: Pure ML model needs significant improvement")
            print("💡 The model heavily relies on pattern matching to perform well")
        elif f1_score < 0.70:
            print("🟡 MEDIOCRE: Pure ML model has room for improvement")
            print("💡 Pattern enhancement provides significant value")
        elif f1_score < 0.80:
            print("✅ DECENT: Pure ML model performs reasonably well")
            print("💡 Pattern enhancement provides moderate improvement")
        else:
            print("🏆 EXCELLENT: Pure ML model performs very well independently")
        
        return {
            'pure_ml_metrics': {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'threat_detection_rate': threat_detection_rate,
                'benign_recognition_rate': benign_recognition_rate,
                'false_positive_rate': false_positives / len(benign_logs)
            },
            'training_f1': training_f1,
            'performance_drop': performance_drop,
            'threats_detected': threats_detected,
            'total_threats': len(threat_logs),
            'false_positives': false_positives,
            'total_benign': len(benign_logs)
        }

def main():
    """Test pure ML performance"""
    tester = PureMLTester()
    results = tester.test_pure_ml_performance()
    
    print(f"\\n🔬 CONCLUSION:")
    print("="*60)
    print("This test shows the TRUE machine learning model performance")
    print("without any pattern matching or rule-based assistance.")
    print("\\nCompare these results with the enhanced model test to see")
    print("how much the pattern matching rules are helping!")

if __name__ == "__main__":
    main()