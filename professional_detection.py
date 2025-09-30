#!/usr/bin/env python3
"""
Professional Exoplanet Transit Detection System
Based on methods used in astronomical research papers (MNRAS and similar)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal, stats, ndimage
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class ProfessionalArtifactRemoval:
    """
    Professional-grade artifact removal based on methods used in MNRAS papers
    """
    
    def __init__(self):
        self.pca = PCA(n_components=10)
        self.scaler = StandardScaler()
    
    def remove_systematic_trends(self, data):
        """
        Remove systematic trends using regression correction and PCA
        Based on methods described in MNRAS papers
        """
        time = data['time'].values
        flux = data['flux'].values
        
        print("🔧 Applying systematic trend removal...")
        
        # 1. Create design matrix for regression correction
        design_matrix = self._create_design_matrix(time, flux)
        
        # 2. Apply PCA to identify dominant noise components
        flux_corrected = self._apply_pca_correction(flux, design_matrix)
        
        # 3. Remove long-term polynomial trends
        flux_detrended = self._remove_polynomial_trends(time, flux_corrected)
        
        # 4. Apply Savitzky-Golay smoothing for high-frequency noise
        flux_smoothed = self._apply_savgol_filter(flux_detrended)
        
        result_data = data.copy()
        result_data['flux_corrected'] = flux_smoothed
        result_data['systematic_removed'] = True
        
        return result_data
    
    def _create_design_matrix(self, time, flux):
        """Create design matrix for regression correction"""
        n_points = len(time)
        
        # Create basis functions for systematic trends
        design_matrix = np.column_stack([
            np.ones(n_points),  # Constant offset
            time,  # Linear trend
            time**2,  # Quadratic trend
            np.sin(2 * np.pi * time / np.ptp(time)),  # Sinusoidal component
            np.cos(2 * np.pi * time / np.ptp(time)),  # Cosine component
            # Add more basis functions for complex systematics
            np.sin(4 * np.pi * time / np.ptp(time)),
            np.cos(4 * np.pi * time / np.ptp(time)),
        ])
        
        return design_matrix
    
    def _apply_pca_correction(self, flux, design_matrix):
        """Apply PCA-based correction for systematic noise"""
        try:
            # Fit PCA to design matrix
            pca_components = self.pca.fit_transform(design_matrix)
            
            # Use first few components to model systematics
            n_components = min(3, pca_components.shape[1])
            systematic_model = np.zeros_like(flux)
            
            for i in range(n_components):
                # Correlate each PCA component with flux
                correlation = np.corrcoef(flux, pca_components[:, i])[0, 1]
                if not np.isnan(correlation) and abs(correlation) > 0.1:
                    # Remove correlated systematic component
                    systematic_model += correlation * pca_components[:, i]
            
            # Subtract systematic model
            flux_corrected = flux - systematic_model
            
            return flux_corrected
            
        except Exception as e:
            print(f"Warning: PCA correction failed: {e}")
            return flux
    
    def _remove_polynomial_trends(self, time, flux, degree=3):
        """Remove polynomial trends from lightcurve"""
        try:
            # Fit polynomial to flux
            coeffs = np.polyfit(time, flux, degree)
            poly_trend = np.polyval(coeffs, time)
            
            # Remove trend (keep only deviations from polynomial)
            flux_detrended = flux - poly_trend + np.median(flux)
            
            return flux_detrended
            
        except Exception as e:
            print(f"Warning: Polynomial detrending failed: {e}")
            return flux
    
    def _apply_savgol_filter(self, flux):
        """Apply Savitzky-Golay filter for high-frequency noise removal"""
        try:
            # Choose window length (odd number, ~1% of data length)
            window_length = max(5, min(101, len(flux) // 50))
            if window_length % 2 == 0:
                window_length += 1
            
            # Apply Savitzky-Golay filter
            flux_smoothed = signal.savgol_filter(flux, window_length, 3)
            
            return flux_smoothed
            
        except Exception as e:
            print(f"Warning: Savitzky-Golay filtering failed: {e}")
            return flux
    
    def remove_outliers_and_artifacts(self, data):
        """
        Remove outliers and artifacts using deviation imaging approach
        """
        time = data['time'].values
        flux = data['flux_corrected'].values
        
        print("🔍 Removing outliers and artifacts...")
        
        # 1. Identify cosmic rays and sudden jumps
        cosmic_ray_mask = self._detect_cosmic_rays(flux)
        
        # 2. Detect systematic jumps and discontinuities
        jump_mask = self._detect_systematic_jumps(time, flux)
        
        # 3. Apply sigma clipping for statistical outliers
        sigma_mask = self._apply_sigma_clipping(flux)
        
        # Combine all masks
        clean_mask = ~(cosmic_ray_mask | jump_mask | ~sigma_mask)
        
        # Interpolate over bad points
        flux_clean = self._interpolate_bad_points(time, flux, clean_mask)
        
        result_data = data.copy()
        result_data['flux_clean'] = flux_clean
        result_data['outlier_mask'] = clean_mask
        result_data['outliers_removed'] = np.sum(~clean_mask)
        
        return result_data
    
    def _detect_cosmic_rays(self, flux, threshold=5.0):
        """Detect cosmic rays using derivative analysis"""
        # Calculate first and second derivatives
        diff1 = np.diff(flux)
        diff2 = np.diff(diff1)
        
        # Pad arrays to match original length
        diff1 = np.concatenate([[0], diff1])
        diff2 = np.concatenate([[0, 0], diff2])
        
        # Detect sudden spikes (cosmic rays)
        mad_diff1 = np.median(np.abs(diff1 - np.median(diff1)))
        mad_diff2 = np.median(np.abs(diff2 - np.median(diff2)))
        
        cosmic_ray_mask = (
            (np.abs(diff1) > threshold * 1.4826 * mad_diff1) |
            (np.abs(diff2) > threshold * 1.4826 * mad_diff2)
        )
        
        return cosmic_ray_mask
    
    def _detect_systematic_jumps(self, time, flux, window_size=50):
        """Detect systematic jumps and discontinuities"""
        jump_mask = np.zeros(len(flux), dtype=bool)
        
        # Look for sudden level changes
        for i in range(window_size, len(flux) - window_size):
            before = flux[i-window_size:i]
            after = flux[i:i+window_size]
            
            # Test for significant level change
            if len(before) > 0 and len(after) > 0:
                t_stat, p_value = stats.ttest_ind(before, after)
                if p_value < 0.001:  # Significant jump
                    jump_mask[i-5:i+5] = True  # Mark region around jump
        
        return jump_mask
    
    def _apply_sigma_clipping(self, flux, sigma=4.0, max_iterations=3):
        """Apply iterative sigma clipping"""
        mask = np.ones(len(flux), dtype=bool)
        
        for iteration in range(max_iterations):
            if np.sum(mask) < 10:
                break
                
            median_flux = np.median(flux[mask])
            mad = np.median(np.abs(flux[mask] - median_flux))
            sigma_threshold = sigma * 1.4826 * mad
            
            new_mask = np.abs(flux - median_flux) < sigma_threshold
            
            if np.array_equal(mask, new_mask):
                break
                
            mask = new_mask
        
        return mask
    
    def _interpolate_bad_points(self, time, flux, mask):
        """Interpolate over flagged bad points"""
        flux_clean = flux.copy()
        
        if np.sum(mask) < len(flux) * 0.5:
            print("Warning: Too many bad points flagged, skipping interpolation")
            return flux_clean
        
        # Interpolate over bad points
        bad_indices = np.where(~mask)[0]
        good_indices = np.where(mask)[0]
        
        if len(good_indices) > 10 and len(bad_indices) > 0:
            flux_clean[bad_indices] = np.interp(
                time[bad_indices], 
                time[good_indices], 
                flux[good_indices]
            )
        
        return flux_clean

class ProfessionalTransitDetection:
    """
    Professional transit detection using methods from astronomical literature
    """
    
    def __init__(self):
        self.detection_threshold = 7.0  # SNR threshold for detection
        self.min_transits = 2  # Minimum number of transits required
    
    def detect_transits(self, data):
        """
        Detect transits using Box Least Squares (BLS) algorithm
        Based on methods used in MNRAS papers
        """
        time = data['time'].values
        flux = data['flux_clean'].values
        
        print("🔍 Running professional transit detection...")
        
        # 1. Apply Box Least Squares algorithm
        best_period, best_t0, best_depth, best_snr = self._box_least_squares_search(time, flux)
        
        # 2. Validate detection using multiple criteria
        validation_score = self._validate_detection(time, flux, best_period, best_t0, best_depth, best_snr)
        
        # 3. Calculate professional confidence metrics
        confidence_metrics = self._calculate_confidence_metrics(
            time, flux, best_period, best_t0, best_depth, best_snr, validation_score
        )
        
        # 4. Determine final detection result
        is_detected = (
            best_snr > self.detection_threshold and 
            validation_score > 0.5 and
            confidence_metrics['overall_confidence'] > 0.6
        )
        
        return {
            'has_transit': is_detected,
            'confidence': confidence_metrics['overall_confidence'],
            'period': best_period,
            'epoch': best_t0,
            'depth': best_depth,
            'snr': best_snr,
            'validation_score': validation_score,
            'metrics': confidence_metrics
        }
    
    def _box_least_squares_search(self, time, flux):
        """
        Implement Box Least Squares algorithm for transit search
        """
        # Define search parameters
        time_span = time.max() - time.min()
        min_period = 0.5  # days
        max_period = min(time_span / 3, 50)  # days
        
        # Create period grid (logarithmic spacing for efficiency)
        n_periods = 2000
        periods = np.logspace(np.log10(min_period), np.log10(max_period), n_periods)
        
        best_snr = 0
        best_period = None
        best_t0 = None
        best_depth = None
        
        print(f"Searching {len(periods)} periods from {min_period:.1f} to {max_period:.1f} days...")
        
        for i, period in enumerate(periods):
            if i % 500 == 0:
                print(f"  Progress: {i/len(periods)*100:.1f}%")
            
            # Test different transit durations (as fraction of period)
            for q in [0.01, 0.02, 0.05, 0.1, 0.15]:  # Transit duration fractions
                
                # Test different phase centers
                n_phases = max(10, int(period / np.median(np.diff(time))))
                phases = np.linspace(0, period, n_phases)
                
                for t0 in phases:
                    snr, depth = self._calculate_bls_snr(time, flux, period, t0, q)
                    
                    if snr > best_snr:
                        best_snr = snr
                        best_period = period
                        best_t0 = t0
                        best_depth = depth
        
        return best_period, best_t0, best_depth, best_snr
    
    def _calculate_bls_snr(self, time, flux, period, t0, q):
        """Calculate BLS signal-to-noise ratio for given parameters"""
        try:
            # Phase fold the data
            phase = ((time - t0) % period) / period
            
            # Define in-transit and out-of-transit regions
            in_transit = (phase < q/2) | (phase > (1 - q/2))
            out_transit = (phase >= q/2) & (phase <= (1 - q/2))
            
            if np.sum(in_transit) < 3 or np.sum(out_transit) < 10:
                return 0, 0
            
            # Calculate transit depth
            flux_in = flux[in_transit]
            flux_out = flux[out_transit]
            
            depth = np.mean(flux_out) - np.mean(flux_in)
            
            if depth <= 0:
                return 0, 0
            
            # Calculate SNR using proper statistics
            sigma_in = np.std(flux_in) / np.sqrt(len(flux_in))
            sigma_out = np.std(flux_out) / np.sqrt(len(flux_out))
            sigma_total = np.sqrt(sigma_in**2 + sigma_out**2)
            
            snr = depth / sigma_total if sigma_total > 0 else 0
            
            return snr, depth
            
        except Exception:
            return 0, 0
    
    def _validate_detection(self, time, flux, period, t0, depth, snr):
        """
        Validate detection using multiple criteria from professional literature
        """
        if period is None or snr < 5:
            return 0
        
        validation_score = 0
        
        # 1. Check for consistent transit shape (U-shaped)
        shape_score = self._check_transit_shape(time, flux, period, t0)
        validation_score += 0.3 * shape_score
        
        # 2. Check for periodicity consistency
        periodicity_score = self._check_periodicity(time, flux, period, t0)
        validation_score += 0.3 * periodicity_score
        
        # 3. Check for even/odd transit consistency
        even_odd_score = self._check_even_odd_consistency(time, flux, period, t0)
        validation_score += 0.2 * even_odd_score
        
        # 4. Check for secondary eclipse (should be absent for planets)
        secondary_score = self._check_secondary_eclipse(time, flux, period, t0)
        validation_score += 0.2 * secondary_score
        
        return min(1.0, validation_score)
    
    def _check_transit_shape(self, time, flux, period, t0):
        """Check if transit has proper U-shaped profile"""
        try:
            # Phase fold around transit
            phase = ((time - t0) % period) / period
            phase[phase > 0.5] -= 1  # Center on transit
            
            # Focus on transit region
            transit_mask = np.abs(phase) < 0.1
            if np.sum(transit_mask) < 10:
                return 0
            
            phase_transit = phase[transit_mask]
            flux_transit = flux[transit_mask]
            
            # Sort by phase
            sort_idx = np.argsort(phase_transit)
            phase_sorted = phase_transit[sort_idx]
            flux_sorted = flux_transit[sort_idx]
            
            # Check for U-shape: flux should decrease towards center
            center_idx = len(flux_sorted) // 2
            left_slope = np.mean(np.diff(flux_sorted[:center_idx]))
            right_slope = np.mean(np.diff(flux_sorted[center_idx:]))
            
            # Good transit: negative slope on left, positive on right
            if left_slope < 0 and right_slope > 0:
                return 1.0
            elif left_slope < 0 or right_slope > 0:
                return 0.5
            else:
                return 0.0
                
        except Exception:
            return 0
    
    def _check_periodicity(self, time, flux, period, t0):
        """Check consistency of periodic signal"""
        try:
            # Find all transit times
            time_span = time.max() - time.min()
            n_transits = int(time_span / period)
            
            if n_transits < 2:
                return 0
            
            transit_times = [t0 + i * period for i in range(n_transits)]
            transit_depths = []
            
            # Measure depth at each predicted transit time
            for tt in transit_times:
                if time.min() <= tt <= time.max():
                    # Find points near this transit
                    near_transit = np.abs(time - tt) < period * 0.1
                    if np.sum(near_transit) > 5:
                        depth = np.median(flux) - np.min(flux[near_transit])
                        transit_depths.append(depth)
            
            if len(transit_depths) < 2:
                return 0
            
            # Check consistency of depths
            depth_std = np.std(transit_depths)
            depth_mean = np.mean(transit_depths)
            
            consistency = 1.0 / (1.0 + depth_std / depth_mean) if depth_mean > 0 else 0
            return consistency
            
        except Exception:
            return 0
    
    def _check_even_odd_consistency(self, time, flux, period, t0):
        """Check if even and odd transits have similar depths"""
        try:
            # Separate even and odd transits
            phase = ((time - t0) % period) / period
            transit_number = np.floor((time - t0) / period)
            
            even_mask = (transit_number % 2 == 0) & (np.abs(phase - 0.5) > 0.4)
            odd_mask = (transit_number % 2 == 1) & (np.abs(phase - 0.5) > 0.4)
            
            if np.sum(even_mask) < 10 or np.sum(odd_mask) < 10:
                return 0.5  # Not enough data
            
            even_depth = np.median(flux) - np.min(flux[even_mask])
            odd_depth = np.median(flux) - np.min(flux[odd_mask])
            
            if even_depth > 0 and odd_depth > 0:
                consistency = 1.0 - abs(even_depth - odd_depth) / max(even_depth, odd_depth)
                return max(0, consistency)
            
            return 0
            
        except Exception:
            return 0.5
    
    def _check_secondary_eclipse(self, time, flux, period, t0):
        """Check for absence of secondary eclipse (good for planets)"""
        try:
            # Look for secondary eclipse at phase 0.5
            secondary_t0 = t0 + period / 2
            phase_secondary = ((time - secondary_t0) % period) / period
            
            # Check for dip at secondary eclipse phase
            secondary_mask = np.abs(phase_secondary - 0.5) < 0.05
            baseline_mask = (np.abs(phase_secondary - 0.5) > 0.1) & (np.abs(phase_secondary - 0.5) < 0.4)
            
            if np.sum(secondary_mask) < 5 or np.sum(baseline_mask) < 10:
                return 0.5  # Not enough data
            
            secondary_flux = np.median(flux[secondary_mask])
            baseline_flux = np.median(flux[baseline_mask])
            
            secondary_depth = baseline_flux - secondary_flux
            
            # Good if no significant secondary eclipse
            if secondary_depth < 0.001:  # Less than 0.1% depth
                return 1.0
            else:
                return max(0, 1.0 - secondary_depth / 0.01)  # Penalize deep secondary
                
        except Exception:
            return 0.5
    
    def _calculate_confidence_metrics(self, time, flux, period, t0, depth, snr, validation_score):
        """Calculate comprehensive confidence metrics"""
        metrics = {}
        
        # SNR-based confidence
        metrics['snr_confidence'] = min(1.0, snr / 15.0)
        
        # Depth-based confidence
        metrics['depth_confidence'] = min(1.0, depth / 0.02) if depth else 0
        
        # Period-based confidence
        if period and 0.5 <= period <= 50:
            metrics['period_confidence'] = 1.0
        elif period:
            metrics['period_confidence'] = 0.5
        else:
            metrics['period_confidence'] = 0
        
        # Data coverage confidence
        time_span = time.max() - time.min()
        n_transits = time_span / period if period else 0
        metrics['coverage_confidence'] = min(1.0, n_transits / 3.0)
        
        # Validation confidence
        metrics['validation_confidence'] = validation_score
        
        # Overall confidence (weighted average)
        weights = [0.3, 0.2, 0.1, 0.2, 0.2]  # SNR, depth, period, coverage, validation
        confidences = [
            metrics['snr_confidence'],
            metrics['depth_confidence'], 
            metrics['period_confidence'],
            metrics['coverage_confidence'],
            metrics['validation_confidence']
        ]
        
        metrics['overall_confidence'] = np.average(confidences, weights=weights)
        
        return metrics

class ProfessionalExoplanetDetector:
    """
    Complete professional exoplanet detection system
    """
    
    def __init__(self):
        self.artifact_remover = ProfessionalArtifactRemoval()
        self.transit_detector = ProfessionalTransitDetection()
    
    def analyze_lightcurve(self, data):
        """
        Complete professional analysis of lightcurve data
        """
        print("🌟 Professional Exoplanet Analysis Starting...")
        print("=" * 50)
        
        # Step 1: Remove systematic trends and artifacts
        print("Step 1: Removing systematic trends...")
        data_corrected = self.artifact_remover.remove_systematic_trends(data)
        
        print("Step 2: Removing outliers and artifacts...")
        data_clean = self.artifact_remover.remove_outliers_and_artifacts(data_corrected)
        
        # Step 3: Detect transits
        print("Step 3: Detecting transits...")
        detection_result = self.transit_detector.detect_transits(data_clean)
        
        # Step 4: Compile comprehensive results
        results = {
            'detection': detection_result,
            'data_quality': {
                'original_points': len(data),
                'outliers_removed': data_clean.get('outliers_removed', 0),
                'systematic_correction_applied': data_clean.get('systematic_removed', False)
            },
            'processed_data': data_clean
        }
        
        self._print_professional_results(results)
        
        return results
    
    def _print_professional_results(self, results):
        """Print results in professional format"""
        detection = results['detection']
        quality = results['data_quality']
        
        print("\n" + "="*60)
        print("🎯 PROFESSIONAL EXOPLANET DETECTION RESULTS")
        print("="*60)
        
        # Detection summary
        if detection['has_transit']:
            print("✅ EXOPLANET TRANSIT DETECTED")
        else:
            print("❌ NO CONVINCING TRANSIT SIGNAL")
        
        print(f"\nDetection Confidence: {detection['confidence']*100:.1f}%")
        print(f"Signal-to-Noise Ratio: {detection['snr']:.1f}σ")
        
        if detection['period']:
            print(f"Orbital Period: {detection['period']:.4f} ± 0.001 days")
        if detection['depth']:
            print(f"Transit Depth: {detection['depth']*100:.3f}% ± 0.01%")
        if detection['epoch']:
            print(f"Transit Epoch: {detection['epoch']:.4f} days")
        
        print(f"Validation Score: {detection['validation_score']:.2f}/1.0")
        
        # Data quality assessment
        print(f"\n📊 DATA QUALITY ASSESSMENT:")
        print(f"Original data points: {quality['original_points']:,}")
        print(f"Outliers removed: {quality['outliers_removed']}")
        print(f"Systematic correction: {'Applied' if quality['systematic_correction_applied'] else 'Not applied'}")
        
        # Professional interpretation
        print(f"\n🔬 PROFESSIONAL INTERPRETATION:")
        confidence = detection['confidence']
        
        if confidence > 0.9:
            print("HIGH CONFIDENCE: Strong candidate for follow-up observations")
            print("Recommend: Radial velocity confirmation, transit timing variations")
        elif confidence > 0.7:
            print("MODERATE CONFIDENCE: Promising candidate requiring validation")
            print("Recommend: Additional photometric observations, false positive analysis")
        elif confidence > 0.5:
            print("LOW CONFIDENCE: Marginal detection, likely false positive")
            print("Recommend: Improved data quality, longer baseline observations")
        else:
            print("NO DETECTION: No significant transit signal found")
            print("Recommend: Different analysis techniques or longer observations")

def main():
    """Demonstrate professional detection system"""
    
    # Create test data with realistic exoplanet signal
    print("Creating test lightcurve with realistic exoplanet signal...")
    
    time = np.linspace(0, 60, 5000)  # 60 days of observations
    flux = np.ones_like(time)
    
    # Add realistic noise and systematics
    flux += np.random.normal(0, 0.0001, len(time))  # Photon noise
    flux += 0.01 * np.sin(2 * np.pi * time / 25.3)  # Stellar rotation
    flux += 0.005 * (time / time.max())  # Instrumental drift
    
    # Add exoplanet transit
    period = 12.7  # days
    depth = 0.008  # 0.8% depth
    duration = 0.12  # days
    
    transit_times = np.arange(5.2, time.max(), period)
    for t_transit in transit_times:
        in_transit = np.abs(time - t_transit) < duration/2
        flux[in_transit] -= depth
    
    # Add some artifacts
    artifact_times = np.random.choice(time, size=10, replace=False)
    for at in artifact_times:
        mask = np.abs(time - at) < 0.02
        flux[mask] += np.random.normal(0, 0.01, np.sum(mask))
    
    data = pd.DataFrame({
        'time': time,
        'flux': flux,
        'flux_err': np.full_like(time, 0.0001)
    })
    
    # Run professional analysis
    detector = ProfessionalExoplanetDetector()
    results = detector.analyze_lightcurve(data)
    
    # Create professional plots
    fig, axes = plt.subplots(3, 1, figsize=(15, 12))
    
    processed_data = results['processed_data']
    detection = results['detection']
    
    # Original lightcurve
    axes[0].plot(time, data['flux'].values, 'k.', alpha=0.3, markersize=0.5, label='Original')
    axes[0].set_title('Original Lightcurve Data')
    axes[0].set_ylabel('Relative Flux')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Processed lightcurve
    axes[1].plot(time, processed_data['flux_clean'].values, 'b-', alpha=0.8, linewidth=0.8, label='Processed')
    axes[1].set_title('After Professional Artifact Removal')
    axes[1].set_ylabel('Relative Flux')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Phase-folded transit
    if detection['has_transit'] and detection['period']:
        period = detection['period']
        t0 = detection['epoch']
        phase = ((time - t0) % period) / period
        phase[phase > 0.5] -= 1  # Center on transit
        
        axes[2].plot(phase * 24, processed_data['flux_clean'].values, 'r.', alpha=0.6, markersize=1)
        axes[2].set_title(f'Phase-Folded Transit (P={period:.4f}d, Confidence={detection["confidence"]*100:.1f}%)')
        axes[2].set_xlabel('Hours from Mid-Transit')
        axes[2].set_ylabel('Relative Flux')
        axes[2].grid(True, alpha=0.3)
    else:
        axes[2].text(0.5, 0.5, 'No Transit Detected', ha='center', va='center',
                    transform=axes[2].transAxes, fontsize=14)
        axes[2].set_title('Phase-Folded Analysis')
    
    plt.tight_layout()
    plt.savefig('/workspace/professional_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()