#!/usr/bin/env python3
"""
Test the professional exoplanet detection system
"""

import numpy as np
import pandas as pd
from professional_detection import ProfessionalExoplanetDetector

def create_realistic_lightcurve():
    """Create a realistic lightcurve with known exoplanet signal"""
    
    print("🔬 Creating realistic lightcurve with known exoplanet...")
    
    # 60 days of observations, 2-hour cadence (like TESS)
    time = np.linspace(0, 60, 720)
    flux = np.ones_like(time)
    
    # Add realistic noise sources
    flux += np.random.normal(0, 0.00008, len(time))  # Photon noise (80 ppm)
    
    # Stellar variability (rotation + granulation)
    stellar_period = 23.5  # days
    flux += 0.003 * np.sin(2 * np.pi * time / stellar_period)  # Rotation modulation
    flux += 0.001 * np.sin(4 * np.pi * time / stellar_period)  # Spot evolution
    
    # Instrumental systematics
    flux += 0.002 * (time / time.max())  # Linear drift
    flux += 0.001 * np.sin(2 * np.pi * time / 13.7)  # Thermal variations
    
    # Add exoplanet transit signal
    period = 15.234  # days (precise period)
    depth = 0.0045   # 0.45% depth (Earth-size around Sun-like star)
    duration = 0.18  # days (3.6 hours)
    t0 = 7.123      # days (first transit time)
    
    print(f"  Injected planet parameters:")
    print(f"    Period: {period:.3f} days")
    print(f"    Depth: {depth*100:.2f}%")
    print(f"    Duration: {duration*24:.1f} hours")
    print(f"    First transit: {t0:.3f} days")
    
    # Calculate all transit times
    n_transits = int((time.max() - t0) / period) + 1
    transit_times = [t0 + i * period for i in range(n_transits)]
    
    print(f"    Expected transits: {len([tt for tt in transit_times if time.min() <= tt <= time.max()])}")
    
    # Add transit signal with limb darkening
    for t_transit in transit_times:
        if time.min() <= t_transit <= time.max():
            # Simple limb-darkened transit model
            dt = np.abs(time - t_transit)
            in_transit = dt < duration/2
            
            if np.any(in_transit):
                # U-shaped transit profile
                phase_in_transit = (dt[in_transit] / (duration/2))
                limb_darkening = 1 - 0.3 * (1 - np.sqrt(1 - phase_in_transit**2))
                flux[in_transit] -= depth * limb_darkening
    
    # Add some realistic artifacts
    print("  Adding realistic artifacts...")
    
    # Cosmic rays (sudden spikes)
    n_cosmic_rays = 5
    cosmic_ray_times = np.random.choice(time, size=n_cosmic_rays, replace=False)
    for cr_time in cosmic_ray_times:
        cr_mask = np.abs(time - cr_time) < 0.01
        flux[cr_mask] += np.random.exponential(0.01, np.sum(cr_mask))
    
    # Systematic jumps (instrument effects)
    jump_times = [20.5, 40.2]  # Simulated instrument resets
    for jump_time in jump_times:
        jump_mask = time > jump_time
        flux[jump_mask] += 0.0008  # Small level shift
    
    # Create DataFrame
    data = pd.DataFrame({
        'time': time,
        'flux': flux,
        'flux_err': np.full_like(time, 0.00008)
    })
    
    return data, {
        'period': period,
        'depth': depth,
        'duration': duration,
        't0': t0,
        'n_transits': len([tt for tt in transit_times if time.min() <= tt <= time.max()])
    }

