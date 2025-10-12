"""
Cost-Sensitive Threat Detection Trainer for RAG Pre-filtering
Optimized for high recall to ensure minimal threat loss before RAG pipeline
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, precision_recall_curve,
    average_precision_score, roc_auc_score, precision_score, 
    recall_score, f1_score, accuracy_score
)
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class CostSensitiveThreatTrainer:
    def __init__(self, recall_target: float = 0.95):
        """
        Initialize cost-sensitive trainer for RAG pre-filtering
        
        Args:
            recall_target: Target recall rate (default 95% to catch most threats)
        """
        self.recall_target = recall_target
        self.vectorizer = TfidfVectorizer(
            max_features=3000,  # Balanced for performance and accuracy
            stop_words='english',
            ngram_range=(1, 2),  # Include bigrams for context
            min_df=3,           # Remove very rare words
            max_df=0.95,        # Remove very common words
            lowercase=True,
            strip_accents='ascii'
        )
        self.model = None
        self.optimal_threshold = 0.5
        self.class_weights = None
        self.results = {}
        
    def load_dataset(self, csv_path: str, sample_size: int = None) -> pd.DataFrame:
        """Load the cybersecurity dataset"""
        print(f"📥 Loading dataset from: {csv_path}")
        
        try:
            # Load data (sample if dataset is very large)
            if sample_size:
                print(f"📊 Sampling {sample_size:,} rows for faster training...")
                df = pd.read_csv(csv_path, nrows=sample_size)
            else:
                df = pd.read_csv(csv_path)
            
            print(f"✅ Loaded {len(df):,} log entries")
            
            # Display dataset info
            print(f"\n📋 Dataset Information:")
            print(f"Columns: {list(df.columns)}")
            print(f"Shape: {df.shape}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            raise
    
    def analyze_dataset(self, df: pd.DataFrame) -> dict:
        """Analyze dataset distribution and characteristics"""
        print("\n🔍 Dataset Analysis:")
        print("="*50)
        
        # Find label column
        label_candidates = ['threat_label', 'label', 'attack_cat', 'class']
        label_col = None
        
        for col in label_candidates:
            if col in df.columns:
                label_col = col
                break
        
        if not label_col:
            print("❌ No suitable label column found!")
            print(f"Available columns: {list(df.columns)}")
            return None
        
        print(f"📊 Using label column: '{label_col}'")
        
        # Label distribution
        label_counts = df[label_col].value_counts()
        print(f"\n🏷️  Label Distribution:")
        for label, count in label_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {label:15}: {count:,} ({percentage:.1f}%)")
        
        # Identify text columns
        text_columns = []
        for col in df.columns:
            if col != label_col and df[col].dtype == 'object':
                avg_length = df[col].astype(str).str.len().mean()
                if avg_length > 15:  # Likely log messages
                    text_columns.append(col)
        
        print(f"\n📝 Text columns found: {text_columns}")
        
        # Check for missing values
        missing_info = df.isnull().sum()
        if missing_info.sum() > 0:
            print(f"\n⚠️  Missing values found:")
            for col, missing in missing_info.items():
                if missing > 0:
                    print(f"  {col}: {missing:,} ({missing/len(df)*100:.1f}%)")
        
        return {
            'label_column': label_col,
            'text_columns': text_columns,
            'label_distribution': label_counts.to_dict(),
            'total_samples': len(df)
        }
    
    def prepare_features(self, df: pd.DataFrame, analysis_info: dict) -> tuple:
        """Prepare features for training"""
        print("\n🔧 Preparing features...")
        
        label_col = analysis_info['label_column']
        text_columns = analysis_info['text_columns']
        
        # Combine text columns into a single feature
        if len(text_columns) > 1:
            print(f"📝 Combining text columns: {text_columns}")
            df['combined_text'] = df[text_columns].fillna('').astype(str).agg(' '.join, axis=1)
            text_feature = 'combined_text'
        elif len(text_columns) == 1:
            text_feature = text_columns[0]
            df[text_feature] = df[text_feature].fillna('')
        else:
            raise ValueError("No suitable text columns found for feature extraction!")
        
        # Vectorize text
        print(f"🔤 Vectorizing text from column: '{text_feature}'")
        X = self.vectorizer.fit_transform(df[text_feature]).toarray()
        
        # Create binary labels (benign=0, threat=1)
        unique_labels = df[label_col].unique()
        print(f"🏷️  Unique labels: {unique_labels}")
        
        # Convert to binary classification
        benign_indicators = ['benign', 'normal', 'legitimate', 'clean']
        is_benign = df[label_col].str.lower().isin(benign_indicators)
        
        if is_benign.any():
            y = (~is_benign).astype(int)
        else:
            # Assume first label is benign, rest are threats
            benign_label = unique_labels[0]
            y = (df[label_col] != benign_label).astype(int)
        
        print(f"✅ Feature matrix shape: {X.shape}")
        print(f"✅ Label distribution: Benign={np.sum(y==0):,}, Threat={np.sum(y==1):,}")
        print(f"✅ Threat percentage: {np.mean(y)*100:.1f}%")
        
        return X, y
    
    def calculate_optimal_class_weights(self, y: np.ndarray) -> dict:
        """Calculate class weights optimized for high recall"""
        benign_count = np.sum(y == 0)
        threat_count = np.sum(y == 1)
        
        # Calculate base weight ratio
        base_ratio = benign_count / threat_count
        
        # Apply multiplier for high recall (aggressive weighting)
        # Start with 2x the natural ratio, can be tuned
        recall_multiplier = 2.0
        threat_weight = base_ratio * recall_multiplier
        
        class_weights = {
            0: 1.0,           # Benign (normal weight)
            1: threat_weight  # Threats (heavily weighted)
        }
        
        print(f"\n⚖️  Class Weight Calculation:")
        print(f"Benign samples: {benign_count:,}")
        print(f"Threat samples: {threat_count:,}")
        print(f"Natural ratio: {base_ratio:.1f}")
        print(f"Applied multiplier: {recall_multiplier}x")
        print(f"Final weights: Benign=1.0, Threat={threat_weight:.1f}")
        
        self.class_weights = class_weights
        return class_weights
    
    def split_dataset(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> tuple:
        """Split dataset with stratification to preserve class distribution"""
        print(f"\n📊 Splitting dataset (test size: {test_size*100:.0f}%)...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"Training set: {X_train.shape[0]:,} samples")
        print(f"  - Benign: {np.sum(y_train==0):,} ({np.mean(y_train==0)*100:.1f}%)")
        print(f"  - Threat: {np.sum(y_train==1):,} ({np.mean(y_train==1)*100:.1f}%)")
        
        print(f"Test set: {X_test.shape[0]:,} samples")
        print(f"  - Benign: {np.sum(y_test==0):,} ({np.mean(y_test==0)*100:.1f}%)")
        print(f"  - Threat: {np.sum(y_test==1):,} ({np.mean(y_test==1)*100:.1f}%)")
        
        return X_train, X_test, y_train, y_test
    
    def train_cost_sensitive_model(self, X_train: np.ndarray, y_train: np.ndarray) -> dict:
        """Train cost-sensitive Random Forest model"""
        print("\n🚀 Training Cost-Sensitive Model...")
        print("="*50)
        
        # Calculate optimal class weights
        class_weights = self.calculate_optimal_class_weights(y_train)
        
        # Initialize model with cost-sensitive configuration
        self.model = RandomForestClassifier(
            n_estimators=100,        # Good balance of accuracy and speed
            max_depth=15,           # Prevent overfitting
            min_samples_split=10,   # Require minimum samples for splits
            min_samples_leaf=5,     # Prevent overfitting to individual samples
            max_features='sqrt',    # Use subset of features for each tree
            class_weight=class_weights,  # Apply cost-sensitive weights
            random_state=42,
            n_jobs=-1,              # Use all CPU cores
            oob_score=True          # Out-of-bag scoring for validation
        )
        
        print("🔧 Model Configuration:")
        print(f"  - Estimators: {self.model.n_estimators}")
        print(f"  - Max Depth: {self.model.max_depth}")
        print(f"  - Class Weights: {class_weights}")
        
        # Train the model
        print("\n⏳ Training in progress...")
        self.model.fit(X_train, y_train)
        
        print("✅ Training completed!")
        print(f"📊 Out-of-bag score: {self.model.oob_score_:.3f}")
        
        # Cross-validation for robustness check
        print("\n🔄 Performing cross-validation...")
        cv_scores = cross_val_score(
            self.model, X_train, y_train,
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            scoring='recall'  # Focus on recall for RAG pre-filtering
        )
        
        cv_results = {
            'cv_recall_mean': cv_scores.mean(),
            'cv_recall_std': cv_scores.std(),
            'cv_scores': cv_scores
        }
        
        print(f"Cross-validation Recall: {cv_results['cv_recall_mean']:.3f} ± {cv_results['cv_recall_std']:.3f}")
        
        return cv_results
    
    def optimize_threshold_for_recall(self, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """Find optimal threshold to achieve target recall"""
        print(f"\n🎯 Optimizing threshold for {self.recall_target*100:.0f}% recall...")
        
        # Get prediction probabilities
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate precision-recall curve
        precision, recall, thresholds = precision_recall_curve(y_test, y_prob)
        
        # Find threshold that achieves target recall
        valid_indices = recall >= self.recall_target
        if not valid_indices.any():
            print(f"⚠️  Cannot achieve {self.recall_target*100:.0f}% recall. Using lowest threshold.")
            optimal_threshold = thresholds.min()
        else:
            # Among thresholds that meet recall target, choose one with highest precision
            valid_precisions = precision[valid_indices]
            valid_thresholds = thresholds[valid_indices]
            best_idx = np.argmax(valid_precisions)
            optimal_threshold = valid_thresholds[best_idx]
        
        self.optimal_threshold = optimal_threshold
        
        # Evaluate with optimal threshold
        y_pred_optimal = (y_prob >= optimal_threshold).astype(int)
        actual_recall = recall_score(y_test, y_pred_optimal)
        actual_precision = precision_score(y_test, y_pred_optimal)
        
        print(f"🎯 Optimal threshold: {optimal_threshold:.3f}")
        print(f"📊 Achieved recall: {actual_recall:.3f}")
        print(f"📊 Achieved precision: {actual_precision:.3f}")
        
        return optimal_threshold
    
    def evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """Comprehensive model evaluation"""
        print("\n📊 Model Evaluation:")
        print("="*50)
        
        # Predictions with default and optimal thresholds
        y_prob = self.model.predict_proba(X_test)[:, 1]
        y_pred_default = self.model.predict(X_test)
        y_pred_optimal = (y_prob >= self.optimal_threshold).astype(int)
        
        # Calculate comprehensive metrics
        results = {
            'default_threshold': {
                'threshold': 0.5,
                'accuracy': accuracy_score(y_test, y_pred_default),
                'precision': precision_score(y_test, y_pred_default),
                'recall': recall_score(y_test, y_pred_default),
                'f1_score': f1_score(y_test, y_pred_default)
            },
            'optimal_threshold': {
                'threshold': self.optimal_threshold,
                'accuracy': accuracy_score(y_test, y_pred_optimal),
                'precision': precision_score(y_test, y_pred_optimal),
                'recall': recall_score(y_test, y_pred_optimal),
                'f1_score': f1_score(y_test, y_pred_optimal)
            },
            'probability_metrics': {
                'roc_auc': roc_auc_score(y_test, y_prob),
                'avg_precision': average_precision_score(y_test, y_prob)
            }
        }
        
        # Display results
        print("📈 Default Threshold (0.5) Results:")
        for metric, value in results['default_threshold'].items():
            if metric != 'threshold':
                print(f"  {metric:10}: {value:.3f}")
        
        print(f"\n🎯 Optimal Threshold ({self.optimal_threshold:.3f}) Results:")
        for metric, value in results['optimal_threshold'].items():
            if metric != 'threshold':
                print(f"  {metric:10}: {value:.3f}")
        
        print(f"\n📊 Probability-based Metrics:")
        for metric, value in results['probability_metrics'].items():
            print(f"  {metric:15}: {value:.3f}")
        
        # RAG-specific analysis
        optimal_recall = results['optimal_threshold']['recall']
        optimal_precision = results['optimal_threshold']['precision']
        
        print(f"\n🎯 RAG Pre-filtering Analysis:")
        print(f"Threat Detection Rate: {optimal_recall:.1%}")
        print(f"False Positive Rate:   {(1-optimal_precision)*optimal_recall/(1-optimal_recall+optimal_recall*optimal_precision):.1%}")
        
        if optimal_recall >= 0.90:
            print("✅ EXCELLENT: High threat detection rate for RAG pre-filtering")
        elif optimal_recall >= 0.80:
            print("✅ GOOD: Acceptable threat detection rate")
        else:
            print("⚠️  WARNING: Low threat detection rate - may miss important threats")
        
        return results
    
    def save_model(self, model_path: str = None) -> str:
        """Save the trained model and metadata"""
        if model_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_path = f"models/cost_sensitive_threat_model_{timestamp}.joblib"
        
        model_path = Path(model_path)
        model_path.parent.mkdir(exist_ok=True)
        
        # Save complete model data
        model_data = {
            'model': self.model,
            'vectorizer': self.vectorizer,
            'optimal_threshold': self.optimal_threshold,
            'class_weights': self.class_weights,
            'recall_target': self.recall_target,
            'training_results': self.results,
            'trained_date': datetime.now().isoformat(),
            'model_type': 'cost_sensitive_threat_detector',
            'optimization_goal': 'high_recall_rag_prefiltering'
        }
        
        joblib.dump(model_data, model_path)
        print(f"\n💾 Model saved to: {model_path}")
        
        # Save training summary
        summary_path = model_path.with_suffix('.txt')
        with open(summary_path, 'w') as f:
            f.write("Cost-Sensitive Threat Detection Model - Training Summary\n")
            f.write("="*60 + "\n\n")
            f.write(f"Training Date: {datetime.now()}\n")
            f.write(f"Model Type: Cost-Sensitive Random Forest\n")
            f.write(f"Optimization Goal: High Recall for RAG Pre-filtering\n")
            f.write(f"Target Recall: {self.recall_target:.1%}\n")
            f.write(f"Optimal Threshold: {self.optimal_threshold:.3f}\n\n")
            
            if 'optimal_threshold' in self.results:
                f.write("Performance Metrics:\n")
                for metric, value in self.results['optimal_threshold'].items():
                    f.write(f"  {metric}: {value:.4f}\n")
        
        print(f"📄 Training summary saved to: {summary_path}")
        return str(model_path)
    
    def run_training_pipeline(self, csv_path: str, sample_size: int = None, test_size: float = 0.2) -> str:
        """Complete training pipeline"""
        print("🚀 Cost-Sensitive Threat Detection Training Pipeline")
        print("="*60)
        print(f"Goal: High recall threat detection for RAG pre-filtering")
        print(f"Target recall: {self.recall_target:.1%}")
        print("="*60)
        
        # Step 1: Load dataset
        df = self.load_dataset(csv_path, sample_size)
        
        # Step 2: Analyze dataset
        analysis_info = self.analyze_dataset(df)
        if not analysis_info:
            return None
        
        # Step 3: Prepare features
        X, y = self.prepare_features(df, analysis_info)
        
        # Step 4: Split dataset
        X_train, X_test, y_train, y_test = self.split_dataset(X, y, test_size)
        
        # Step 5: Train model
        cv_results = self.train_cost_sensitive_model(X_train, y_train)
        
        # Step 6: Optimize threshold
        self.optimize_threshold_for_recall(X_test, y_test)
        
        # Step 7: Evaluate model
        evaluation_results = self.evaluate_model(X_test, y_test)
        
        # Store all results
        self.results = {
            **cv_results,
            **evaluation_results,
            'dataset_info': analysis_info
        }
        
        # Step 8: Save model
        model_path = self.save_model()
        
        print(f"\n🎉 Training pipeline completed successfully!")
        print(f"📁 Model saved to: {model_path}")
        
        return model_path

def main():
    """Main training function"""
    # Configuration
    csv_path = "../data/cybersecurity_logs.csv"  # Update this path
    sample_size = None  # Set to a number (e.g., 100000) for faster training on large datasets
    recall_target = 0.95  # Target 95% recall for RAG pre-filtering
    
    # Initialize trainer
    trainer = CostSensitiveThreatTrainer(recall_target=recall_target)
    
    # Run training pipeline
    model_path = trainer.run_training_pipeline(
        csv_path=csv_path,
        sample_size=sample_size,
        test_size=0.2
    )
    
    if model_path:
        print(f"\n✅ Training completed successfully!")
        print(f"📁 Model available at: {model_path}")
        print(f"🎯 Use this model for RAG pre-filtering with high recall")
    else:
        print("❌ Training failed!")

if __name__ == "__main__":
    main()