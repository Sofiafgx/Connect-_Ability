#!/usr/bin/env python3
"""
Demo Script for Exoplanet Transit Detection System
Shows how users can input data and get AI analysis results
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from main import ExoplanetDetectionPipeline
import time

def create_sample_lightcurve(has_transit=True, noise_level=0.0001):
    """Create a sample lightcurve for demonstration"""
    
    print(f"🔬 Generating sample lightcurve (transit: {has_transit})...")
    
    # Create time array (30 days, 2-hour cadence)
    time_array = np.linspace(0, 30, 360)
    flux_array = np.ones_like(time_array)
    
    # Add stellar variability (rotation)
    stellar_period = 12.5  # days
    flux_array += 0.008 * np.sin(2 * np.pi * time_array / stellar_period)
    
    # Add noise
    flux_array += np.random.normal(0, noise_level, len(time_array))
    
    if has_transit:
        # Add exoplanet transit signal
        planet_period = 7.2  # days
        transit_depth = 0.012  # 1.2% depth
        transit_duration = 0.15  # days
        
        # Calculate transit times
        transit_times = np.arange(3.5, time_array.max(), planet_period)
        
        for t_transit in transit_times:
            # Simple box-shaped transit
            in_transit = np.abs(time_array - t_transit) < transit_duration/2
            flux_array[in_transit] -= transit_depth
    
    # Add some instrumental artifacts
    artifact_times = np.random.choice(time_array, size=5, replace=False)
    for at in artifact_times:
        mask = np.abs(time_array - at) < 0.02
        flux_array[mask] += np.random.normal(0, 0.003, np.sum(mask))
    
    return pd.DataFrame({
        'time': time_array,
        'flux': flux_array,
        'flux_err': np.full_like(time_array, noise_level)
    })

def demonstrate_user_workflow():
    """Demonstrate the complete user workflow"""
    
    print("🌟" + "="*60)
    print("🌟 EXOPLANET TRANSIT DETECTION DEMO")
    print("🌟" + "="*60)
    print()
    print("This demo shows how users can input lightcurve data")
    print("and get AI-powered exoplanet detection results.")
    print()
    
    # Initialize the AI system
    print("🤖 Initializing AI Detection System...")
    pipeline = ExoplanetDetectionPipeline()
    
    print("📚 Training AI model (this happens once)...")
    start_time = time.time()
    pipeline.train_system(n_training_samples=50)  # Smaller for demo
    training_time = time.time() - start_time
    print(f"✅ AI system ready! (trained in {training_time:.1f} seconds)")
    print()
    
    # Test cases to demonstrate
    test_cases = [
        {"name": "Strong Transit Signal", "has_transit": True, "noise": 0.0001},
        {"name": "No Transit (False Positive Test)", "has_transit": False, "noise": 0.0001},
        {"name": "Weak Transit in Noisy Data", "has_transit": True, "noise": 0.0005},
    ]
    
    results_summary = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📊 TEST CASE {i}: {test_case['name']}")
        print("-" * 50)
        
        # 1. User creates/loads lightcurve data
        data = create_sample_lightcurve(
            has_transit=test_case['has_transit'],
            noise_level=test_case['noise']
        )
        
        print(f"📈 Data loaded: {len(data)} points, {data['time'].max():.1f} day span")
        
        # 2. AI analyzes the data
        print("🔍 AI analyzing data...")
        analysis_start = time.time()
        
        # Run through the complete pipeline
        processed_data = pipeline.artifact_detector.remove_instrumental_artifacts(data)
        processed_data = pipeline.artifact_detector.detect_stellar_variability(processed_data)
        transit_result = pipeline.transit_detector.detect_transits(processed_data)
        
        analysis_time = time.time() - analysis_start
        
        # 3. Present results to user
        confidence_pct = transit_result['confidence'] * 100
        
        print(f"⚡ Analysis completed in {analysis_time:.2f} seconds")
        print()
        print("🎯 RESULTS:")
        print(f"   Transit Detected: {'YES' if transit_result['has_transit'] else 'NO'}")
        print(f"   Confidence: {confidence_pct:.1f}%")
        
        if transit_result.get('period'):
            print(f"   Estimated Period: {transit_result['period']:.3f} days")
        if transit_result.get('depth'):
            print(f"   Transit Depth: {transit_result['depth']*100:.2f}%")
        if transit_result.get('snr'):
            print(f"   Signal-to-Noise: {transit_result['snr']:.1f}σ")
        
        # Interpretation
        if confidence_pct >= 90:
            interpretation = "🎯 VERY LIKELY genuine exoplanet transit"
        elif confidence_pct >= 70:
            interpretation = "🔍 PROBABLE transit - investigate further"
        elif confidence_pct >= 50:
            interpretation = "⚠️ UNCERTAIN - could be false positive"
        else:
            interpretation = "❌ UNLIKELY to be genuine transit"
        
        print(f"   Interpretation: {interpretation}")
        
        # Store results
        results_summary.append({
            'test_case': test_case['name'],
            'expected': test_case['has_transit'],
            'detected': transit_result['has_transit'],
            'confidence': confidence_pct,
            'correct': test_case['has_transit'] == transit_result['has_transit']
        })
        
        print()
        
        # Create a quick plot for this test case
        fig, axes = plt.subplots(2, 1, figsize=(10, 6))
        fig.suptitle(f"Test Case {i}: {test_case['name']} (Confidence: {confidence_pct:.1f}%)")
        
        time_vals = data['time'].values
        
        # Original lightcurve
        axes[0].plot(time_vals, data['flux'].values, 'k.', alpha=0.5, markersize=2, label='Original')
        axes[0].plot(time_vals, processed_data['flux_stellar_corrected'].values, 'r-', 
                    alpha=0.8, linewidth=1, label='AI Processed')
        axes[0].set_ylabel('Relative Flux')
        axes[0].set_title('Lightcurve Data')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Phase-folded if transit detected
        if transit_result['has_transit'] and transit_result.get('period'):
            period = transit_result['period']
            phase = ((time_vals % period) / period - 0.5) * 24
            
            axes[1].plot(phase, processed_data['flux_stellar_corrected'].values, 'b.', 
                        alpha=0.6, markersize=3)
            axes[1].set_title(f'Phase-Folded Transit (P={period:.3f}d)')
            axes[1].set_xlabel('Hours from Mid-Transit')
            axes[1].set_ylabel('Relative Flux')
        else:
            axes[1].text(0.5, 0.5, 'No Transit Detected', ha='center', va='center',
                        transform=axes[1].transAxes, fontsize=12)
            axes[1].set_title('Phase-Folded Data')
            axes[1].set_xlabel('Time (days)')
            axes[1].set_ylabel('Relative Flux')
        
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'/workspace/demo_test_case_{i}.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Plot saved as: demo_test_case_{i}.png")
        print()
    
    # Summary of all test cases
    print("="*60)
    print("📋 SUMMARY OF ALL TEST CASES")
    print("="*60)
    
    correct_detections = sum(1 for r in results_summary if r['correct'])
    total_tests = len(results_summary)
    accuracy = correct_detections / total_tests * 100
    
    print(f"Overall AI Accuracy: {accuracy:.1f}% ({correct_detections}/{total_tests})")
    print()
    
    print(f"{'Test Case':<35} {'Expected':<10} {'Detected':<10} {'Confidence':<12} {'Result'}")
    print("-" * 80)
    
    for result in results_summary:
        status = "✅ Correct" if result['correct'] else "❌ Incorrect"
        expected = "Transit" if result['expected'] else "No Transit"
        detected = "Transit" if result['detected'] else "No Transit"
        
        print(f"{result['test_case']:<35} {expected:<10} {detected:<10} "
              f"{result['confidence']:.1f}%{'':>7} {status}")
    
    print()
    print("🎉 Demo completed! The AI system successfully analyzed all test cases.")
    print()
    print("💡 HOW USERS INTERACT WITH THE SYSTEM:")
    print("   1. 🌐 Web Interface: Upload files via browser")
    print("   2. 🖥️ Desktop GUI: User-friendly application")
    print("   3. ⚡ Command Line: Quick analysis for experts")
    print()
    print("📊 Each method provides the same AI analysis with confidence percentages!")

def demonstrate_different_input_methods():
    """Show how users can input data in different ways"""
    
    print("\n" + "="*60)
    print("📊 DIFFERENT WAYS USERS CAN INPUT DATA")
    print("="*60)
    
    # Create sample data
    sample_data = create_sample_lightcurve(has_transit=True, noise_level=0.0001)
    
    print("\n1. 📁 FILE UPLOAD (CSV Format)")
    print("   Users can upload CSV files with columns:")
    sample_csv = sample_data.head(10).to_csv(index=False)
    print("   " + "\n   ".join(sample_csv.split('\n')[:6]))
    print("   ...")
    
    print("\n2. ✏️ MANUAL ENTRY")
    print("   Users can copy/paste data directly:")
    print("   Format: time,flux (one pair per line)")
    for i in range(5):
        print(f"   {sample_data.iloc[i]['time']:.3f},{sample_data.iloc[i]['flux']:.6f}")
    print("   ...")
    
    print("\n3. 🌐 URL INPUT")
    print("   Users can provide direct links to data files:")
    print("   Example: https://example.com/lightcurve.csv")
    
    print("\n4. 🎲 DEMO DATA")
    print("   Pre-loaded examples for testing:")
    print("   • With Transit Signal (for positive detection)")
    print("   • Without Transit (for false positive testing)")
    print("   • Noisy Data (challenging dataset)")
    
    print("\n✨ ALL METHODS PROVIDE THE SAME AI ANALYSIS:")
    print("   → Confidence percentage (0-100%)")
    print("   → Transit detection (YES/NO)")
    print("   → Orbital period estimate")
    print("   → Transit depth measurement")
    print("   → Data quality assessment")

if __name__ == "__main__":
    try:
        # Run the main demonstration
        demonstrate_user_workflow()
        
        # Show input methods
        demonstrate_different_input_methods()
        
        print("\n🌟 Demo completed successfully!")
        print("🚀 Try the different interfaces:")
        print("   • Web: python web_interface.py")
        print("   • GUI: python user_interface.py") 
        print("   • CLI: python quick_analyze.py data.csv")
        
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()