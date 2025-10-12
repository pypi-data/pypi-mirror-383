"""
Quick Model Verification Test
Check if the test script is providing accurate results
"""

import joblib
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_model_info():
    """Load model and get training metadata"""
    model_path = "models/improved_threat_model.joblib"
    
    try:
        model_data = joblib.load(model_path)
        training_results = model_data.get('training_results', {}).get('ImprovedModel', {})
        
        print("📊 ACTUAL TRAINING RESULTS:")
        print("="*40)
        print(f"Accuracy:  {training_results.get('accuracy', 0):.3f}")
        print(f"Precision: {training_results.get('precision', 0):.3f}")
        print(f"Recall:    {training_results.get('recall', 0):.3f}")
        print(f"F1-Score:  {training_results.get('f1_score', 0):.3f}")
        print(f"ROC-AUC:   {training_results.get('roc_auc', 0):.3f}")
        print(f"Trained:   {model_data.get('trained_date', 'Unknown')}")
        
        return model_data, training_results
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None, None

def quick_test_samples():
    """Test a few clear samples to verify model behavior"""
    model_data, training_results = load_model_info()
    
    if not model_data:
        return
    
    model = model_data['model']
    vectorizer = model_data['vectorizer']
    
    # Clear threat samples
    threat_samples = [
        "Failed password for root from 192.168.1.100 port 22 ssh2",
        "sudo: hacker : COMMAND=/bin/bash /tmp/exploit.sh",
        "CVE-2021-44228 Log4j exploitation detected",
        "SQL injection attempt blocked - UNION SELECT detected"
    ]
    
    # Clear benign samples  
    benign_samples = [
        "System startup completed successfully",
        "User john.doe logged in successfully",
        "Backup job completed - 5GB archived",
        "HTTP 200 GET /api/health - 45ms"
    ]
    
    print(f"\n🧪 QUICK VERIFICATION TEST:")
    print("="*40)
    
    print("\n🚨 Testing THREAT samples:")
    threat_correct = 0
    for i, sample in enumerate(threat_samples):
        features = vectorizer.transform([sample]).toarray()
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1]  # Threat probability
        
        status = "✅ DETECTED" if prediction == 1 else "❌ MISSED"
        if prediction == 1:
            threat_correct += 1
            
        print(f"{i+1}. {status} | Prob: {probability:.3f} | {sample[:50]}...")
    
    print(f"\n✅ Testing BENIGN samples:")
    benign_correct = 0
    for i, sample in enumerate(benign_samples):
        features = vectorizer.transform([sample]).toarray()
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1]  # Threat probability
        
        status = "✅ CORRECT" if prediction == 0 else "❌ FALSE POS"
        if prediction == 0:
            benign_correct += 1
            
        print(f"{i+1}. {status} | Prob: {probability:.3f} | {sample[:50]}...")
    
    # Quick metrics
    total_correct = threat_correct + benign_correct
    total_samples = len(threat_samples) + len(benign_samples)
    accuracy = total_correct / total_samples
    
    print(f"\n📊 QUICK TEST RESULTS:")
    print("="*40)
    print(f"Threats detected: {threat_correct}/{len(threat_samples)} ({threat_correct/len(threat_samples):.1%})")
    print(f"Benign correct:   {benign_correct}/{len(benign_samples)} ({benign_correct/len(benign_samples):.1%})")
    print(f"Overall accuracy: {total_correct}/{total_samples} ({accuracy:.1%})")
    
    # Compare with training
    training_f1 = training_results.get('f1_score', 0)
    print(f"\nTraining F1-Score: {training_f1:.3f}")
    print(f"Hardcoded in test: 0.8443")
    print(f"Difference: {abs(training_f1 - 0.8443):.3f}")
    
    if abs(training_f1 - 0.8443) > 0.05:
        print("🔴 WARNING: Test script uses wrong training F1-score!")
    else:
        print("✅ Training F1-score matches test script")

def check_enhanced_availability():
    """Check if enhanced detector is properly available"""
    print(f"\n🔧 ENHANCED DETECTOR CHECK:")
    print("="*40)
    
    try:
        from enhanced_threat_model import EnhancedThreatDetector
        print("✅ Enhanced detector import successful")
        
        try:
            detector = EnhancedThreatDetector()
            print("✅ Enhanced detector initialization successful")
            
            # Quick test
            test_log = "Failed password for root from 192.168.1.100 port 22 ssh2"
            result = detector.predict_log(test_log)
            
            print(f"✅ Enhanced detector test successful:")
            print(f"   ML Probability: {result['ml_threat_probability']:.3f}")
            print(f"   Enhanced Prob:  {result['threat_probability']:.3f}")
            print(f"   Enhancement:    {'Yes' if result['enhancement_applied'] else 'No'}")
            
        except Exception as e:
            print(f"❌ Enhanced detector initialization failed: {e}")
            
    except ImportError as e:
        print(f"❌ Enhanced detector import failed: {e}")

if __name__ == "__main__":
    print("🔍 MODEL VERIFICATION TEST")
    print("="*50)
    print("Checking if the current test script is accurate...")
    
    quick_test_samples()
    check_enhanced_availability()
    
    print(f"\n🎯 CONCLUSION:")
    print("="*40)
    print("If the training F1-score doesn't match 0.8443,")
    print("then the test script's overfitting analysis is WRONG!")