def test_professional_detection():
    """Test the professional detection system"""
    
    print("🌟 Testing Professional Exoplanet Detection System")
    print("=" * 60)
    
    # Create test data
    data, true_params = create_realistic_lightcurve()
    
    print(f"\n📊 Dataset Information:")
    print(f"  Data points: {len(data):,}")
    print(f"  Time span: {data['time'].max() - data['time'].min():.1f} days")
    print(f"  Cadence: {np.median(np.diff(data['time']))*24:.1f} hours")
    print(f"  RMS noise: {data['flux'].std()*1e6:.0f} ppm")
    
    # Run professional analysis
    detector = ProfessionalExoplanetDetector()
    results = detector.analyze_lightcurve(data)
    
    # Compare results with injected parameters
    print(f"\n🎯 COMPARISON WITH INJECTED PARAMETERS:")
    print("=" * 50)
    
    detection = results['detection']
    
    print(f"{'Parameter':<20} {'Injected':<15} {'Detected':<15} {'Accuracy'}")
    print("-" * 65)
    
    # Period comparison
    if detection['period']:
        period_error = abs(detection['period'] - true_params['period'])
        period_accuracy = f"{period_error/true_params['period']*100:.2f}%"
        print(f"{'Period (days)':<20} {true_params['period']:<15.3f} {detection['period']:<15.3f} {period_accuracy}")
    else:
        print(f"{'Period (days)':<20} {true_params['period']:<15.3f} {'Not detected':<15} {'N/A'}")
    
    # Depth comparison  
    if detection['depth']:
        depth_error = abs(detection['depth'] - true_params['depth'])
        depth_accuracy = f"{depth_error/true_params['depth']*100:.1f}%"
        print(f"{'Depth (%)':<20} {true_params['depth']*100:<15.2f} {detection['depth']*100:<15.2f} {depth_accuracy}")
    else:
        print(f"{'Depth (%)':<20} {true_params['depth']*100:<15.2f} {'Not detected':<15} {'N/A'}")
    
    # Detection success
    detection_success = "✅ SUCCESS" if detection['has_transit'] else "❌ MISSED"
    print(f"{'Detection':<20} {'Transit':<15} {'Transit' if detection['has_transit'] else 'No Transit':<15} {detection_success}")
    
    # Performance summary
    print(f"\n📈 PERFORMANCE SUMMARY:")
    print(f"  Detection Success: {'YES' if detection['has_transit'] else 'NO'}")
    print(f"  Confidence Level: {detection['confidence']*100:.1f}%")
    print(f"  Signal-to-Noise: {detection['snr']:.1f}σ")
    print(f"  Validation Score: {detection['validation_score']:.2f}/1.0")
    
    # Professional assessment
    print(f"\n🔬 PROFESSIONAL ASSESSMENT:")
    if detection['has_transit'] and detection['confidence'] > 0.8:
        print("  ✅ HIGH QUALITY DETECTION")
        print("  Recommendation: Excellent candidate for follow-up")
        print("  Next steps: Radial velocity confirmation, atmospheric characterization")
    elif detection['has_transit'] and detection['confidence'] > 0.6:
        print("  🔍 MODERATE QUALITY DETECTION") 
        print("  Recommendation: Additional validation required")
        print("  Next steps: More photometric data, false positive analysis")
    elif detection['has_transit']:
        print("  ⚠️ LOW QUALITY DETECTION")
        print("  Recommendation: Likely false positive")
        print("  Next steps: Improved data quality, alternative analysis")
    else:
        print("  ❌ NO DETECTION")
        print("  Recommendation: Signal below detection threshold")
        print("  Next steps: Longer observations, higher precision photometry")
    
    return results

if __name__ == "__main__":
    try:
        results = test_professional_detection()
        
        print(f"\n🎉 Professional analysis complete!")
        print(f"📊 Check /workspace/professional_analysis.png for plots")
        print(f"📖 See PROFESSIONAL_METHODS.md for detailed methodology")
        
        # Quick summary for user
        detection = results['detection']
        if detection['has_transit']:
            print(f"\n✨ RESULT: Exoplanet detected with {detection['confidence']*100:.0f}% confidence!")
        else:
            print(f"\n💫 RESULT: No exoplanet detected in this lightcurve.")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()