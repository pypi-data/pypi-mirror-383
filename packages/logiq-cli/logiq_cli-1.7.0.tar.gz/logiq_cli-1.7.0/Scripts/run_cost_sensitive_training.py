"""
Complete Cost-Sensitive Training and Evaluation Workflow
Run this script to train and test the cost-sensitive threat detection model
"""

import sys
from pathlib import Path
import pandas as pd

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from cost_sensitive_trainer import CostSensitiveTrainer
from cost_sensitive_evaluator import CostSensitiveModelEvaluator

def check_data_file(csv_path: str) -> bool:
    """Check if data file exists and show basic info"""
    print(f"🔍 Checking data file: {csv_path}")
    
    if not Path(csv_path).exists():
        print(f"❌ File not found: {csv_path}")
        return False
    
    try:
        # Read just the header to check columns
        df_sample = pd.read_csv(csv_path, nrows=1)
        print(f"✅ File found with columns: {list(df_sample.columns)}")
        
        # Get file size
        file_size = Path(csv_path).stat().st_size / (1024 * 1024)  # MB
        print(f"📊 File size: {file_size:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def main():
    """Main training and evaluation workflow"""
    print("🚀 Cost-Sensitive Threat Detection Training Pipeline")
    print("="*60)
    
    # Configuration
    data_path = "../data/cybersecurity_threat_detection_logs.csv"
    sample_size = 10000  # Use smaller sample for testing
    
    # Check data file
    if not check_data_file(data_path):
        print("\n💡 Available data files:")
        data_dir = Path("../data")
        if data_dir.exists():
            for csv_file in data_dir.glob("*.csv"):
                print(f"   - {csv_file.name}")
        else:
            print("   - No data directory found")
        return
    
    try:
        print(f"\n📚 Step 1: Training Cost-Sensitive Model")
        print("-" * 40)
        
        # Initialize trainer
        trainer = CostSensitiveTrainer()
        
        # Train model with sample data
        model_path = trainer.train_model(
            csv_path=data_path,
            sample_size=sample_size,  # Use sample for faster training
            test_size=0.2,
            random_state=42
        )
        
        print(f"✅ Training completed! Model saved to: {model_path}")
        
        print(f"\n🔍 Step 2: Evaluating Model Performance")
        print("-" * 40)
        
        # Initialize evaluator
        evaluator = CostSensitiveModelEvaluator(model_path)
        
        # Run evaluation on remaining data
        report_path = evaluator.run_comprehensive_evaluation(
            test_csv_path=data_path,
            sample_size=sample_size // 2,  # Use different sample for testing
            sample_logs=[
                "Oct 11 13:45:01 sshd[2541]: Failed password for invalid user admin from 192.168.1.100",
                "CVE-2021-44228 Log4j RCE exploitation attempt detected",
                "SQL injection attempt: UNION SELECT * FROM users",
                "User john.doe logged in successfully from office network",
                "Daily backup completed successfully - 2.5GB archived",
                "Suspicious PowerShell execution detected: Invoke-Expression base64",
                "Normal web request: GET /api/users/profile HTTP/200",
                "Multiple failed SSH attempts from 203.45.67.89"
            ]
        )
        
        print(f"✅ Evaluation completed! Report saved to: {report_path}")
        
        print(f"\n🎉 Training and Evaluation Pipeline Completed!")
        print("="*60)
        print("📄 Next Steps:")
        print("   1. Review the evaluation report for performance metrics")
        print("   2. Check threat detection rate for RAG pre-filtering suitability")
        print("   3. Test with your specific log formats if needed")
        print("   4. Integrate model into your RAG pipeline")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if the CSV file has the right format")
        print("   2. Ensure pandas, sklearn, numpy are installed")
        print("   3. Verify sufficient disk space for model files")
        print("   4. Try with a smaller sample_size")

if __name__ == "__main__":
    main()