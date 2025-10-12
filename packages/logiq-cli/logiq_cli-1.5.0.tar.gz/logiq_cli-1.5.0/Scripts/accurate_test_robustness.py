"""
Accurate Model Robustness Testing - Reliable and Consistent Testing
Fixed issues with inconsistent evaluation and provides accurate performance metrics
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple
import sys
import os
import json
from datetime import datetime

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_threat_model import EnhancedThreatDetector
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

class AccurateModelTester:
    def __init__(self, model_path: str = "models/improved_threat_model.joblib"):
        """Initialize tester with both standard and enhanced models"""
        self.model_path = model_path
        self.load_models()
        
    def load_models(self):
        """Load both standard ML and enhanced models"""
        print("🔧 Loading Models...")
        
        # Load standard ML model
        try:
            model_data = joblib.load(self.model_path)
            self.ml_model = model_data['model']
            self.vectorizer = model_data['vectorizer']
            self.training_metadata = {
                'accuracy': model_data.get('training_results', {}).get('ImprovedModel', {}).get('accuracy', 0.0),
                'precision': model_data.get('training_results', {}).get('ImprovedModel', {}).get('precision', 0.0),
                'recall': model_data.get('training_results', {}).get('ImprovedModel', {}).get('recall', 0.0),
                'f1_score': model_data.get('training_results', {}).get('ImprovedModel', {}).get('f1_score', 0.0),
                'trained_date': model_data.get('trained_date', 'Unknown')
            }
            print(f"✅ Standard ML model loaded from: {self.model_path}")
            print(f"   Training F1-Score: {self.training_metadata['f1_score']:.3f}")
        except Exception as e:
            print(f"❌ Failed to load standard model: {e}")
            raise
        
        # Load enhanced model if available
        if ENHANCED_AVAILABLE:
            try:
                self.enhanced_detector = EnhancedThreatDetector(self.model_path)
                print("✅ Enhanced detector (ML + Patterns) loaded")
            except Exception as e:
                print(f"⚠️  Enhanced detector failed to load: {e}")
                ENHANCED_AVAILABLE = False
        
        self.enhanced_available = ENHANCED_AVAILABLE
    
    def predict_standard(self, log_text: str) -> Dict[str, Any]:
        """Make prediction using standard ML model only"""
        text_features = self.vectorizer.transform([log_text]).toarray()
        prediction = self.ml_model.predict(text_features)[0]
        probabilities = self.ml_model.predict_proba(text_features)[0]
        
        return {
            'prediction': int(prediction),
            'threat_probability': float(probabilities[1]),
            'benign_probability': float(probabilities[0]),
            'is_threat': bool(prediction == 1),
            'confidence': float(max(probabilities)),
            'model_type': 'standard'
        }
    
    def predict_enhanced(self, log_text: str) -> Dict[str, Any]:
        """Make prediction using enhanced model"""
        if not self.enhanced_available:
            return self.predict_standard(log_text)
        
        result = self.enhanced_detector.predict_log(log_text)
        return {
            'prediction': result['prediction'],
            'threat_probability': result['threat_probability'],
            'benign_probability': 1.0 - result['threat_probability'],
            'is_threat': result['is_threat'],
            'confidence': result['confidence'],
            'ml_only_probability': result['ml_threat_probability'],
            'enhancement_applied': result['enhancement_applied'],
            'pattern_matches': result['pattern_analysis']['pattern_matches'],
            'model_type': 'enhanced'
        }
    
    def get_test_data(self) -> Tuple[List[str], List[str]]:
        """Get consistent test datasets"""
        
        # High-confidence threat logs (should be detected)
        threat_logs = [
            # SSH brute force attacks
            "Oct 11 13:45:01 sshd[2541]: Failed password for invalid user admin from 103.20.10.5 port 51234 ssh2",
            "Oct 12 08:15:42 sshd[3421]: Failed password for root from 45.67.89.123 port 22 ssh2",
            "Oct 12 08:16:01 sshd[3425]: Failed password for invalid user test from 45.67.89.123 port 22 ssh2",
            
            # Privilege escalation
            "Oct 11 14:02:15 sudo: user root : TTY=pts/0 ; PWD=/home/user ; COMMAND=/usr/bin/python /tmp/revshell.py",
            "Oct 12 10:30:45 sudo: hacker : TTY=pts/2 ; PWD=/tmp ; USER=root ; COMMAND=/bin/bash /tmp/exploit.sh",
            "Oct 12 12:05:33 su: FAILED SU (to root) alice on pts/0",
            
            # Suspicious processes and network activity
            "Oct 11 15:10:30 kernel: Audit: type=1300 msg=audit(1665501030.123:456): arch=c000003e syscall=42 success=yes exit=0 a0=3 a1=7fffb7a421a0 a2=10 a3=7fffb7a41230 items=1 ppid=1 uid=1001 auid=1001 ses=2 msg='comm=\"nc\" exe=\"/bin/nc\" path=\"/tmp/exfil.tar.gz\"'",
            "Oct 12 15:10:48 process: python3 /var/tmp/download_and_execute.py executing with PID 12345",
            "PROCESS: Suspicious process spawned - nc.exe -l -p 4444 detected",
            
            # Account manipulation
            "Oct 11 17:01:10 useradd: new user: name=backdoor_user, UID=1005, GID=1005, home=/home/backdoor_user, shell=/bin/bash",
            
            # CVE exploitation
            "2024-01-15 ERROR: CVE-2023-4911 buffer overflow detected in glibc dynamic loader",
            "ALERT: Possible CVE-2023-38408 SSH forwarding vulnerability exploitation attempt",
            "CRITICAL: Log4j vulnerability CVE-2021-44228 exploitation detected in application logs",
            
            # Web attacks
            "403 Forbidden: SQL injection attempt blocked - UNION SELECT detected in user input",
            "INTRUSION: Directory traversal attack - ../../etc/passwd requested",
            "MALWARE: Suspicious PowerShell execution - encoded command detected",
            
            # Network threats
            "ANTIVIRUS: Trojan.Win32.Generic detected in file C:\\temp\\suspicious.exe",
            "BEHAVIOR: Ransomware activity suspected - mass file encryption detected",
            "DLP: Sensitive data exfiltration attempt blocked - SSN pattern in outbound traffic",
            "AUTHENTICATION: Brute force attack detected - 50 failed login attempts",
        ]
        
        # High-confidence benign logs (should NOT be detected as threats)
        benign_logs = [
            # Normal system operations
            "Oct 11 08:00:05 kernel: Initializing cgroup subsys cpuset",
            "Oct 11 09:15:20 sshd[1200]: Accepted password for regular_user from 192.168.1.5 port 45000 ssh2",
            "Oct 12 08:00:15 sshd[1001]: Accepted publickey for developer from 192.168.1.10 port 22 ssh2",
            "Oct 12 10:15:33 sshd[1200]: pam_unix(sshd:session): session closed for user admin",
            
            # Legitimate administrative activities
            "Oct 12 11:20:45 sudo: admin : TTY=pts/0 ; PWD=/home/admin ; USER=root ; COMMAND=/usr/bin/apt update",
            "Oct 12 12:05:18 sudo: developer : TTY=pts/1 ; PWD=/var/log ; USER=root ; COMMAND=/bin/cat /var/log/apache2/error.log",
            "Oct 12 13:45:22 sudo: sysadmin : TTY=pts/2 ; PWD=/etc ; USER=root ; COMMAND=/bin/systemctl restart nginx",
            
            # Normal application operations
            "2024-01-15 INFO: System startup completed successfully in 45.2 seconds",
            "CRON: Daily backup job completed - 15.2GB archived to /backup/daily_20240115.tar.gz",
            "DATABASE: Connection pool initialized - 10 connections to prod_db",
            "WEB: HTTP 200 GET /api/users/profile - response time 125ms",
            "API: GET /api/v1/health - Status: 200 OK, Response time: 45ms",
            
            # Maintenance and monitoring
            "MAINTENANCE: Log rotation completed - archived 5 files, freed 250MB",
            "UPDATE: Software patch applied successfully - Apache 2.4.52 to 2.4.54",
            "MONITOR: Health check passed - all services responding normally",
            "BACKUP: Incremental backup completed - 2.1GB processed in 8 minutes",
            
            # Network operations
            "NETWORK: Interface eth0 link up - 1Gbps full duplex",
            "VPN: Client connected from remote office - user: remote_worker",
            "FIREWALL: Rule updated - allowing HTTPS traffic on port 443",
            
            # Security-related but benign
            "SECURITY_SCAN: Vulnerability scan completed - no critical issues found",
            "AUDIT: Quarterly security review completed - compliance maintained",
            "CERTIFICATE: SSL certificate renewed successfully for domain.com",
        ]
        
        return threat_logs, benign_logs
    
    def test_model(self, model_type: str = 'standard') -> Dict[str, Any]:
        """Test specified model type with consistent data"""
        
        threat_logs, benign_logs = self.get_test_data()
        
        print(f\"\\n🧪 Testing {model_type.upper()} Model\")\n        print(\"=\"*60)\n        \n        # Test threat logs\n        print(f\"🔍 Testing against {len(threat_logs)} THREAT logs:\")\n        print(\"=\"*60)\n        \n        threat_results = []\n        threats_detected = 0\n        enhancements_applied = 0\n        \n        for i, log in enumerate(threat_logs):\n            if model_type == 'enhanced':\n                result = self.predict_enhanced(log)\n            else:\n                result = self.predict_standard(log)\n            \n            threat_results.append({**result, 'log_text': log, 'expected': 1})\n            \n            if result['is_threat']:\n                threats_detected += 1\n                status = \"✅ DETECTED\"\n            else:\n                status = \"❌ MISSED\"\n            \n            # Show enhancement info for enhanced model\n            if model_type == 'enhanced' and result.get('enhancement_applied', False):\n                enhancements_applied += 1\n                prob_info = f\"ML:{result['ml_only_probability']:.3f}→{result['threat_probability']:.3f}\"\n                model_icon = \"🔧\"\n            else:\n                prob_info = f\"Threat:{result['threat_probability']:.3f}\"\n                model_icon = \"🤖\"\n            \n            print(f\"{i+1:2d}. {status} {model_icon} | {prob_info} | {log[:60]}...\")\n        \n        # Test benign logs\n        print(f\"\\n🔍 Testing against {len(benign_logs)} BENIGN logs:\")\n        print(\"=\"*60)\n        \n        benign_results = []\n        benign_correct = 0\n        false_positives = 0\n        \n        for i, log in enumerate(benign_logs):\n            if model_type == 'enhanced':\n                result = self.predict_enhanced(log)\n            else:\n                result = self.predict_standard(log)\n            \n            benign_results.append({**result, 'log_text': log, 'expected': 0})\n            \n            if not result['is_threat']:\n                benign_correct += 1\n                status = \"✅ CORRECT\"\n            else:\n                false_positives += 1\n                status = \"❌ FALSE POS\"\n            \n            # Show enhancement info for enhanced model\n            if model_type == 'enhanced' and result.get('enhancement_applied', False):\n                prob_info = f\"ML:{result['ml_only_probability']:.3f}→{result['threat_probability']:.3f}\"\n                model_icon = \"🔧\"\n            else:\n                prob_info = f\"Threat:{result['threat_probability']:.3f}\"\n                model_icon = \"🤖\"\n            \n            print(f\"{i+1:2d}. {status} {model_icon} | {prob_info} | {log[:60]}...\")\n        \n        # Calculate metrics\n        all_results = threat_results + benign_results\n        \n        true_positives = threats_detected\n        true_negatives = benign_correct\n        false_negatives = len(threat_logs) - threats_detected\n        false_positives = false_positives\n        \n        total_correct = true_positives + true_negatives\n        total_samples = len(all_results)\n        \n        accuracy = total_correct / total_samples\n        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0\n        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0\n        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0\n        \n        threat_detection_rate = threats_detected / len(threat_logs)\n        benign_recognition_rate = benign_correct / len(benign_logs)\n        \n        if model_type == 'enhanced':\n            enhancement_rate = enhancements_applied / len(all_results)\n            print(f\"\\n🔧 Pattern Enhancement Applied: {enhancements_applied}/{total_samples} ({enhancement_rate:.1%})\")\n        \n        print(f\"\\n📊 {model_type.upper()} MODEL PERFORMANCE:\")\n        print(\"=\"*60)\n        print(f\"Accuracy:      {accuracy:.3f} ({total_correct}/{total_samples})\")\n        print(f\"Precision:     {precision:.3f}\")\n        print(f\"Recall:        {recall:.3f}\")\n        print(f\"F1-Score:      {f1_score:.3f}\")\n        print(f\"\\nDetection Rates:\")\n        print(f\"Threats:       {threat_detection_rate:.3f} ({threats_detected}/{len(threat_logs)})\")\n        print(f\"Benign:        {benign_recognition_rate:.3f} ({benign_correct}/{len(benign_logs)})\")\n        print(f\"\\nConfusion Matrix:\")\n        print(f\"True Negatives:  {true_negatives:3d} | False Positives: {false_positives:3d}\")\n        print(f\"False Negatives: {false_negatives:3d} | True Positives:  {true_positives:3d}\")\n        \n        return {\n            'model_type': model_type,\n            'threat_results': threat_results,\n            'benign_results': benign_results,\n            'metrics': {\n                'accuracy': accuracy,\n                'precision': precision,\n                'recall': recall,\n                'f1_score': f1_score,\n                'threat_detection_rate': threat_detection_rate,\n                'benign_recognition_rate': benign_recognition_rate,\n                'true_positives': true_positives,\n                'true_negatives': true_negatives,\n                'false_positives': false_positives,\n                'false_negatives': false_negatives,\n                'total_samples': total_samples\n            },\n            'enhancement_rate': enhancements_applied / total_samples if model_type == 'enhanced' else 0\n        }\n    \n    def compare_models(self) -> Dict[str, Any]:\n        \"\"\"Compare standard and enhanced models side by side\"\"\"\n        print(\"🚀 ACCURATE MODEL ROBUSTNESS TEST\")\n        print(\"=\"*60)\n        print(\"Comparing Standard ML vs Enhanced (ML + Patterns) Models\")\n        \n        # Test standard model\n        standard_results = self.test_model('standard')\n        \n        # Test enhanced model if available\n        if self.enhanced_available:\n            enhanced_results = self.test_model('enhanced')\n        else:\n            enhanced_results = None\n            print(\"\\n⚠️  Enhanced model not available for comparison\")\n        \n        # Performance comparison\n        print(\"\\n📊 MODEL COMPARISON SUMMARY:\")\n        print(\"=\"*60)\n        \n        training_f1 = self.training_metadata['f1_score']\n        standard_f1 = standard_results['metrics']['f1_score']\n        \n        print(f\"Training F1-Score:    {training_f1:.3f}\")\n        print(f\"Standard Test F1:     {standard_f1:.3f}\")\n        \n        if enhanced_results:\n            enhanced_f1 = enhanced_results['metrics']['f1_score']\n            print(f\"Enhanced Test F1:     {enhanced_f1:.3f}\")\n            \n            print(f\"\\nPerformance Analysis:\")\n            standard_drop = training_f1 - standard_f1\n            enhanced_drop = training_f1 - enhanced_f1\n            \n            print(f\"Standard Drop:        {standard_drop:.3f}\")\n            print(f\"Enhanced Drop:        {enhanced_drop:.3f}\")\n            print(f\"Enhancement Gain:     {enhanced_f1 - standard_f1:.3f}\")\n            \n            # Enhancement usage\n            print(f\"\\nPattern Enhancement:  {enhanced_results['enhancement_rate']:.1%} of samples\")\n            \n            # Recommendation\n            print(f\"\\n🎯 RECOMMENDATIONS:\")\n            print(\"=\"*60)\n            \n            if enhanced_f1 > 0.80 and enhanced_drop < 0.05:\n                print(\"🏆 EXCELLENT: Enhanced model ready for production!\")\n            elif enhanced_f1 > 0.70 and enhanced_drop < 0.15:\n                print(\"✅ GOOD: Enhanced model shows strong performance\")\n            elif enhanced_f1 > standard_f1:\n                print(\"📈 IMPROVED: Enhanced model outperforms standard\")\n            else:\n                print(\"⚠️  NEEDS WORK: Model requires additional tuning\")\n                \n        else:\n            standard_drop = training_f1 - standard_f1\n            print(f\"\\nStandard Model Analysis:\")\n            print(f\"Performance Drop:     {standard_drop:.3f}\")\n            \n            if standard_drop > 0.15:\n                print(\"🔴 OVERFITTING: Significant performance drop on real data\")\n            elif standard_drop > 0.05:\n                print(\"🟡 MILD OVERFITTING: Some performance degradation\")\n            else:\n                print(\"🟢 GOOD GENERALIZATION: Model performs well on real data\")\n        \n        return {\n            'standard_results': standard_results,\n            'enhanced_results': enhanced_results,\n            'training_metadata': self.training_metadata,\n            'comparison_date': datetime.now().isoformat()\n        }\n    \n    def save_test_report(self, results: Dict[str, Any], filename: str = None):\n        \"\"\"Save detailed test report\"\"\"\n        if filename is None:\n            timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n            filename = f\"model_test_report_{timestamp}.json\"\n        \n        script_dir = Path(__file__).parent\n        report_path = script_dir / filename\n        \n        # Prepare serializable results\n        serializable_results = {\n            'metadata': {\n                'test_date': results['comparison_date'],\n                'model_path': self.model_path,\n                'training_metadata': self.training_metadata\n            },\n            'standard_model': {\n                'metrics': results['standard_results']['metrics']\n            }\n        }\n        \n        if results['enhanced_results']:\n            serializable_results['enhanced_model'] = {\n                'metrics': results['enhanced_results']['metrics'],\n                'enhancement_rate': results['enhanced_results']['enhancement_rate']\n            }\n        \n        with open(report_path, 'w') as f:\n            json.dump(serializable_results, f, indent=2)\n        \n        print(f\"\\n💾 Test report saved to: {report_path}\")\n        return report_path\n\ndef main():\n    \"\"\"Main testing function\"\"\"\n    tester = AccurateModelTester()\n    results = tester.compare_models()\n    tester.save_test_report(results)\n    return results\n\nif __name__ == \"__main__\":\n    main()\n