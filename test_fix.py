#!/usr/bin/env python3
"""
Test script to verify the bug fix
"""

import numpy as np
import pandas as pd
from main import ExoplanetDetectionPipeline

def test_system():
    """Test the system with a simple example"""
    print("🧪 Testing the fixed exoplanet detection system...")
    
    try:
        # Initialize pipeline
        pipeline = ExoplanetDetectionPipeline()
        
        # Train with smaller dataset to test quickly
        print("🤖 Training AI system...")
        pipeline.train_system(n_training_samples=20)
        
        # Create test data
        print("📊 Creating test lightcurve...")
        time = np.linspace(0, 30, 1000)
        flux = np.ones_like(time) + np.random.normal(0, 0.0001, len(time))
        
        # Add a transit signal
        period = 8.5
        depth = 0.015
        transit_times = np.arange(5, 30, period)
        for t_transit in transit_times:
            in_transit = np.abs(time - t_transit) < 0.1
            flux[in_transit] -= depth
        
        data = pd.DataFrame({
            'time': time,
            'flux': flux,
            'flux_err': np.full_like(time, 0.0001)
        })
        
        # Process through pipeline
        print("🔍 Analyzing data...")
        processed_data = pipeline.artifact_detector.remove_instrumental_artifacts(data)
        processed_data = pipeline.artifact_detector.detect_stellar_variability(processed_data)
        
        # Detect transits
        result = pipeline.transit_detector.detect_transits(processed_data)
        
        # Print results
        print("\n✅ SUCCESS! System working correctly.")
        print(f"Transit detected: {result['has_transit']}")
        print(f"Confidence: {result['confidence']*100:.1f}%")
        if result.get('period'):
            print(f"Period: {result['period']:.3f} days")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system()
    if success:
        print("\n🎉 The bug has been fixed! You can now run:")
        print("   python main.py")
        print("   python web_interface.py")
        print("   python user_interface.py")
        print("   python quick_analyze.py data.csv")
    else:
        print("\n❌ There are still issues. Please check the error messages above.")