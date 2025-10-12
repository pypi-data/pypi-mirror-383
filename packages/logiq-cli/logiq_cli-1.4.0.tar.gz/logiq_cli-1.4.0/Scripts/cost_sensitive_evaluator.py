"""
Cost-Sensitive Model Evaluation Script
Comprehensive evaluation of trained cost-sensitive threat detection model
"""

import pandas as pd
import numpy as np
from sklearn.metrics import (
    classification_report, confusion_matrix, precision_recall_curve,
    roc_curve, auc, average_precision_score, roc_auc_score,
    precision_score, recall_score, f1_score, accuracy_score
)
import joblib
from pathlib import Path
from typing import Dict, Any, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Optional visualization imports
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("⚠️  Visualization packages not available - continuing without plots")

class CostSensitiveModelEvaluator:
    def __init__(self, model_path: str):
        """
        Initialize evaluator with trained model
        
        Args:
            model_path: Path to the saved model file
        """
        self.model_path = model_path
        self.model_data = None
        self.model = None
        self.vectorizer = None
        self.optimal_threshold = 0.5
        self.load_model()
        
    def load_model(self):
        """Load the trained model and components"""
        print(f"📥 Loading model from: {self.model_path}")
        
        try:
            self.model_data = joblib.load(self.model_path)
            self.model = self.model_data['model']
            self.vectorizer = self.model_data['vectorizer']
            self.optimal_threshold = self.model_data.get('optimal_threshold', 0.5)
            
            print("✅ Model loaded successfully!")
            print(f"📊 Model type: {self.model_data.get('model_type', 'Unknown')}")
            print(f"🎯 Optimal threshold: {self.optimal_threshold:.3f}")
            print(f"📅 Trained: {self.model_data.get('trained_date', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def load_test_data(self, csv_path: str, sample_size: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """Load and prepare test data"""
        print(f"\n📥 Loading test data from: {csv_path}")
        
        try:
            # Load data
            if sample_size:
                df = pd.read_csv(csv_path, nrows=sample_size)
                print(f"📊 Using sample of {sample_size:,} rows")
            else:
                df = pd.read_csv(csv_path)
            
            print(f"✅ Loaded {len(df):,} test samples")
            
            # Find label and text columns (same logic as trainer)
            label_candidates = ['threat_label', 'label', 'attack_cat', 'class']
            label_col = None
            
            for col in label_candidates:
                if col in df.columns:
                    label_col = col
                    break
            
            if not label_col:
                raise ValueError("No suitable label column found!")
            
            # Find text columns
            text_columns = []
            for col in df.columns:
                if col != label_col and df[col].dtype == 'object':
                    avg_length = df[col].astype(str).str.len().mean()
                    if avg_length > 15:
                        text_columns.append(col)
            
            # Prepare text features
            if len(text_columns) > 1:
                df['combined_text'] = df[text_columns].fillna('').astype(str).agg(' '.join, axis=1)
                text_feature = 'combined_text'
            elif len(text_columns) == 1:
                text_feature = text_columns[0]
                df[text_feature] = df[text_feature].fillna('')
            else:
                raise ValueError("No suitable text columns found!")
            
            # Vectorize text using trained vectorizer
            X = self.vectorizer.transform(df[text_feature]).toarray()
            
            # Prepare binary labels
            unique_labels = df[label_col].unique()
            benign_indicators = ['benign', 'normal', 'legitimate', 'clean']
            is_benign = df[label_col].str.lower().isin(benign_indicators)
            
            if is_benign.any():
                y = (~is_benign).astype(int)
            else:
                benign_label = unique_labels[0]
                y = (df[label_col] != benign_label).astype(int)
            
            print(f"✅ Prepared features: {X.shape}")
            print(f"✅ Label distribution: Benign={np.sum(y==0):,}, Threat={np.sum(y==1):,}")
            print(f"✅ Threat percentage: {np.mean(y)*100:.1f}%")
            
            return X, y
            
        except Exception as e:
            print(f"❌ Error loading test data: {e}")
            raise
    
    def predict_with_probabilities(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Make predictions with probabilities"""
        print("\n🔮 Making predictions...")
        
        # Get probabilities
        y_prob = self.model.predict_proba(X)[:, 1]
        
        # Default threshold predictions
        y_pred_default = self.model.predict(X)
        
        # Optimal threshold predictions
        y_pred_optimal = (y_prob >= self.optimal_threshold).astype(int)
        
        print(f"✅ Generated predictions for {len(X):,} samples")
        
        return y_prob, y_pred_default, y_pred_optimal
    
    def evaluate_performance(self, y_true: np.ndarray, y_prob: np.ndarray, 
                           y_pred_default: np.ndarray, y_pred_optimal: np.ndarray) -> Dict[str, Any]:
        """Comprehensive performance evaluation"""
        print("\n📊 Performance Evaluation:")
        print("="*50)
        
        # Calculate metrics for both thresholds
        results = {
            'default_threshold': {
                'threshold': 0.5,
                'accuracy': accuracy_score(y_true, y_pred_default),
                'precision': precision_score(y_true, y_pred_default),
                'recall': recall_score(y_true, y_pred_default),
                'f1_score': f1_score(y_true, y_pred_default),
                'predictions': y_pred_default
            },
            'optimal_threshold': {
                'threshold': self.optimal_threshold,
                'accuracy': accuracy_score(y_true, y_pred_optimal),
                'precision': precision_score(y_true, y_pred_optimal),
                'recall': recall_score(y_true, y_pred_optimal),
                'f1_score': f1_score(y_true, y_pred_optimal),
                'predictions': y_pred_optimal
            },
            'probability_metrics': {
                'roc_auc': roc_auc_score(y_true, y_prob),
                'avg_precision': average_precision_score(y_true, y_prob),
                'probabilities': y_prob
            }
        }
        
        # Display results
        print("📈 Default Threshold (0.5) Results:")
        for metric, value in results['default_threshold'].items():
            if metric not in ['predictions']:
                print(f"  {metric:10}: {value:.3f}")
        
        print(f"\n🎯 Optimal Threshold ({self.optimal_threshold:.3f}) Results:")
        for metric, value in results['optimal_threshold'].items():
            if metric not in ['predictions']:
                print(f"  {metric:10}: {value:.3f}")
        
        print(f"\n📊 Probability-based Metrics:")
        for metric, value in results['probability_metrics'].items():
            if metric not in ['probabilities']:
                print(f"  {metric:15}: {value:.3f}")
        
        return results
    
    def analyze_confusion_matrices(self, y_true: np.ndarray, y_pred_default: np.ndarray, 
                                 y_pred_optimal: np.ndarray) -> Dict[str, np.ndarray]:
        """Analyze confusion matrices for both thresholds"""
        print("\n🔍 Confusion Matrix Analysis:")
        print("="*50)
        
        # Calculate confusion matrices
        cm_default = confusion_matrix(y_true, y_pred_default)
        cm_optimal = confusion_matrix(y_true, y_pred_optimal)
        
        print("📊 Default Threshold Confusion Matrix:")
        print("     Predicted")
        print("       B    T")
        print(f"B  [{cm_default[0,0]:4d} {cm_default[0,1]:4d}]  Actual")
        print(f"T  [{cm_default[1,0]:4d} {cm_default[1,1]:4d}]")
        
        print(f"\n🎯 Optimal Threshold Confusion Matrix:")
        print("     Predicted")
        print("       B    T")
        print(f"B  [{cm_optimal[0,0]:4d} {cm_optimal[0,1]:4d}]  Actual")
        print(f"T  [{cm_optimal[1,0]:4d} {cm_optimal[1,1]:4d}]")
        
        # Calculate rates
        tn_opt, fp_opt, fn_opt, tp_opt = cm_optimal.ravel()
        
        print(f"\n📈 Optimal Threshold Analysis:")
        print(f"True Positives (Threats caught):     {tp_opt:,}")
        print(f"False Negatives (Threats missed):    {fn_opt:,}")
        print(f"False Positives (Benign flagged):    {fp_opt:,}")
        print(f"True Negatives (Benign correct):     {tn_opt:,}")
        
        threat_detection_rate = tp_opt / (tp_opt + fn_opt) if (tp_opt + fn_opt) > 0 else 0
        false_positive_rate = fp_opt / (fp_opt + tn_opt) if (fp_opt + tn_opt) > 0 else 0
        
        print(f"\n🎯 RAG Pre-filtering Metrics:")
        print(f"Threat Detection Rate: {threat_detection_rate:.1%}")
        print(f"False Positive Rate:   {false_positive_rate:.1%}")
        print(f"Threats Missed:        {fn_opt:,} ({fn_opt/(tp_opt + fn_opt)*100:.1f}%)")
        
        if threat_detection_rate >= 0.95:
            print("✅ EXCELLENT: Very high threat detection rate")
        elif threat_detection_rate >= 0.90:
            print("✅ GOOD: High threat detection rate")
        elif threat_detection_rate >= 0.80:
            print("⚠️  MODERATE: Acceptable but could be improved")
        else:
            print("🔴 POOR: Low threat detection rate - many threats missed")
        
        return {
            'default': cm_default,
            'optimal': cm_optimal
        }
    
    def analyze_feature_importance(self, top_n: int = 20) -> List[Tuple[str, float]]:
        """Analyze feature importance from the trained model"""
        print(f"\n🔍 Top {top_n} Threat Indicators:")
        print("="*50)
        
        if hasattr(self.model, 'feature_importances_'):
            feature_names = self.vectorizer.get_feature_names_out()
            importances = self.model.feature_importances_
            
            # Get top features
            top_indices = np.argsort(importances)[-top_n:][::-1]
            top_features = [(feature_names[i], importances[i]) for i in top_indices]
            
            for i, (feature, importance) in enumerate(top_features, 1):
                print(f"{i:2d}. {feature:20} : {importance:.4f}")
            
            return top_features
        else:
            print("❌ Model doesn't support feature importance analysis")
            return []
    
    def test_sample_predictions(self, X: np.ndarray, y_true: np.ndarray, 
                              y_prob: np.ndarray, y_pred_optimal: np.ndarray,
                              sample_logs: List[str] = None) -> None:
        """Test predictions on sample log entries"""
        print("\n🧪 Sample Prediction Analysis:")
        print("="*60)
        
        if sample_logs is None:
            # Use some indices for sample analysis
            sample_indices = np.random.choice(len(X), min(10, len(X)), replace=False)
        else:
            # If sample logs provided, transform them
            if len(sample_logs) > 0:
                sample_X = self.vectorizer.transform(sample_logs).toarray()
                sample_prob = self.model.predict_proba(sample_X)[:, 1]
                sample_pred = (sample_prob >= self.optimal_threshold).astype(int)
                
                print("Sample Log Predictions:")
                for i, log in enumerate(sample_logs[:10]):  # Show first 10
                    status = "🚨 THREAT" if sample_pred[i] == 1 else "✅ BENIGN"
                    print(f"{i+1:2d}. {status} | Prob: {sample_prob[i]:.3f} | {log[:60]}...")
                return
        
        # Use random samples from test set
        print("Random Test Set Samples:")
        for i, idx in enumerate(sample_indices):
            actual = "THREAT" if y_true[idx] == 1 else "BENIGN"
            predicted = "THREAT" if y_pred_optimal[idx] == 1 else "BENIGN"
            prob = y_prob[idx]
            
            if actual == predicted:
                status = "✅ CORRECT"
            else:
                status = "❌ WRONG"
            
            print(f"{i+1:2d}. {status} | Actual: {actual} | Pred: {predicted} | Prob: {prob:.3f}")
    
    def generate_evaluation_report(self, results: Dict[str, Any], 
                                 confusion_matrices: Dict[str, np.ndarray],
                                 top_features: List[Tuple[str, float]]) -> str:
        """Generate comprehensive evaluation report"""
        report_path = Path(self.model_path).with_suffix('.evaluation_report.txt')
        
        with open(report_path, 'w') as f:
            f.write("Cost-Sensitive Threat Detection Model - Evaluation Report\n")
            f.write("="*70 + "\n\n")
            
            # Model info
            f.write("Model Information:\n")
            f.write(f"Model Path: {self.model_path}\n")
            f.write(f"Model Type: {self.model_data.get('model_type', 'Unknown')}\n")
            f.write(f"Trained Date: {self.model_data.get('trained_date', 'Unknown')}\n")
            f.write(f"Optimization Goal: {self.model_data.get('optimization_goal', 'Unknown')}\n")
            f.write(f"Optimal Threshold: {self.optimal_threshold:.3f}\n\n")
            
            # Performance metrics
            f.write("Performance Metrics:\n")
            f.write("-" * 30 + "\n")
            f.write("Default Threshold (0.5):\n")
            for metric, value in results['default_threshold'].items():
                if metric not in ['predictions']:
                    f.write(f"  {metric}: {value:.4f}\n")
            
            f.write(f"\nOptimal Threshold ({self.optimal_threshold:.3f}):\n")
            for metric, value in results['optimal_threshold'].items():
                if metric not in ['predictions']:
                    f.write(f"  {metric}: {value:.4f}\n")
            
            f.write(f"\nProbability-based Metrics:\n")
            for metric, value in results['probability_metrics'].items():
                if metric not in ['probabilities']:
                    f.write(f"  {metric}: {value:.4f}\n")
            
            # Confusion matrix analysis
            cm_opt = confusion_matrices['optimal']
            tn, fp, fn, tp = cm_opt.ravel()
            
            f.write(f"\nConfusion Matrix Analysis (Optimal Threshold):\n")
            f.write("-" * 45 + "\n")
            f.write(f"True Positives (Threats caught):   {tp:,}\n")
            f.write(f"False Negatives (Threats missed):  {fn:,}\n")
            f.write(f"False Positives (Benign flagged):  {fp:,}\n")
            f.write(f"True Negatives (Benign correct):   {tn:,}\n")
            
            threat_detection_rate = tp / (tp + fn) if (tp + fn) > 0 else 0
            false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
            
            f.write(f"\nRAG Pre-filtering Analysis:\n")
            f.write(f"Threat Detection Rate: {threat_detection_rate:.1%}\n")
            f.write(f"False Positive Rate:   {false_positive_rate:.1%}\n")
            f.write(f"Threats Missed:        {fn:,} ({fn/(tp + fn)*100:.1f}%)\n")
            
            # Feature importance
            if top_features:
                f.write(f"\nTop Threat Indicators:\n")
                f.write("-" * 25 + "\n")
                for i, (feature, importance) in enumerate(top_features[:15], 1):
                    f.write(f"{i:2d}. {feature:25} : {importance:.4f}\n")
            
            # Recommendations
            f.write(f"\nRecommendations:\n")
            f.write("-" * 15 + "\n")
            
            if threat_detection_rate >= 0.95:
                f.write("✅ Model ready for RAG pre-filtering deployment\n")
            elif threat_detection_rate >= 0.90:
                f.write("✅ Model acceptable for RAG pre-filtering\n")
            else:
                f.write("⚠️  Consider retraining with higher recall target\n")
            
            if false_positive_rate > 0.20:
                f.write("⚠️  High false positive rate - may overwhelm RAG pipeline\n")
            
            f.write(f"\nUse optimal threshold {self.optimal_threshold:.3f} for predictions\n")
        
        print(f"\n📄 Evaluation report saved to: {report_path}")
        return str(report_path)
    
    def run_comprehensive_evaluation(self, test_csv_path: str, 
                                   sample_size: int = None,
                                   sample_logs: List[str] = None) -> str:
        """Run complete evaluation pipeline"""
        print("🔍 Comprehensive Model Evaluation")
        print("="*50)
        
        # Load test data
        X_test, y_test = self.load_test_data(test_csv_path, sample_size)
        
        # Make predictions
        y_prob, y_pred_default, y_pred_optimal = self.predict_with_probabilities(X_test)
        
        # Evaluate performance
        results = self.evaluate_performance(y_test, y_prob, y_pred_default, y_pred_optimal)
        
        # Analyze confusion matrices
        confusion_matrices = self.analyze_confusion_matrices(y_test, y_pred_default, y_pred_optimal)
        
        # Feature importance analysis
        top_features = self.analyze_feature_importance()
        
        # Sample predictions
        self.test_sample_predictions(X_test, y_test, y_prob, y_pred_optimal, sample_logs)
        
        # Generate report
        report_path = self.generate_evaluation_report(results, confusion_matrices, top_features)
        
        print(f"\n🎉 Evaluation completed!")
        return report_path

def main():
    """Main evaluation function"""
    # Configuration
    model_path = "models/cost_sensitive_threat_model_20241011_143000.joblib"  # Update this path
    test_csv_path = "../data/cybersecurity_logs.csv"  # Update this path
    sample_size = 10000  # Use None for full dataset
    
    # Sample logs for testing (optional)
    sample_logs = [
        "Oct 11 13:45:01 sshd[2541]: Failed password for invalid user admin from 103.20.10.5 port 51234 ssh2",
        "Oct 12 10:30:45 sudo: hacker : TTY=pts/2 ; PWD=/tmp ; USER=root ; COMMAND=/bin/bash /tmp/exploit.sh",
        "CVE-2021-44228 Log4j exploitation detected",
        "SQL injection attempt blocked - UNION SELECT detected",
        "Oct 11 08:00:05 kernel: Initializing cgroup subsys cpuset",
        "User john.doe logged in successfully",
        "CRON: Daily backup job completed - 15.2GB archived",
        "WEB: HTTP 200 GET /api/users/profile - response time 125ms"
    ]
    
    try:
        # Initialize evaluator
        evaluator = CostSensitiveModelEvaluator(model_path)
        
        # Run evaluation
        report_path = evaluator.run_comprehensive_evaluation(
            test_csv_path=test_csv_path,
            sample_size=sample_size,
            sample_logs=sample_logs
        )
        
        print(f"\n✅ Evaluation completed successfully!")
        print(f"📄 Report saved to: {report_path}")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")

if __name__ == "__main__":
    main()