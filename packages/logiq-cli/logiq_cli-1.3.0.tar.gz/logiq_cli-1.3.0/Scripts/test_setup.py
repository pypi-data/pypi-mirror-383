"""
Quick Test Script for Cost-Sensitive Model
Test the training and evaluation pipeline with minimal setup
"""

import sys
from pathlib import Path

def test_imports():
    """Test if all required packages are available"""
    print("🧪 Testing Package Imports:")
    print("-" * 30)
    
    packages = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('sklearn', None),
        ('joblib', None)
    ]
    
    missing = []
    for package, alias in packages:
        try:
            if alias:
                exec(f"import {package} as {alias}")
            else:
                exec(f"import {package}")
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n💡 Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    else:
        print(f"\n✅ All packages available!")
        return True

def check_data_files():
    """Check available data files"""
    print("\n📁 Checking Data Files:")
    print("-" * 25)
    
    data_dir = Path("../data")
    if not data_dir.exists():
        print("❌ Data directory not found")
        return []
    
    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        print("❌ No CSV files found")
        return []
    
    print("✅ Available CSV files:")
    for csv_file in csv_files:
        file_size = csv_file.stat().st_size / (1024 * 1024)  # MB
        print(f"   - {csv_file.name} ({file_size:.1f} MB)")
    
    return csv_files

def test_training_pipeline():
    """Test the complete pipeline"""
    print("\n🚀 Testing Training Pipeline:")
    print("-" * 30)
    
    # Check imports
    if not test_imports():
        return False
    
    # Check data
    csv_files = check_data_files()
    if not csv_files:
        return False
    
    # Try to import our modules
    try:
        from cost_sensitive_trainer import CostSensitiveThreatTrainer
        from cost_sensitive_evaluator import CostSensitiveModelEvaluator
        print("✅ Custom modules imported successfully")
    except ImportError as e:
        print(f"❌ Custom module import failed: {e}")
        return False
    
    print("\n🎯 Ready to Train!")
    print("Run: python run_cost_sensitive_training.py")
    
    return True

def main():
    """Main test function"""
    print("🧪 Cost-Sensitive Model Test Suite")
    print("=" * 40)
    
    success = test_training_pipeline()
    
    if success:
        print("\n✅ All tests passed! Ready for training.")
        print("\n📋 Quick Start Commands:")
        print("   1. python test_setup.py              # This script")
        print("   2. python run_cost_sensitive_training.py  # Full pipeline")
        print("   3. Check the generated reports in models/")
    else:
        print("\n❌ Setup issues found. Please fix before training.")

if __name__ == "__main__":
    main()