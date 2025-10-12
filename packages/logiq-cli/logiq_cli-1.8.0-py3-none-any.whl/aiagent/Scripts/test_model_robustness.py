"""
Model Robustness Testing - Test against real-world log samples
Tests for overfitting and evaluates model performance on unseen data
Now supports both standard ML model and enhanced hybrid model
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_threat_model import EnhancedThreatDetector
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    print("⚠️  Enhanced detector not available, using standard ML model only")

class ModelRobustnessTester:
    def __init__(self, model_path: str = "models/improved_threat_model.joblib", use_enhanced: bool = True):
        """Load the trained model and components (supports both standard and enhanced models)"""
        self.use_enhanced = use_enhanced and ENHANCED_AVAILABLE
        
        if self.use_enhanced:
            print("🔧 Loading Enhanced Threat Detector (ML + Pattern Matching)")
            try:
                self.enhanced_detector = EnhancedThreatDetector(model_path)
                print(f"✅ Enhanced model loaded from: {model_path}")
            except Exception as e:
                print(f"❌ Failed to load enhanced model, falling back to standard: {e}")
                self.use_enhanced = False
        
        if not self.use_enhanced:
            print("🤖 Loading Standard ML Model")
            try:
                model_data = joblib.load(model_path)
                self.model = model_data['model']
                self.vectorizer = model_data['vectorizer']
                print(f"✅ Standard model loaded from: {model_path}")
            except Exception as e:
                print(f"❌ Failed to load model: {e}")
                raise
    
    def predict_log(self, log_text: str) -> Dict[str, Any]:
        """Make prediction on a single log entry (supports both enhanced and standard models)"""
        if self.use_enhanced:
            # Use enhanced detector (ML + patterns)
            result = self.enhanced_detector.predict_log(log_text)
            return {
                'prediction': result['prediction'],
                'threat_probability': result['threat_probability'],
                'benign_probability': 1.0 - result['threat_probability'],
                'is_threat': result['is_threat'],
                'confidence': result['confidence'],
                'enhanced': True,
                'ml_only_prob': result.get('ml_threat_probability', result['threat_probability']),
                'enhancement_applied': result.get('enhancement_applied', False)
            }
        else:
            # Use standard ML model
            text_features = self.vectorizer.transform([log_text]).toarray()
            prediction = self.model.predict(text_features)[0]
            probabilities = self.model.predict_proba(text_features)[0]
            return {
                'prediction': int(prediction),
                'threat_probability': float(probabilities[1]),
                'benign_probability': float(probabilities[0]),
                'is_threat': bool(prediction == 1),
                'confidence': float(max(probabilities)),
                'enhanced': False,
                'ml_only_prob': float(probabilities[1]),
                'enhancement_applied': False
            }
    
    def test_realistic_threat_logs(self) -> List[Dict]:
        """Test against realistic threat-related logs"""
        
        threat_logs = [
            # Real system compromise logs from user (previously missed)
            "Oct 11 13:45:01 sshd[2541]: Failed password for invalid user admin from 103.20.10.5 port 51234 ssh2",
            "Oct 11 14:02:15 sudo: user root : TTY=pts/0 ; PWD=/home/user ; COMMAND=/usr/bin/python /tmp/revshell.py",
            "Oct 11 15:10:30 kernel: Audit: type=1300 msg=audit(1665501030.123:456): arch=c000003e syscall=42 success=yes exit=0 a0=3 a1=7fffb7a421a0 a2=10 a3=7fffb7a41230 items=1 ppid=1 uid=1001 auid=1001 ses=2 msg='comm=\"nc\" exe=\"/bin/nc\" path=\"/tmp/exfil.tar.gz\"'",
            "Oct 11 17:01:10 useradd: new user: name=backdoor_user, UID=1005, GID=1005, home=/home/backdoor_user, shell=/bin/bash",
            
            # Additional SSH attacks
            "Oct 12 08:15:42 sshd[3421]: Failed password for root from 45.67.89.123 port 22 ssh2",
            "Oct 12 08:16:01 sshd[3425]: Failed password for invalid user test from 45.67.89.123 port 22 ssh2",
            "Oct 12 09:22:15 auth.log: Failed password for admin from 192.168.1.200 port 2222 ssh2",
            
            # Privilege escalation attempts
            "Oct 12 10:30:45 sudo: hacker : TTY=pts/2 ; PWD=/tmp ; USER=root ; COMMAND=/bin/bash /tmp/exploit.sh",
            "Oct 12 11:15:20 sudo: attacker : authentication failure ; TTY=pts/1 ; PWD=/home/attacker ; USER=root ; COMMAND=/bin/su",
            "Oct 12 12:05:33 su: FAILED SU (to root) alice on pts/0",
            
            # Suspicious process execution
            "Oct 12 13:45:12 kernel: audit: type=1309 msg=audit(1665502512.456:789): comm=\"nc\" exe=\"/bin/nc\" args=\"-l -p 4444 -e /bin/bash\"",
            "Oct 12 14:20:35 systemd: Started suspicious-service - /tmp/backdoor.py running on port 8080",
            "Oct 12 15:10:48 process: python3 /var/tmp/download_and_execute.py executing with PID 12345",
            
            # Network-based attacks
            "Oct 12 16:30:22 iptables: BLOCKED: IN=eth0 OUT= SRC=198.51.100.10 DST=192.168.1.50 LEN=60 PROTO=TCP SPT=1234 DPT=22",
            "Oct 12 17:45:18 snort: [1:2019401:3] ET SCAN Suspicious inbound to mySQL port 3306 [Classification: Potentially Bad Traffic]",
            "Oct 12 18:22:07 wireshark: TCP connection to known C&C server 203.0.113.50:443 detected",
            
            # File system manipulation
            "Oct 12 19:15:33 audit: type=1300 msg=audit(1665509733.123:999): syscall=2 success=yes exit=3 a0=7fff12345678 comm=\"cp\" exe=\"/bin/cp\" path=\"/etc/shadow\"",
            "Oct 12 20:30:55 file_monitor: /etc/passwd modified by process with PID 6789 (unknown binary)",
            "Oct 12 21:45:12 tripwire: File integrity violation - /bin/ls checksum changed unexpectedly",
            
            # Real CVE mentions and exploits
            "2024-01-15 ERROR: CVE-2023-4911 buffer overflow detected in glibc dynamic loader",
            "ALERT: Possible CVE-2023-38408 SSH forwarding vulnerability exploitation attempt",
            "SECURITY: CVE-2023-20198 Cisco IOS XE web UI privilege escalation detected",
            "CRITICAL: Log4j vulnerability CVE-2021-44228 exploitation detected in application logs",
            "EXPLOIT: CVE-2023-22515 Confluence privilege escalation attempt from IP 172.16.1.100",
            
            # Web application attacks
            "403 Forbidden: SQL injection attempt blocked - UNION SELECT detected in user input",
            "WAF BLOCK: Cross-site scripting attempt - <script>alert('xss')</script> in form field",
            "INTRUSION: Directory traversal attack - ../../etc/passwd requested",
            "WEB: Command injection detected - ; cat /etc/passwd appended to form parameter",
            "API: Deserialization attack blocked - malicious Java object in POST request",
            
            # Malware and suspicious activities
            "MALWARE: Suspicious PowerShell execution - encoded command detected",
            "ANTIVIRUS: Trojan.Win32.Generic detected in file C:\\temp\\suspicious.exe",
            "EDR: Process hollowing detected - legitimate process replaced with malicious code",
            "BEHAVIOR: Ransomware activity suspected - mass file encryption detected",
            
            # Network security events
            "IDS ALERT: Suspicious network traffic from 192.168.1.100 - possible data exfiltration",
            "FIREWALL: Blocked connection attempt to known malicious IP 198.51.100.5",
            "DNS SINKHOLE: Malware callback to evil.com blocked",
            "DLP: Sensitive data exfiltration attempt blocked - SSN pattern in outbound traffic",
            
            # System compromise indicators
            "AUDIT: Unauthorized privilege escalation - user 'guest' attempted sudo access",
            "FILE INTEGRITY: Critical system file modified - /etc/passwd checksum mismatch",
            "PROCESS: Suspicious process spawned - nc.exe -l -p 4444 detected",
            "REGISTRY: Suspicious Windows registry modification - Run key altered for persistence",
            
            # Application security
            "APPLICATION: Deserialization attack detected in Java application",
            "API SECURITY: Rate limiting triggered - 1000 requests/sec from single IP",
            "AUTHENTICATION: Brute force attack detected - 50 failed login attempts",
            "JWT: Token manipulation detected - signature verification failed for user session"
        ]
        
        print("🔍 Testing against realistic THREAT logs:")
        print("="*60)
        
        results = []
        enhanced_count = 0
        for i, log in enumerate(threat_logs):
            result = self.predict_log(log)
            results.append({**result, 'log_text': log, 'expected': 1})
            
            # Track enhancement usage
            if result.get('enhancement_applied', False):
                enhanced_count += 1
            
            # Enhanced status indicator
            if self.use_enhanced:
                if result.get('enhancement_applied', False):
                    enhancement_status = "🔧"
                    ml_vs_enhanced = f"ML:{result['ml_only_prob']:.3f}→{result['threat_probability']:.3f}"
                else:
                    enhancement_status = "🤖"
                    ml_vs_enhanced = f"ML:{result['threat_probability']:.3f}"
            else:
                enhancement_status = "🤖"
                ml_vs_enhanced = f"ML:{result['threat_probability']:.3f}"
            
            status = "✅ CORRECT" if result['is_threat'] else "❌ MISSED"
            print(f"{i+1:2d}. {status} {enhancement_status} | {ml_vs_enhanced} | {log[:50]}...")
        
        if self.use_enhanced:
            print(f"\n🔧 Enhancement applied to {enhanced_count}/{len(threat_logs)} logs ({enhanced_count/len(threat_logs):.1%})")
        
        return results
    
    def test_realistic_benign_logs(self) -> List[Dict]:
        """Test against realistic benign system logs"""
        
        benign_logs = [
            # Real normal system logs from user
            "Oct 11 08:00:05 kernel: Initializing cgroup subsys cpuset",
            "Oct 11 09:15:20 sshd[1200]: Accepted password for regular_user from 192.168.1.5 port 45000 ssh2",
            "Oct 11 10:30:00 CRON[450]: (root) CMD (command -v lsb_release >/dev/null && lsb_release -a)",
            "Oct 11 13:05:30 rsyslogd: [origin software=\"rsyslogd\" swVersion=\"8.2102.0\" x-pid=\"700\" x-info=\"https://www.rsyslog.com\"] rsyslogd started.",
            
            # Additional normal SSH activities
            "Oct 12 08:00:15 sshd[1001]: Accepted publickey for developer from 192.168.1.10 port 22 ssh2",
            "Oct 12 09:30:22 sshd[1150]: pam_unix(sshd:session): session opened for user admin by (uid=0)",
            "Oct 12 10:15:33 sshd[1200]: pam_unix(sshd:session): session closed for user admin",
            
            # Legitimate sudo usage
            "Oct 12 11:20:45 sudo: admin : TTY=pts/0 ; PWD=/home/admin ; USER=root ; COMMAND=/usr/bin/apt update",
            "Oct 12 12:05:18 sudo: developer : TTY=pts/1 ; PWD=/var/log ; USER=root ; COMMAND=/bin/cat /var/log/apache2/error.log",
            "Oct 12 13:45:22 sudo: sysadmin : TTY=pts/2 ; PWD=/etc ; USER=root ; COMMAND=/bin/systemctl restart nginx",
            
            # Normal system operations
            "2024-01-15 INFO: System startup completed successfully in 45.2 seconds",
            "CRON: Daily backup job completed - 15.2GB archived to /backup/daily_20240115.tar.gz",
            "DHCP: Lease renewed for client MAC 00:1B:44:11:3A:B7 - IP 192.168.1.150",
            "DNS: Resolved domain google.com to 142.250.190.14",
            "NTP: Clock synchronized with time server pool.ntp.org",
            
            # User activities
            "AUTH: User john.doe@company.com logged in successfully from 192.168.1.45",
            "SESSION: User session timeout - user inactive for 30 minutes",
            "FILE: Document upload completed - quarterly_report.pdf (2.3MB)",
            "PRINT: Print job submitted by user 'accounting' - invoice_template.pdf",
            "LOGIN: Successful login for user alice from workstation WS-001",
            
            # Application operations
            "DATABASE: Connection pool initialized - 10 connections to prod_db",
            "WEB: HTTP 200 GET /api/users/profile - response time 125ms",
            "EMAIL: Message sent successfully to customer@example.com",
            "CACHE: Redis cache cleared - 1,247 keys invalidated",
            "API: GET /api/v1/health - Status: 200 OK, Response time: 45ms",
            
            # Maintenance activities
            "MAINTENANCE: Log rotation completed - archived 5 files, freed 250MB",
            "UPDATE: Software patch applied successfully - Apache 2.4.52 to 2.4.54",
            "MONITOR: Health check passed - all services responding normally",
            "BACKUP: Incremental backup completed - 2.1GB processed in 8 minutes",
            "CLEANUP: Temporary files removed - freed 500MB disk space",
            
            # Network normal activities
            "NETWORK: Interface eth0 link up - 1Gbps full duplex",
            "VPN: Client connected from remote office - user: remote_worker",
            "LOAD_BALANCER: Server pool health check - all 4 servers healthy",
            "FIREWALL: Rule updated - allowing HTTPS traffic on port 443",
            
            # Database operations
            "SQL: Query executed successfully - SELECT * FROM users WHERE active=1 (15ms)",
            "TRANSACTION: Payment processed - Order #12345 for $99.99",
            "MIGRATION: Database schema updated - added index on user_activity.timestamp",
            "BACKUP: Database backup completed - 5.2GB written to /backup/db_20241011.sql",
            
            # System monitoring
            "MONITOR: CPU usage: 15%, Memory usage: 45%, Disk usage: 60%",
            "PERFORMANCE: Average response time: 150ms, Error rate: 0.01%",
            "ALERT: System performance within normal parameters",
            "CAPACITY: Current connections: 150/1000, Load average: 0.85",
            
            # Security-related but benign
            "SECURITY_SCAN: Vulnerability scan completed - no critical issues found",
            "AUDIT: Quarterly security review completed - compliance maintained",
            "CERTIFICATE: SSL certificate renewed successfully for domain.com",
            "FIREWALL: Security policy updated - blocked known malicious IPs",
            
            # Legitimate file operations
            "FILE: Logrotate completed for /var/log/messages - compressed 10MB to 1MB",
            "STORAGE: Disk cleanup completed - removed old log files, freed 2GB",
            "ARCHIVE: Monthly archive created - 50GB data moved to cold storage"
        ]
        
        print("\n🔍 Testing against realistic BENIGN logs:")
        print("="*60)
        
        results = []
        false_positive_count = 0
        enhanced_count = 0
        
        for i, log in enumerate(benign_logs):
            result = self.predict_log(log)
            results.append({**result, 'log_text': log, 'expected': 0})
            
            # Track false positives and enhancement usage
            if result['is_threat']:
                false_positive_count += 1
            if result.get('enhancement_applied', False):
                enhanced_count += 1
            
            # Enhanced status indicator
            if self.use_enhanced:
                if result.get('enhancement_applied', False):
                    enhancement_status = "🔧"
                    ml_vs_enhanced = f"ML:{result['ml_only_prob']:.3f}→{result['threat_probability']:.3f}"
                else:
                    enhancement_status = "🤖"
                    ml_vs_enhanced = f"ML:{result['threat_probability']:.3f}"
            else:
                enhancement_status = "🤖"
                ml_vs_enhanced = f"ML:{result['threat_probability']:.3f}"
            
            status = "✅ CORRECT" if not result['is_threat'] else "❌ FALSE POSITIVE"
            print(f"{i+1:2d}. {status} {enhancement_status} | {ml_vs_enhanced} | {log[:50]}...")
        
        if self.use_enhanced:
            print(f"\n🔧 Enhancement applied to {enhanced_count}/{len(benign_logs)} logs ({enhanced_count/len(benign_logs):.1%})")
        print(f"⚠️  False positives: {false_positive_count}/{len(benign_logs)} ({false_positive_count/len(benign_logs):.1%})")
        
        return results
    
    def test_edge_cases(self) -> List[Dict]:
        """Test edge cases and potential overfitting scenarios"""
        
        edge_cases = [
            # CVE mentions in benign contexts
            "PATCH: Security update applied - fixed CVE-2023-1234 vulnerability",
            "DOCUMENTATION: CVE-2022-5678 has been documented in security knowledge base",
            "TRAINING: Security team reviewed CVE-2023-9999 during monthly meeting",
            
            # Technical terms that might confuse the model
            "DATABASE: Connection timeout error - max_connections exceeded",
            "APPLICATION: Memory allocation failed - out of memory exception",
            "NETWORK: Packet loss detected on interface - investigating connectivity",
            
            # Log4j mentions (should be high threat)
            "CRITICAL: Log4j vulnerability CVE-2021-44228 exploitation detected",
            "INFO: Log4j library updated to version 2.17.1 - CVE-2021-44228 patched",
            
            # Mixed signals
            "SECURITY SCAN: No vulnerabilities found - system clean",
            "VULNERABILITY ASSESSMENT: Completed scan of 500 systems - 0 critical issues",
            "PENETRATION TEST: Authorized security testing in progress",
            
            # Very short logs
            "Error 404",
            "Connection timeout",
            "Service started",
            "User logout",
            
            # Very long logs
            "APPLICATION DEBUG: Processing user request with parameters: user_id=12345, action=view_profile, session_token=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567890abcdef123456789012345678901234567890123456789012345678901234567890 timestamp=2024-01-15T10:30:45.123Z ip_address=192.168.1.100 user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' referer=https://app.company.com/dashboard response_time=234ms status=success"
        ]
        
        print("\n🔍 Testing EDGE CASES and potential overfitting scenarios:")
        print("="*60)
        
        results = []
        for i, log in enumerate(edge_cases):
            result = self.predict_log(log)
            results.append({**result, 'log_text': log, 'expected': None})  # No clear expected result
            
            threat_level = "HIGH" if result['threat_probability'] > 0.7 else "MEDIUM" if result['threat_probability'] > 0.3 else "LOW"
            print(f"{i+1:2d}. {threat_level:6} | Threat: {result['threat_probability']:.3f} | {log[:50]}...")
        
        return results
    
    def calculate_performance_metrics(self, results: List[Dict]) -> Dict[str, float]:
        """Calculate performance metrics for test results"""
        
        # Filter out edge cases (no expected result)
        labeled_results = [r for r in results if r.get('expected') is not None]
        
        if not labeled_results:
            return {}
        
        true_labels = [r['expected'] for r in labeled_results]
        predictions = [r['prediction'] for r in labeled_results]
        probabilities = [r['threat_probability'] for r in labeled_results]
        
        # Basic metrics
        correct_predictions = sum(1 for true, pred in zip(true_labels, predictions) if true == pred)
        accuracy = correct_predictions / len(labeled_results)
        
        # True/False Positives/Negatives
        tp = sum(1 for true, pred in zip(true_labels, predictions) if true == 1 and pred == 1)
        tn = sum(1 for true, pred in zip(true_labels, predictions) if true == 0 and pred == 0)
        fp = sum(1 for true, pred in zip(true_labels, predictions) if true == 0 and pred == 1)
        fn = sum(1 for true, pred in zip(true_labels, predictions) if true == 1 and pred == 0)
        
        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'true_positives': tp,
            'true_negatives': tn,
            'false_positives': fp,
            'false_negatives': fn,
            'total_samples': len(labeled_results)
        }
    
    def run_comprehensive_test(self):
        """Run comprehensive robustness testing"""
        print("🧪 COMPREHENSIVE MODEL ROBUSTNESS TEST")
        print("="*60)
        print("Testing for overfitting and real-world performance...")
        
        # Display actual training metrics first
        try:
            model_data = joblib.load("models/improved_threat_model.joblib")
            training_results = model_data.get('training_results', {}).get('ImprovedModel', {})
            print(f"\n📊 BASELINE TRAINING PERFORMANCE:")
            print(f"Training Date: {model_data.get('trained_date', 'Unknown')}")
            print(f"Accuracy:  {training_results.get('accuracy', 0):.3f}")
            print(f"Precision: {training_results.get('precision', 0):.3f}")
            print(f"Recall:    {training_results.get('recall', 0):.3f}")
            print(f"F1-Score:  {training_results.get('f1_score', 0):.3f}")
            print(f"ROC-AUC:   {training_results.get('roc_auc', 0):.3f}")
        except:
            print("\n⚠️  Could not load training metrics from model file")
        
        # Test different categories
        threat_results = self.test_realistic_threat_logs()
        benign_results = self.test_realistic_benign_logs()
        edge_results = self.test_edge_cases()
        
        # Combine all labeled results
        all_results = threat_results + benign_results
        
        # Track enhancement usage if enhanced model
        total_enhancements = 0
        if self.use_enhanced:
            for result in all_results:
                if result.get('enhancement_applied', False):
                    total_enhancements += 1
        
        # Calculate performance metrics
        metrics = self.calculate_performance_metrics(all_results)
        
        print(f"\n📊 REAL-WORLD PERFORMANCE SUMMARY:")
        print("="*60)
        print(f"Total Test Samples: {metrics.get('total_samples', 0)}")
        print(f"Accuracy: {metrics.get('accuracy', 0):.3f}")
        print(f"Precision: {metrics.get('precision', 0):.3f}")
        print(f"Recall: {metrics.get('recall', 0):.3f}")
        print(f"F1-Score: {metrics.get('f1_score', 0):.3f}")
        
        print(f"\nConfusion Matrix:")
        print(f"True Negatives:  {metrics.get('true_negatives', 0):3d} | False Positives: {metrics.get('false_positives', 0):3d}")
        print(f"False Negatives: {metrics.get('false_negatives', 0):3d} | True Positives:  {metrics.get('true_positives', 0):3d}")
        
        # Analyze potential issues
        print(f"\n🔍 POTENTIAL ISSUES ANALYSIS:")
        print("="*60)
        
        threat_accuracy = sum(1 for r in threat_results if r['is_threat']) / len(threat_results)
        benign_accuracy = sum(1 for r in benign_results if not r['is_threat']) / len(benign_results)
        
        print(f"Threat Detection Rate: {threat_accuracy:.3f} ({int(threat_accuracy * len(threat_results))}/{len(threat_results)})")
        print(f"Benign Recognition Rate: {benign_accuracy:.3f} ({int(benign_accuracy * len(benign_results))}/{len(benign_results)})")
        
        if threat_accuracy < 0.7:
            print("⚠️  WARNING: Low threat detection rate - model may be underfit")
        if benign_accuracy < 0.8:
            print("⚠️  WARNING: High false positive rate - model may be overfit to threat patterns")
        if threat_accuracy > 0.95 and benign_accuracy > 0.95:
            print("✅ EXCELLENT: Model shows good generalization")
        
        # Check for overfitting signs - get actual training metrics
        try:
            model_data = joblib.load("models/improved_threat_model.joblib")
            training_results = model_data.get('training_results', {}).get('ImprovedModel', {})
            training_f1 = training_results.get('f1_score', 0.0)
            training_accuracy = training_results.get('accuracy', 0.0)
            training_precision = training_results.get('precision', 0.0)
            training_recall = training_results.get('recall', 0.0)
        except:
            training_f1 = 0.768  # Fallback to actual known value
            training_accuracy = 0.736
            training_precision = 0.694
            training_recall = 0.860
        
        test_f1 = metrics.get('f1_score', 0)
        performance_drop = training_f1 - test_f1
        
        print(f"\nOverfitting Analysis:")
        print(f"Training F1-Score: {training_f1:.3f}")
        print(f"Real-world F1-Score: {test_f1:.3f}")
        print(f"Performance Drop: {performance_drop:.3f}")
        
        print(f"\nDetailed Training vs Test Comparison:")
        print(f"Training Accuracy:  {training_accuracy:.3f} | Test Accuracy:  {metrics.get('accuracy', 0):.3f}")
        print(f"Training Precision: {training_precision:.3f} | Test Precision: {metrics.get('precision', 0):.3f}")
        print(f"Training Recall:    {training_recall:.3f} | Test Recall:    {metrics.get('recall', 0):.3f}")
        
        if performance_drop > 0.10:
            print("🔴 SIGNIFICANT OVERFITTING: Model performs much worse on real data")
        elif performance_drop > 0.05:
            print("🟡 MILD OVERFITTING: Some performance degradation on real data")
        elif performance_drop < -0.05:
            print("🟢 EXCELLENT GENERALIZATION: Model performs better on test data than training!")
        else:
            print("🟢 GOOD GENERALIZATION: Model performs well on unseen data")
        
        return {
            'threat_results': threat_results,
            'benign_results': benign_results,
            'edge_results': edge_results,
            'metrics': metrics,
            'threat_detection_rate': threat_accuracy,
            'benign_recognition_rate': benign_accuracy,
            'performance_drop': performance_drop,
            'enhanced_usage': (total_enhancements / len(all_results)) if self.use_enhanced else 0.0
        }

def main():
    """Main testing function with support for enhanced model"""
    print("🚀 ForensIQ Threat Detection Model Testing")
    print("="*50)
    
    # Try enhanced model first, fallback to standard
    try:
        tester = ModelRobustnessTester(use_enhanced=True)
        model_type = "Enhanced (ML + Patterns)"
    except:
        print("⚠️  Enhanced model not available, using standard ML model")
        tester = ModelRobustnessTester(use_enhanced=False)
        model_type = "Standard ML"
    
    print(f"📊 Testing {model_type} Model")
    
    results = tester.run_comprehensive_test()
    
    print(f"\n🎯 FINAL RECOMMENDATION:")
    
    if tester.use_enhanced:
        # Enhanced model recommendations
        if (results['performance_drop'] < 0.02 and 
            results['metrics'].get('f1_score', 0) > 0.75 and 
            results['threat_detection_rate'] > 0.80):
            print("🏆 EXCELLENT: Enhanced model ready for production deployment!")
        elif (results['performance_drop'] < 0.08 and 
              results['metrics'].get('f1_score', 0) > 0.65):
            print("✅ GOOD: Enhanced model shows strong performance!")
        elif results['metrics'].get('f1_score', 0) > 0.60:
            print("⚠️  ACCEPTABLE: Enhanced model needs minor tuning but usable for demo")
        else:
            print("🔴 NEEDS IMPROVEMENT: Enhanced model requires significant work")
        
        print(f"📈 Enhancement Usage: {results['enhanced_usage']:.1%} of tests used pattern matching")
    else:
        # Standard model recommendations - more realistic thresholds
        if (results['performance_drop'] < 0.02 and 
            results['metrics'].get('f1_score', 0) > 0.70):
            print("✅ Model is ready for production deployment!")
        elif (results['performance_drop'] < 0.08 and 
              results['metrics'].get('f1_score', 0) > 0.60):
            print("⚠️  Model needs minor tuning but is acceptable for demo")
        else:
            print("🔴 Model needs significant improvement before deployment")
        
        # Specific guidance
        if results['threat_detection_rate'] < 0.70:
            print("💡 SUGGESTION: Consider lowering detection threshold or adding more threat patterns")
        if results['benign_recognition_rate'] < 0.85:
            print("💡 SUGGESTION: Review false positive cases to reduce noise")
    
    return results

if __name__ == "__main__":
    main()