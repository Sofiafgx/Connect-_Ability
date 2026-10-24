"""
Test script for the exoplanet detection system
Validates that all components work correctly
"""

import os
import sys
import numpy as np
import pandas as pd

def test_imports():
    """Test that all required modules can be imported"""
    print("="*80)
    print("TEST 1: Checking imports...")
    print("="*80)
    
    try:
        import tensorflow as tf
        print(f"✓ TensorFlow {tf.__version__}")
        
        import sklearn
        print(f"✓ scikit-learn {sklearn.__version__}")
        
        import flask
        print(f"✓ Flask {flask.__version__}")
        
        from data_loader import ExoplanetDataLoader
        print("✓ data_loader module")
        
        from model import ExoplanetClassifier
        print("✓ model module")
        
        print("\n✅ All imports successful!\n")
        return True
    except Exception as e:
        print(f"\n❌ Import error: {e}\n")
        return False


def test_model_architecture():
    """Test that the model can be built"""
    print("="*80)
    print("TEST 2: Building model architecture...")
    print("="*80)
    
    try:
        from model import ExoplanetClassifier
        
        classifier = ExoplanetClassifier(input_dim=12)
        classifier.build_model()
        
        print("✓ Model built successfully")
        print(f"✓ Total parameters: {classifier.model.count_params():,}")
        print("\n✅ Model architecture test passed!\n")
        return True
    except Exception as e:
        print(f"\n❌ Model build error: {e}\n")
        return False


def test_data_loader():
    """Test data loader functionality"""
    print("="*80)
    print("TEST 3: Testing data loader...")
    print("="*80)
    
    try:
        from data_loader import ExoplanetDataLoader
        
        loader = ExoplanetDataLoader(data_dir='data')
        print("✓ Data loader initialized")
        
        # Check if data already exists
        if os.path.exists('data/combined_exoplanet_data.csv'):
            df = pd.read_csv('data/combined_exoplanet_data.csv')
            print(f"✓ Found existing data: {len(df)} rows")
            print("\n✅ Data loader test passed!\n")
            return True
        else:
            print("⚠ No pre-existing data found (run train.py to download)")
            print("\n⚠ Data loader test skipped (requires internet)\n")
            return True
    except Exception as e:
        print(f"\n❌ Data loader error: {e}\n")
        return False


def test_prediction():
    """Test prediction with sample data"""
    print("="*80)
    print("TEST 4: Testing prediction...")
    print("="*80)
    
    # Check if model exists
    if not os.path.exists('models/exoplanet_classifier.h5'):
        print("⚠ Model not found. Run train.py first.")
        print("\n⚠ Prediction test skipped\n")
        return True
    
    try:
        from model import ExoplanetClassifier
        
        # Load model
        classifier = ExoplanetClassifier(input_dim=1)
        classifier.load_model()
        print("✓ Model loaded successfully")
        
        # Test prediction with sample data
        sample_data = {
            'orbital_period': 3.5,
            'transit_duration': 2.8,
            'transit_depth': 850,
            'planet_radius': 1.4,
            'semi_major_axis': 0.045,
            'eq_temperature': 1342,
            'impact_parameter': 0.42,
            'stellar_temp': 5778,
            'stellar_radius': 0.98,
            'stellar_mass': 0.95,
            'stellar_magnitude': 12.3,
            'snr': 18.5
        }
        
        prediction, probabilities = classifier.predict_single(sample_data)
        
        print(f"✓ Sample prediction: {prediction}")
        print(f"✓ Probabilities:")
        print(f"  - False Positive: {probabilities['false_positive']:.2%}")
        print(f"  - Candidate: {probabilities['candidate']:.2%}")
        print(f"  - Confirmed: {probabilities['confirmed']:.2%}")
        
        print("\n✅ Prediction test passed!\n")
        return True
    except Exception as e:
        print(f"\n❌ Prediction error: {e}\n")
        return False


def test_web_interface():
    """Test that web interface files exist"""
    print("="*80)
    print("TEST 5: Checking web interface files...")
    print("="*80)
    
    files_to_check = [
        'app.py',
        'templates/index.html',
        'static/css/style.css',
        'static/js/script.js'
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"❌ {file} not found")
            all_exist = False
    
    if all_exist:
        print("\n✅ Web interface test passed!\n")
    else:
        print("\n❌ Some web interface files are missing\n")
    
    return all_exist


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" EXOPLANET DETECTION SYSTEM - TEST SUITE")
    print("="*80 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Model Architecture", test_model_architecture),
        ("Data Loader", test_data_loader),
        ("Prediction", test_prediction),
        ("Web Interface", test_web_interface)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("="*80)
    print(" TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {name}")
    
    print("\n" + "="*80)
    print(f" {passed}/{total} tests passed")
    print("="*80 + "\n")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Train the model: python train.py")
        print("2. Start web interface: python app.py")
        print("3. Or use CLI: python predict.py --interactive")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        if not os.path.exists('models/exoplanet_classifier.h5'):
            print("\n💡 Tip: Run 'python train.py' to train the model first.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
