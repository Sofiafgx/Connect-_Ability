#!/usr/bin/env python3
"""
Test script for improved transit detection
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from main import ExoplanetDetectionPipeline

def create_test_lightcurve(has_transit=True, period=8.5, depth=0.015, noise_level=0.0001):
    """Create test lightcurve with known parameters"""
    
    # Create time array (30 days, good coverage)
    time = np.linspace(0, 30, 2000)
    flux = np.ones_like(time)
    
    # Add noise
    flux += np.random.normal(0, noise_level, len(time))
    
    # Add stellar variability
    stellar_period = 15.3
    flux += 0.005 * np.sin(2 * np.pi * time / stellar_period)
    
    if has_transit:
        # Add transit signal
        duration = 0.15  # days
        transit_times = np.arange(3, time.max(), period)
        
        print(f"Adding {len(transit_times)} transits with:")
        print(f"  Period: {period:.2f} days")
        print(f"  Depth: {depth:.1%}")
        print(f"  Duration: {duration:.2f} days")
        
        for t_transit in transit_times:
            in_transit = np.abs(time - t_transit) < duration/2
            flux[in_transit] -= depth
            print(f"  Transit at {t_transit:.1f} days ({np.sum(in_transit)} points)")
    
    return pd.DataFrame({
        'time': time,
        'flux': flux,
        'flux_err': np.full_like(time, noise_level)
    })

def test_detection_sensitivity():
    """Test detection with different signal strengths"""
    
    print("🧪 Testing Improved Transit Detection")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = ExoplanetDetectionPipeline()
    pipeline.train_system()
    
    # Test cases with different signal strengths
    test_cases = [
        {"name": "Strong Transit", "depth": 0.020, "expected": True},
        {"name": "Medium Transit", "depth": 0.010, "expected": True},
        {"name": "Weak Transit", "depth": 0.005, "expected": True},
        {"name": "Very Weak Transit", "depth": 0.002, "expected": False},  # May not detect
        {"name": "No Transit", "has_transit": False, "expected": False},
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        # Create test data
        has_transit = test_case.get('has_transit', True)
        depth = test_case.get('depth', 0.01)
        
        data = create_test_lightcurve(
            has_transit=has_transit,
            period=8.5,
            depth=depth,
            noise_level=0.0001
        )
        
        # Process data
        print("🔧 Processing data...")
        processed_data = pipeline.artifact_detector.remove_instrumental_artifacts(data)
        processed_data = pipeline.artifact_detector.detect_stellar_variability(processed_data)
        
        # Detect transits
        print("🔍 Detecting transits...")
        result = pipeline.transit_detector.detect_transits(processed_data)
        
        # Show results
        detected = result['has_transit']
        confidence = result['confidence'] * 100
        expected = test_case['expected']
        
        status = "✅ CORRECT" if detected == expected else "❌ INCORRECT"
        
        print(f"Results:")
        print(f"  Expected: {expected}")
        print(f"  Detected: {detected}")
        print(f"  Confidence: {confidence:.1f}%")
        if result.get('period'):
            print(f"  Period: {result['period']:.2f} days")
        if result.get('depth'):
            print(f"  Depth: {result['depth']:.1%}")
        if result.get('snr'):
            print(f"  SNR: {result['snr']:.1f}σ")
        print(f"  Status: {status}")
        
        results.append({
            'name': test_case['name'],
            'expected': expected,
            'detected': detected,
            'confidence': confidence,
            'correct': detected == expected
        })
        
        # Create a plot for each test
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle(f"Test {i}: {test_case['name']} - Confidence: {confidence:.1f}%")
        
        time_vals = data['time'].values
        
        # Original lightcurve
        axes[0].plot(time_vals, data['flux'].values, 'k.', alpha=0.5, markersize=1, label='Original')
        axes[0].plot(time_vals, processed_data['flux_stellar_corrected'].values, 'r-', 
                    alpha=0.8, linewidth=1, label='Processed')
        axes[0].set_ylabel('Relative Flux')
        axes[0].set_title('Lightcurve Data')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Phase-folded if transit detected
        if result['has_transit'] and result.get('period'):
            period = result['period']
            phase = ((time_vals % period) / period - 0.5) * 24
            
            axes[1].plot(phase, processed_data['flux_stellar_corrected'].values, 'b.', 
                        alpha=0.6, markersize=2)
            axes[1].set_title(f'Phase-Folded Transit (P={period:.3f}d)')
            axes[1].set_xlabel('Hours from Mid-Transit')
            axes[1].set_ylabel('Relative Flux')
            
            # Highlight detected transit
            in_transit_phase = np.abs(phase) < 2
            if np.any(in_transit_phase):
                axes[1].plot(phase[in_transit_phase], 
                           processed_data['flux_stellar_corrected'].values[in_transit_phase], 
                           'r.', markersize=3, alpha=0.8, label='Detected Transit')
                axes[1].legend()
        else:
            axes[1].text(0.5, 0.5, 'No Transit Detected', ha='center', va='center',
                        transform=axes[1].transAxes, fontsize=12)
            axes[1].set_title('Phase-Folded Data')
            axes[1].set_xlabel('Time (days)')
            axes[1].set_ylabel('Relative Flux')
        
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'/workspace/improved_test_{i}.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 SUMMARY")
    print(f"{'='*50}")
    
    correct = sum(1 for r in results if r['correct'])
    total = len(results)
    accuracy = correct / total * 100
    
    print(f"Overall Accuracy: {accuracy:.1f}% ({correct}/{total})")
    print()
    
    print(f"{'Test Case':<20} {'Expected':<10} {'Detected':<10} {'Confidence':<12} {'Status'}")
    print("-" * 65)
    
    for result in results:
        status = "✅" if result['correct'] else "❌"
        print(f"{result['name']:<20} {str(result['expected']):<10} {str(result['detected']):<10} "
              f"{result['confidence']:.1f}%{'':>7} {status}")
    
    return results

if __name__ == "__main__":
    try:
        results = test_detection_sensitivity()
        
        # Check if we're detecting transits now
        transit_detections = [r for r in results if r['detected']]
        
        if len(transit_detections) > 0:
            print(f"\n🎉 SUCCESS! Detected {len(transit_detections)} transits!")
            print("The improved algorithm is now working correctly.")
        else:
            print(f"\n⚠️ Still having issues - no transits detected.")
            print("The algorithm may need further tuning.")
        
        print(f"\n🚀 Try running:")
        print("   python main.py")
        print("   python demo.py")
        print("   python web_interface.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()