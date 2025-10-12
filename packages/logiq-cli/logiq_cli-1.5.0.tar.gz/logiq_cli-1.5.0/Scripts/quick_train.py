"""
Quick Training Script - Train Cost-Sensitive Model
Simple training without complex setup checks
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_curve
from sklearn.utils.class_weight import compute_class_weight
import joblib
from datetime import datetime
from pathlib import Path

def quick_train():
    """Quick training function"""
    print("🚀 Quick Cost-Sensitive Training")
    print("="*40)
    
    # Configuration
    csv_path = "../data/cybersecurity_threat_detection_logs.csv"
    sample_size = 50000  # Use subset for quick training
    
    print(f"📥 Loading data from: {csv_path}")
    print(f"📊 Using sample size: {sample_size:,}")
    
    try:
        # Load data
        df = pd.read_csv(csv_path, nrows=sample_size)
        print(f"✅ Loaded {len(df):,} samples")
        print(f"📝 Columns: {list(df.columns)}")
        
        # Find label column
        label_candidates = ['threat_label', 'label', 'attack_cat', 'class', 'Label']
        label_col = None
        
        for col in label_candidates:
            if col in df.columns:
                label_col = col
                break
        
        if not label_col:
            print(f"❌ No label column found in: {list(df.columns)}")
            return
        
        # Find text columns
        text_columns = []
        for col in df.columns:
            if col != label_col and df[col].dtype == 'object':
                avg_length = df[col].astype(str).str.len().mean()
                if avg_length > 15:
                    text_columns.append(col)
        
        print(f"📝 Text columns: {text_columns}")
        print(f"🎯 Label column: {label_col}")
        
        # Prepare text features
        if len(text_columns) > 1:
            df['combined_text'] = df[text_columns].fillna('').astype(str).agg(' '.join, axis=1)
            text_feature = 'combined_text'
        elif len(text_columns) == 1:
            text_feature = text_columns[0]
            df[text_feature] = df[text_feature].fillna('')
        else:
            print("❌ No suitable text columns found!")
            return
        
        # Check unique labels
        unique_labels = df[label_col].unique()
        print(f"📊 Unique labels: {unique_labels}")
        
        # Prepare binary labels
        benign_indicators = ['benign', 'normal', 'legitimate', 'clean', 'Normal']
        is_benign = df[label_col].str.lower().isin([x.lower() for x in benign_indicators])
        
        if is_benign.any():
            y = (~is_benign).astype(int)
        else:
            # Assume first unique label is benign
            benign_label = unique_labels[0]
            y = (df[label_col] != benign_label).astype(int)
        
        print(f"✅ Label distribution: Benign={np.sum(y==0):,}, Threat={np.sum(y==1):,}")
        print(f"✅ Threat percentage: {np.mean(y)*100:.1f}%")
        
        # Vectorize text
        print("\n🔤 Vectorizing text features...")
        vectorizer = TfidfVectorizer(
            max_features=3000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        
        X = vectorizer.fit_transform(df[text_feature]).toarray()
        print(f"✅ Feature matrix shape: {X.shape}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"📊 Training set: {X_train.shape[0]:,} samples")
        print(f"📊 Test set: {X_test.shape[0]:,} samples")
        
        # Calculate class weights for cost-sensitive learning
        print("\n⚖️  Calculating class weights...")
        classes = np.unique(y_train)
        class_weights = compute_class_weight('balanced', classes=classes, y=y_train)
        class_weight_dict = dict(zip(classes, class_weights))
        
        print(f"📊 Class weights: {class_weight_dict}")
        
        # Train model
        print("\n🤖 Training Random Forest model...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight=class_weight_dict,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        print("✅ Model training completed!")
        
        # Quick evaluation
        print("\n📊 Quick Evaluation:")
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        print(f"Training accuracy: {train_score:.3f}")
        print(f"Test accuracy: {test_score:.3f}")
        
        # Predictions
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        print(f"\nConfusion Matrix:")
        print(f"True Positives:  {tp:,}")
        print(f"False Negatives: {fn:,}")
        print(f"False Positives: {fp:,}")
        print(f"True Negatives:  {tn:,}")
        
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\nMetrics:")
        print(f"Precision: {precision:.3f}")
        print(f"Recall:    {recall:.3f}")
        print(f"F1-Score:  {f1:.3f}")
        
        # Find optimal threshold for high recall
        print("\n🎯 Finding optimal threshold for high recall...")
        precisions, recalls, thresholds = precision_recall_curve(y_test, y_prob)
        
        # Note: precision_recall_curve returns n_thresholds = n_samples + 1
        # So we need to align the arrays properly
        if len(thresholds) == len(recalls) - 1:
            # Remove last element from recalls and precisions
            recalls = recalls[:-1]
            precisions = precisions[:-1]
        
        # Find threshold that gives at least 90% recall
        target_recall = 0.90
        valid_indices = recalls >= target_recall
        
        if np.any(valid_indices):
            # Get the index in the valid set, then map back to original
            valid_precisions = precisions[valid_indices]
            best_relative_idx = np.argmax(valid_precisions)
            # Find the actual index in the original arrays
            valid_actual_indices = np.where(valid_indices)[0]
            best_idx = valid_actual_indices[best_relative_idx]
            optimal_threshold = thresholds[best_idx]
        else:
            # Fallback to best F1
            f1_scores = 2 * (precisions * recalls) / (precisions + recalls)
            f1_scores = np.nan_to_num(f1_scores)
            best_idx = np.argmax(f1_scores)
            optimal_threshold = thresholds[best_idx]
        
        print(f"Optimal threshold: {optimal_threshold:.3f}")
        
        # Test optimal threshold
        y_pred_optimal = (y_prob >= optimal_threshold).astype(int)
        cm_opt = confusion_matrix(y_test, y_pred_optimal)
        tn_opt, fp_opt, fn_opt, tp_opt = cm_opt.ravel()
        
        recall_opt = tp_opt / (tp_opt + fn_opt) if (tp_opt + fn_opt) > 0 else 0
        precision_opt = tp_opt / (tp_opt + fp_opt) if (tp_opt + fp_opt) > 0 else 0
        
        print(f"\nOptimal Threshold Results:")
        print(f"Recall:    {recall_opt:.3f}")
        print(f"Precision: {precision_opt:.3f}")
        print(f"Threats caught: {tp_opt:,}/{tp_opt + fn_opt:,} ({recall_opt:.1%})")
        
        # Save model
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"quick_threat_model_{timestamp}.joblib"
        model_path = models_dir / model_filename
        
        model_data = {
            'model': model,
            'vectorizer': vectorizer,
            'optimal_threshold': optimal_threshold,
            'model_type': 'RandomForest_CostSensitive',
            'trained_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'training_size': len(X_train),
            'test_metrics': {
                'accuracy': test_score,
                'precision': precision_opt,
                'recall': recall_opt,
                'f1_score': 2 * (precision_opt * recall_opt) / (precision_opt + recall_opt) if (precision_opt + recall_opt) > 0 else 0
            }
        }
        
        joblib.dump(model_data, model_path)
        print(f"\n💾 Model saved to: {model_path}")
        
        print(f"\n🎉 Training completed successfully!")
        print(f"📊 Use threshold {optimal_threshold:.3f} for high recall")
        
        return str(model_path)
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_train()