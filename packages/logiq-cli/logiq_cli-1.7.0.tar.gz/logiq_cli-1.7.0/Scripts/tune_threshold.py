"""
Threshold Tuning Experiment
Test different thresholds to improve precision while maintaining recall
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

def test_thresholds():
    """Test different threshold values"""
    print("🎯 Threshold Tuning Experiment")
    print("="*40)
    
    # Load model
    models_dir = Path("models")
    model_files = list(models_dir.glob("quick_threat_model_*.joblib"))
    latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
    
    model_data = joblib.load(latest_model)
    model = model_data['model']
    vectorizer = model_data['vectorizer']
    
    print(f"📥 Using model: {latest_model.name}")
    print(f"🔄 Current optimal threshold: {model_data['optimal_threshold']:.3f}")
    
    # Load fresh test data
    print("\n📊 Loading fresh test data...")
    csv_path = "../data/cybersecurity_threat_detection_logs.csv"
    df_test = pd.read_csv(csv_path, skiprows=range(1, 50001), nrows=5000)
    
    # Prepare features
    text_columns = ['timestamp', 'user_agent']
    available_text_cols = [col for col in text_columns if col in df_test.columns]
    
    if len(available_text_cols) > 1:
        df_test['combined_text'] = df_test[available_text_cols].fillna('').astype(str).agg(' '.join, axis=1)
        text_feature = 'combined_text'
    else:
        text_feature = available_text_cols[0]
        df_test[text_feature] = df_test[text_feature].fillna('')
    
    X_test = vectorizer.transform(df_test[text_feature]).toarray()
    
    # Prepare labels
    benign_indicators = ['benign', 'normal', 'legitimate', 'clean', 'Normal']
    is_benign = df_test['threat_label'].str.lower().isin([x.lower() for x in benign_indicators])
    y_true = (~is_benign).astype(int)
    
    # Get probabilities
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print(f"✅ Test data: {len(X_test):,} samples")
    print(f"✅ Threat distribution: {np.sum(y_true):,} threats, {np.sum(y_true==0):,} benign")
    
    # Test different thresholds
    print(f"\n🧪 Testing Thresholds (Range: 0.50 - 0.65):")
    print("-" * 80)
    print(f"{'Threshold':<10} {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'FP Rate':<10} {'Threats Caught':<15}")
    print("-" * 80)
    
    best_threshold = 0.460
    best_score = 0
    
    # Test thresholds from 0.50 to 0.65
    for threshold in np.arange(0.50, 0.66, 0.01):
        y_pred = (y_prob >= threshold).astype(int)
        
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        
        # Calculate false positive rate
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        fp_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        threats_caught = f"{tp}/{tp+fn}"
        
        # Balanced score: prioritize recall but reward precision improvement
        balanced_score = recall * 0.7 + precision * 0.3
        
        if balanced_score > best_score and recall >= 0.85:  # Maintain at least 85% recall
            best_score = balanced_score
            best_threshold = threshold
        
        print(f"{threshold:<10.3f} {precision:<10.3f} {recall:<10.3f} {f1:<10.3f} {fp_rate:<10.3f} {threats_caught:<15}")
    
    print("-" * 80)
    print(f"🎯 RECOMMENDED THRESHOLD: {best_threshold:.3f}")
    
    # Test recommended threshold
    y_pred_best = (y_prob >= best_threshold).astype(int)
    cm_best = confusion_matrix(y_true, y_pred_best)
    tn_best, fp_best, fn_best, tp_best = cm_best.ravel()
    
    precision_best = precision_score(y_true, y_pred_best)
    recall_best = recall_score(y_true, y_pred_best)
    f1_best = f1_score(y_true, y_pred_best)
    fp_rate_best = fp_best / (fp_best + tn_best)
    
    print(f"\n📊 RECOMMENDED THRESHOLD PERFORMANCE:")
    print(f"Threshold: {best_threshold:.3f}")
    print(f"Precision: {precision_best:.3f} (↑ Better than {model_data['optimal_threshold']:.3f})")
    print(f"Recall:    {recall_best:.3f}")
    print(f"F1-Score:  {f1_best:.3f}")
    print(f"False Positive Rate: {fp_rate_best:.3f}")
    print(f"Threats Caught: {tp_best:,}/{tp_best + fn_best:,} ({recall_best:.1%})")
    print(f"Threats Missed: {fn_best:,}")
    
    # Compare with current threshold
    y_pred_current = (y_prob >= model_data['optimal_threshold']).astype(int)
    cm_current = confusion_matrix(y_true, y_pred_current)
    tn_curr, fp_curr, fn_curr, tp_curr = cm_current.ravel()
    precision_curr = precision_score(y_true, y_pred_current)
    fp_rate_curr = fp_curr / (fp_curr + tn_curr)
    
    print(f"\n📈 IMPROVEMENT SUMMARY:")
    print(f"Precision improvement: {precision_best - precision_curr:+.3f}")
    print(f"False Positive reduction: {fp_rate_curr - fp_rate_best:+.3f}")
    print(f"Fewer false positives: {fp_curr - fp_best:,} logs")
    
    if recall_best >= 0.85:
        print(f"✅ EXCELLENT: Maintains high recall ({recall_best:.1%})")
    else:
        print(f"⚠️  WARNING: Recall dropped to {recall_best:.1%}")
    
    # RAG Pipeline Impact
    print(f"\n🔄 RAG PIPELINE IMPACT:")
    print(f"Current ({model_data['optimal_threshold']:.3f}): {fp_curr + tp_curr:,} logs sent to RAG")
    print(f"Recommended ({best_threshold:.3f}): {fp_best + tp_best:,} logs sent to RAG")
    print(f"RAG workload reduction: {(fp_curr + tp_curr) - (fp_best + tp_best):,} logs ({((fp_curr + tp_curr) - (fp_best + tp_best))/(fp_curr + tp_curr)*100:.1f}%)")
    
    print(f"\n💡 RECOMMENDATION:")
    if best_threshold > model_data['optimal_threshold']:
        print(f"✅ UPGRADE threshold from {model_data['optimal_threshold']:.3f} to {best_threshold:.3f}")
        print(f"   - Better precision: {precision_best:.3f} vs {precision_curr:.3f}")
        print(f"   - Reduced RAG load: {(fp_curr + tp_curr) - (fp_best + tp_best):,} fewer logs")
        print(f"   - Still catches {recall_best:.1%} of threats")
    else:
        print(f"⚠️  Current threshold {model_data['optimal_threshold']:.3f} is already optimal")

if __name__ == "__main__":
    test_thresholds()