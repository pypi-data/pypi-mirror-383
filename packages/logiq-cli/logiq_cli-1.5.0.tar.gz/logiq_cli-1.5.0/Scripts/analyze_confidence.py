"""
Model Confidence Analysis
Analyze confidence levels and prediction certainty in binary classification
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import matplotlib.pyplot as plt

def analyze_model_confidence():
    """Analyze confidence levels in model predictions"""
    print("📊 Model Confidence Analysis")
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
    
    # Load test data
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
    
    # Prepare true labels
    benign_indicators = ['benign', 'normal', 'legitimate', 'clean', 'Normal']
    is_benign = df_test['threat_label'].str.lower().isin([x.lower() for x in benign_indicators])
    y_true = (~is_benign).astype(int)
    
    # Get predictions and probabilities
    y_prob = model.predict_proba(X_test)[:, 1]  # Probability of being threat
    y_pred = (y_prob >= threshold).astype(int)
    
    print(f"\n📊 Probability Distribution Analysis:")
    print("-" * 40)
    
    # Analyze probability distribution
    print(f"Probability Statistics:")
    print(f"  Minimum:     {np.min(y_prob):.4f}")
    print(f"  Maximum:     {np.max(y_prob):.4f}")
    print(f"  Mean:        {np.mean(y_prob):.4f}")
    print(f"  Median:      {np.median(y_prob):.4f}")
    print(f"  Std Dev:     {np.std(y_prob):.4f}")
    
    # Confidence level analysis
    print(f"\n🎯 Confidence Level Breakdown:")
    print("-" * 40)
    
    # Define confidence levels based on distance from decision boundary (0.5)
    very_high_conf_threat = np.sum(y_prob >= 0.8)
    high_conf_threat = np.sum((y_prob >= 0.7) & (y_prob < 0.8))
    medium_conf_threat = np.sum((y_prob >= 0.6) & (y_prob < 0.7))
    low_conf_threat = np.sum((y_prob >= threshold) & (y_prob < 0.6))
    
    very_high_conf_benign = np.sum(y_prob <= 0.2)
    high_conf_benign = np.sum((y_prob > 0.2) & (y_prob <= 0.3))
    medium_conf_benign = np.sum((y_prob > 0.3) & (y_prob <= 0.4))
    low_conf_benign = np.sum((y_prob > 0.4) & (y_prob < threshold))
    
    uncertain = np.sum((y_prob >= 0.4) & (y_prob <= 0.6))
    
    total_samples = len(y_prob)
    
    print(f"THREAT Predictions:")
    print(f"  Very High Confidence (≥0.8): {very_high_conf_threat:,} ({very_high_conf_threat/total_samples*100:.1f}%)")
    print(f"  High Confidence (0.7-0.8):   {high_conf_threat:,} ({high_conf_threat/total_samples*100:.1f}%)")
    print(f"  Medium Confidence (0.6-0.7):  {medium_conf_threat:,} ({medium_conf_threat/total_samples*100:.1f}%)")
    print(f"  Low Confidence ({threshold:.1f}-0.6):   {low_conf_threat:,} ({low_conf_threat/total_samples*100:.1f}%)")
    
    print(f"\nBENIGN Predictions:")
    print(f"  Very High Confidence (≤0.2): {very_high_conf_benign:,} ({very_high_conf_benign/total_samples*100:.1f}%)")
    print(f"  High Confidence (0.2-0.3):   {high_conf_benign:,} ({high_conf_benign/total_samples*100:.1f}%)")
    print(f"  Medium Confidence (0.3-0.4):  {medium_conf_benign:,} ({medium_conf_benign/total_samples*100:.1f}%)")
    print(f"  Low Confidence (0.4-{threshold:.1f}):   {low_conf_benign:,} ({low_conf_benign/total_samples*100:.1f}%)")
    
    print(f"\nUNCERTAIN Region (0.4-0.6):    {uncertain:,} ({uncertain/total_samples*100:.1f}%)")
    
    # Analyze prediction confidence by correctness
    print(f"\n🎯 Confidence vs Accuracy Analysis:")
    print("-" * 40)
    
    correct_predictions = (y_pred == y_true)
    
    # For correct predictions
    correct_probs = y_prob[correct_predictions]
    incorrect_probs = y_prob[~correct_predictions]
    
    print(f"CORRECT Predictions ({np.sum(correct_predictions):,} samples):")
    print(f"  Mean probability:    {np.mean(correct_probs):.4f}")
    print(f"  Std deviation:       {np.std(correct_probs):.4f}")
    print(f"  High confidence (>0.7 or <0.3): {np.sum((correct_probs > 0.7) | (correct_probs < 0.3)):,} ({np.sum((correct_probs > 0.7) | (correct_probs < 0.3))/len(correct_probs)*100:.1f}%)")
    
    print(f"\nINCORRECT Predictions ({np.sum(~correct_predictions):,} samples):")
    print(f"  Mean probability:    {np.mean(incorrect_probs):.4f}")
    print(f"  Std deviation:       {np.std(incorrect_probs):.4f}")
    print(f"  High confidence (>0.7 or <0.3): {np.sum((incorrect_probs > 0.7) | (incorrect_probs < 0.3)):,} ({np.sum((incorrect_probs > 0.7) | (incorrect_probs < 0.3))/len(incorrect_probs)*100:.1f}%)")
    
    # Calibration analysis
    print(f"\n📊 Model Calibration Analysis:")
    print("-" * 40)
    
    # Bin predictions by probability ranges
    prob_bins = np.arange(0, 1.1, 0.1)
    bin_accuracies = []
    bin_confidences = []
    bin_counts = []
    
    for i in range(len(prob_bins)-1):
        bin_mask = (y_prob >= prob_bins[i]) & (y_prob < prob_bins[i+1])
        if np.sum(bin_mask) > 0:
            bin_accuracy = np.mean(y_true[bin_mask])
            bin_confidence = np.mean(y_prob[bin_mask])
            bin_count = np.sum(bin_mask)
            
            bin_accuracies.append(bin_accuracy)
            bin_confidences.append(bin_confidence)
            bin_counts.append(bin_count)
            
            print(f"  Prob {prob_bins[i]:.1f}-{prob_bins[i+1]:.1f}: {bin_count:4d} samples, Avg prob: {bin_confidence:.3f}, True threat rate: {bin_accuracy:.3f}")
    
    # Overall confidence assessment
    print(f"\n🎯 Overall Confidence Assessment:")
    print("="*40)
    
    # Calculate entropy-based confidence
    prob_entropy = -y_prob * np.log2(y_prob + 1e-10) - (1-y_prob) * np.log2(1-y_prob + 1e-10)
    avg_entropy = np.mean(prob_entropy)
    high_certainty_samples = np.sum((y_prob <= 0.2) | (y_prob >= 0.8))
    
    print(f"Average Prediction Entropy: {avg_entropy:.4f} (lower = more confident)")
    print(f"High Certainty Predictions: {high_certainty_samples:,}/{total_samples:,} ({high_certainty_samples/total_samples*100:.1f}%)")
    print(f"Uncertain Predictions (0.4-0.6): {uncertain:,}/{total_samples:,} ({uncertain/total_samples*100:.1f}%)")
    
    # Final confidence rating
    if high_certainty_samples/total_samples > 0.5:
        confidence_rating = "HIGH"
    elif high_certainty_samples/total_samples > 0.3:
        confidence_rating = "MEDIUM"
    else:
        confidence_rating = "LOW"
    
    print(f"\n🏆 OVERALL MODEL CONFIDENCE: {confidence_rating}")
    
    if confidence_rating == "LOW":
        print("⚠️  Model shows low confidence - many predictions near decision boundary")
        print("💡 Consider: Feature engineering, more training data, or different algorithms")
    elif confidence_rating == "MEDIUM":
        print("✅ Model shows reasonable confidence - acceptable for pre-filtering")
        print("💡 Consider: Threshold tuning or ensemble methods for improvement")
    else:
        print("🎉 Model shows high confidence - good separation between classes")
    
    # Return summary statistics
    return {
        'avg_entropy': avg_entropy,
        'high_certainty_rate': high_certainty_samples/total_samples,
        'uncertain_rate': uncertain/total_samples,
        'confidence_rating': confidence_rating,
        'prob_mean': np.mean(y_prob),
        'prob_std': np.std(y_prob)
    }

if __name__ == "__main__":
    stats = analyze_model_confidence()