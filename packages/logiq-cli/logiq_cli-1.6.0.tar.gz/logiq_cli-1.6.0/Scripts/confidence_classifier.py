"""
Confidence-Based Log Classification
Classify logs with confidence scores and flags
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path

def classify_with_confidence(logs):
    """Classify logs with confidence scores and flags"""
    print("🎯 Confidence-Based Log Classification")
    print("="*50)
    
    # Load model
    models_dir = Path("models")
    model_files = list(models_dir.glob("quick_threat_model_*.joblib"))
    latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
    
    model_data = joblib.load(latest_model)
    model = model_data['model']
    vectorizer = model_data['vectorizer']
    threshold = model_data['optimal_threshold']
    
    print(f"📥 Using model: {latest_model.name}")
    print(f"🎯 Threshold: {threshold:.3f}")
    
    # Transform logs
    X = vectorizer.transform(logs).toarray()
    y_prob = model.predict_proba(X)[:, 1]
    
    # Classification results with confidence
    results = []
    
    for i, log in enumerate(logs):
        prob = y_prob[i]
        
        # Determine classification and confidence based on new logic:
        # - Low confidence THREAT → Send to RAG (uncertain)
        # - High/Medium confidence → Non-threat, skip RAG (confident it's benign)
        
        if prob >= threshold:
            # Above threshold - potential threat
            if prob >= 0.7:
                # High probability threat - high confidence threat
                classification = "THREAT"
                confidence_level = "HIGH" 
                confidence_score = 80 + (prob - 0.7) * 20  # 80-100
                action = "SEND_TO_RAG"
            elif prob >= 0.55:
                # Medium probability threat - medium confidence threat  
                classification = "THREAT"
                confidence_level = "MEDIUM"
                confidence_score = 60 + (prob - 0.55) * 20  # 60-80
                action = "SEND_TO_RAG"
            else:
                # Low probability threat - LOW CONFIDENCE (uncertain, needs RAG)
                classification = "THREAT"
                confidence_level = "LOW"
                confidence_score = 30 + (prob - threshold) * 30  # 30-60
                action = "SEND_TO_RAG"  # Low confidence threats need RAG analysis
        else:
            # Below threshold - likely benign
            if prob <= 0.2:
                # Very low probability - HIGH CONFIDENCE benign
                classification = "BENIGN"
                confidence_level = "HIGH"
                confidence_score = 90 + (0.2 - prob) * 10  # 90-100
                action = "SKIP_RAG"  # High confidence benign - filter out
            elif prob <= 0.35:
                # Low probability - MEDIUM CONFIDENCE benign
                classification = "BENIGN" 
                confidence_level = "MEDIUM"
                confidence_score = 70 + (0.35 - prob) * 20  # 70-90
                action = "SKIP_RAG"  # Medium confidence benign - filter out
            else:
                # Close to threshold - treat as uncertain threat (send to RAG)
                classification = "THREAT"
                confidence_level = "LOW"
                confidence_score = 40 + (threshold - prob) * 20  # Variable based on distance from threshold
                action = "SEND_TO_RAG"  # Uncertain cases go to RAG
        
        # Risk flags based on new logic
        risk_flags = []
        
        if classification == "THREAT":
            if confidence_level == "HIGH":
                risk_flags.append("HIGH_CONFIDENCE_THREAT")
            elif confidence_level == "MEDIUM":
                risk_flags.append("MEDIUM_CONFIDENCE_THREAT") 
            else:
                risk_flags.append("LOW_CONFIDENCE_THREAT")
                risk_flags.append("UNCERTAIN_NEEDS_RAG")
        else:  # BENIGN
            if confidence_level == "HIGH":
                risk_flags.append("HIGH_CONFIDENCE_BENIGN")
            else:
                risk_flags.append("MEDIUM_CONFIDENCE_BENIGN")
        
        # Priority level based on confidence and classification
        if classification == "THREAT":
            if confidence_level == "HIGH":
                priority = "P1_HIGH_CONFIDENCE_THREAT"
            elif confidence_level == "MEDIUM":
                priority = "P2_MEDIUM_CONFIDENCE_THREAT"
            else:
                priority = "P3_LOW_CONFIDENCE_UNCERTAIN"
        else:  # BENIGN with high/medium confidence
            priority = "P4_CONFIDENT_BENIGN"
        
        result = {
            'log_id': i + 1,
            'log_text': log,
            'threat_probability': round(prob, 4),
            'classification': classification,
            'confidence_score': round(confidence_score, 1),
            'confidence_level': confidence_level,
            'priority': priority,
            'risk_flags': risk_flags,
            'rag_action': action,
            'recommendation': get_recommendation(prob, confidence_score, classification)
        }
        
        results.append(result)
    
    return results

def get_recommendation(prob, confidence_score, classification):
    """Get action recommendation based on new confidence logic"""
    if classification == "THREAT":
        if confidence_score >= 80:
            return "HIGH_CONFIDENCE_THREAT_INVESTIGATE"
        elif confidence_score >= 60:
            return "MEDIUM_CONFIDENCE_THREAT_ANALYZE"
        else:
            return "LOW_CONFIDENCE_UNCERTAIN_RAG_NEEDED"
    else:  # BENIGN
        if confidence_score >= 80:
            return "HIGH_CONFIDENCE_BENIGN_FILTER_OUT"
        else:
            return "MEDIUM_CONFIDENCE_BENIGN_FILTER_OUT"

def print_classification_results(results):
    """Print formatted classification results"""
    print(f"\n📊 Classification Results")
    print("="*100)
    
    for result in results:
        print(f"\n🔍 Log {result['log_id']:2d}: {result['log_text'][:70]}...")
        print(f"   📈 Threat Probability: {result['threat_probability']:.4f}")
        print(f"   🎯 Classification: {result['classification']}")
        print(f"   📊 Confidence: {result['confidence_score']:.1f}% ({result['confidence_level']})")
        print(f"   🚨 Priority: {result['priority']}")
        
        if result['risk_flags']:
            flags_str = ', '.join(result['risk_flags'])
            print(f"   🏷️  Flags: {flags_str}")
        
        print(f"   📤 RAG Action: {result['rag_action']}")
        print(f"   💡 Recommendation: {result['recommendation']}")

def generate_summary_stats(results):
    """Generate summary statistics based on new confidence logic"""
    print(f"\n📈 Summary Statistics")
    print("="*50)
    
    total_logs = len(results)
    threat_logs = sum(1 for r in results if r['classification'] == 'THREAT')
    benign_logs = total_logs - threat_logs
    
    # Confidence distribution
    high_conf = sum(1 for r in results if r['confidence_level'] == 'HIGH')
    medium_conf = sum(1 for r in results if r['confidence_level'] == 'MEDIUM')
    low_conf = sum(1 for r in results if r['confidence_level'] == 'LOW')
    
    # RAG actions
    send_to_rag = sum(1 for r in results if r['rag_action'] == 'SEND_TO_RAG')
    skip_rag = sum(1 for r in results if r['rag_action'] == 'SKIP_RAG')
    
    # New priority distribution
    p1_high_conf_threat = sum(1 for r in results if r['priority'] == 'P1_HIGH_CONFIDENCE_THREAT')
    p2_medium_conf_threat = sum(1 for r in results if r['priority'] == 'P2_MEDIUM_CONFIDENCE_THREAT')
    p3_low_conf_uncertain = sum(1 for r in results if r['priority'] == 'P3_LOW_CONFIDENCE_UNCERTAIN')
    p4_confident_benign = sum(1 for r in results if r['priority'] == 'P4_CONFIDENT_BENIGN')
    
    # Risk flags based on new logic
    high_conf_threats = sum(1 for r in results if 'HIGH_CONFIDENCE_THREAT' in r['risk_flags'])
    medium_conf_threats = sum(1 for r in results if 'MEDIUM_CONFIDENCE_THREAT' in r['risk_flags'])
    low_conf_threats = sum(1 for r in results if 'LOW_CONFIDENCE_THREAT' in r['risk_flags'])
    high_conf_benign = sum(1 for r in results if 'HIGH_CONFIDENCE_BENIGN' in r['risk_flags'])
    medium_conf_benign = sum(1 for r in results if 'MEDIUM_CONFIDENCE_BENIGN' in r['risk_flags'])
    
    print(f"📊 Classification Breakdown:")
    print(f"   🚨 Threats: {threat_logs:2d}/{total_logs} ({threat_logs/total_logs*100:.1f}%)")
    print(f"   ✅ Benign:  {benign_logs:2d}/{total_logs} ({benign_logs/total_logs*100:.1f}%)")
    
    print(f"\n📊 Confidence Distribution:")
    print(f"   � High:      {high_conf:2d}/{total_logs} ({high_conf/total_logs*100:.1f}%)")
    print(f"   � Medium:    {medium_conf:2d}/{total_logs} ({medium_conf/total_logs*100:.1f}%)")
    print(f"   � Low:       {low_conf:2d}/{total_logs} ({low_conf/total_logs*100:.1f}%)")
    
    print(f"\n🎯 RAG Pre-filtering Results:")
    print(f"   📤 Send to RAG: {send_to_rag:2d}/{total_logs} ({send_to_rag/total_logs*100:.1f}%)")
    print(f"   ✅ Filter out:  {skip_rag:2d}/{total_logs} ({skip_rag/total_logs*100:.1f}%)")
    
    print(f"\n🚨 Threat Analysis by Confidence:")
    print(f"   🔴 High confidence threats:   {high_conf_threats:2d} (immediate investigation)")
    print(f"   🟡 Medium confidence threats: {medium_conf_threats:2d} (standard analysis)")
    print(f"   ⚪ Low confidence (uncertain): {low_conf_threats:2d} (needs RAG analysis)")
    
    print(f"\n✅ Benign Analysis by Confidence:")
    print(f"   🟢 High confidence benign:   {high_conf_benign:2d} (safe to filter)")
    print(f"   🔵 Medium confidence benign: {medium_conf_benign:2d} (safe to filter)")
    
    print(f"\n💡 RAG Efficiency:")
    efficiency = skip_rag / total_logs * 100
    print(f"   🎯 Filtering efficiency: {efficiency:.1f}% of logs filtered out")
    
    # Overall confidence rating
    avg_confidence = np.mean([r['confidence_score'] for r in results])
    
    if avg_confidence >= 80:
        overall_rating = "EXCELLENT"
    elif avg_confidence >= 70:
        overall_rating = "GOOD"
    elif avg_confidence >= 60:
        overall_rating = "FAIR"
    else:
        overall_rating = "POOR"
    
    print(f"\n🎯 Overall Model Performance:")
    print(f"   Average Confidence: {avg_confidence:.1f}%")
    print(f"   Overall Rating: {overall_rating}")

def main():
    """Main function with test logs"""
    
    # Test logs - mix of obvious threats, benign, and uncertain cases
    test_logs = [
        # Clear threats
        "Oct 11 13:45:01 sshd[2541]: Failed password for invalid user admin from 103.20.10.5 port 51234 ssh2",
        "Oct 11 14:02:15 sudo: user root : TTY=pts/0 ; PWD=/home/user ; COMMAND=/usr/bin/python /tmp/revshell.py",
        "Oct 11 15:10:30 kernel: Audit: syscall=42 comm=\"nc\" exe=\"/bin/nc\" path=\"/tmp/exfil.tar.gz\"",
        "Oct 11 17:01:10 useradd: new user: name=backdoor_user, UID=1005, shell=/bin/bash",
        
        # Clear benign
        "Oct 11 08:00:05 kernel: Initializing cgroup subsys cpuset",
        "Oct 11 09:15:20 sshd[1200]: Accepted password for regular_user from 192.168.1.5 port 45000 ssh2",
        "Oct 11 10:30:00 CRON[450]: (root) CMD (command -v lsb_release >/dev/null && lsb_release -a)",
        "Oct 11 13:05:30 rsyslogd: rsyslogd started",
        
        # Potentially uncertain
        "Oct 11 16:30:15 apache: 192.168.1.100 GET /admin/login HTTP/1.1 200",
        "Oct 11 18:45:22 firewall: ACCEPT TCP 10.0.0.5:22 -> 192.168.1.1:1234"
    ]
    
    print("🧪 Testing Confidence-Based Classification")
    
    # Classify logs
    results = classify_with_confidence(test_logs)
    
    # Print results
    print_classification_results(results)
    
    # Generate summary
    generate_summary_stats(results)
    
    print(f"\n💡 Usage Instructions:")
    print("="*30)
    print("📊 Confidence Scores (0-100):")
    print("   90-100: Very High Confidence")
    print("   70-89:  High Confidence") 
    print("   50-69:  Medium Confidence")
    print("   0-49:   Low Confidence")
    print("")
    print("🚨 Priority Levels:")
    print("   P1: Critical - Immediate action")
    print("   P2: High - Priority investigation")
    print("   P3: Medium - Standard analysis")
    print("   P4: Low - Monitor closely")
    print("   P5: Benign - Safe to ignore")

if __name__ == "__main__":
    main()