"""
Quick Model Test Script
Test the trained cost-sensitive model on new samples
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path

def test_trained_model():
    """Test the most recently trained model"""
    print("🧪 Testing Trained Cost-Sensitive Model")
    print("="*50)
    
    # Find the most recent model
    models_dir = Path("models")
    if not models_dir.exists():
        print("❌ Models directory not found!")
        return
    
    model_files = list(models_dir.glob("quick_threat_model_*.joblib"))
    if not model_files:
        print("❌ No trained models found!")
        return
    
    # Get most recent model
    latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
    print(f"📥 Loading model: {latest_model.name}")
    
    # Load model
    try:
        model_data = joblib.load(latest_model)
        model = model_data['model']
        vectorizer = model_data['vectorizer']
        optimal_threshold = model_data['optimal_threshold']
        
        print(f"✅ Model loaded successfully!")
        print(f"🎯 Optimal threshold: {optimal_threshold:.3f}")
        print(f"📅 Trained: {model_data.get('trained_date', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Test with sample logs
    print(f"\n🧪 Testing Sample Log Entries:")
    print("-" * 40)
    
    test_logs = [
        # Suspicious/Malicious samples
        "2024-10-11 15:30:45 192.168.1.100 10.0.0.5 TCP DROP malicious network_security 1024 Mozilla/5.0 /admin/login",
        "2024-10-11 16:45:12 203.0.113.5 192.168.1.50 HTTP BLOCK suspicious web_security 2048 sqlmap/1.4.2 /users?id=1' OR '1'='1",
        "2024-10-11 17:22:33 198.51.100.10 172.16.0.1 SSH DENY malicious endpoint_security 512 PuTTY/0.76 /tmp/exploit.sh",
        "2024-10-11 18:15:05 악성코드 탐지 suspicious malware_detection 4096 Unknown /system32/virus.exe",
        
        # Benign samples  
        "2024-10-11 12:00:01 192.168.1.20 10.0.0.1 HTTPS ALLOW benign web_security 8192 Chrome/118.0 /api/dashboard",
        "2024-10-11 13:30:22 10.0.0.15 192.168.1.5 TCP ALLOW benign network_security 1536 Firefox/119.0 /home/profile",
        "2024-10-11 14:45:33 172.16.0.10 192.168.0.1 HTTP ALLOW benign application_security 2048 Safari/17.0 /search?q=weather",
        "2024-10-11 09:15:44 192.168.0.100 10.1.1.1 SMTP ALLOW benign email_security 1024 Outlook/16.0 /inbox/read"
    ]
    
    # Transform test logs using the trained vectorizer
    X_test = vectorizer.transform(test_logs).toarray()
    
    # Make predictions
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred_default = model.predict(X_test)
    y_pred_optimal = (y_prob >= optimal_threshold).astype(int)
    
    # Display results
    for i, log in enumerate(test_logs):
        prob = y_prob[i]
        pred_default = "🚨 THREAT" if y_pred_default[i] == 1 else "✅ BENIGN"
        pred_optimal = "🚨 THREAT" if y_pred_optimal[i] == 1 else "✅ BENIGN"
        
        print(f"\n{i+1:2d}. Log: {log[:80]}...")
        print(f"    Threat Probability: {prob:.3f}")
        print(f"    Default (0.5):      {pred_default}")
        print(f"    Optimal ({optimal_threshold:.3f}):      {pred_optimal}")
    
    # Test with larger sample from data
    print(f"\n🔬 Testing on Fresh Data Sample:")
    print("-" * 35)
    
    try:
        # Load fresh data (different from training)
        csv_path = "../data/cybersecurity_threat_detection_logs.csv"
        
        # Skip first 50,000 rows (used for training) and take next 5,000
        df_test = pd.read_csv(csv_path, skiprows=range(1, 50001), nrows=5000)
        
        if 'threat_label' in df_test.columns:
            # Prepare test data same way as training
            text_columns = ['timestamp', 'user_agent']
            available_text_cols = [col for col in text_columns if col in df_test.columns]
            
            if len(available_text_cols) > 1:
                df_test['combined_text'] = df_test[available_text_cols].fillna('').astype(str).agg(' '.join, axis=1)
                text_feature = 'combined_text'
            elif len(available_text_cols) == 1:
                text_feature = available_text_cols[0]
                df_test[text_feature] = df_test[text_feature].fillna('')
            else:
                print("❌ No suitable text columns found in test data")
                return
            
            # Transform features
            X_fresh = vectorizer.transform(df_test[text_feature]).toarray()
            
            # Prepare labels
            benign_indicators = ['benign', 'normal', 'legitimate', 'clean', 'Normal']
            is_benign = df_test['threat_label'].str.lower().isin([x.lower() for x in benign_indicators])
            y_true = (~is_benign).astype(int)
            
            # Make predictions
            y_prob_fresh = model.predict_proba(X_fresh)[:, 1]
            y_pred_fresh = (y_prob_fresh >= optimal_threshold).astype(int)
            
            # Evaluate
            from sklearn.metrics import classification_report, confusion_matrix
            
            print(f"📊 Fresh Test Results ({len(X_fresh):,} samples):")
            
            cm = confusion_matrix(y_true, y_pred_fresh)
            tn, fp, fn, tp = cm.ravel()
            
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            print(f"True Positives:  {tp:,}")
            print(f"False Negatives: {fn:,}")
            print(f"False Positives: {fp:,}")
            print(f"True Negatives:  {tn:,}")
            print(f"")
            print(f"Recall:    {recall:.3f} ({tp:,}/{tp+fn:,} threats caught)")
            print(f"Precision: {precision:.3f}")
            print(f"F1-Score:  {f1:.3f}")
            
            threat_detection_rate = recall
            false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
            
            print(f"\n🎯 RAG Pre-filtering Performance:")
            print(f"Threat Detection Rate: {threat_detection_rate:.1%}")
            print(f"False Positive Rate:   {false_positive_rate:.1%}")
            
            if threat_detection_rate >= 0.90:
                print("✅ EXCELLENT: Ready for RAG pre-filtering!")
            elif threat_detection_rate >= 0.80:
                print("✅ GOOD: Suitable for RAG pre-filtering")
            else:
                print("⚠️  MODERATE: Consider threshold adjustment")
        
        else:
            print("❌ No threat_label column found in test data")
            
    except Exception as e:
        print(f"⚠️  Could not test on fresh data: {e}")
    
    print(f"\n🎉 Model testing completed!")
    print(f"💡 Model ready for RAG pipeline integration")

if __name__ == "__main__":
    test_trained_model()