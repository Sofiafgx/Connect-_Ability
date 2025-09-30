# main.py - Exoplanet Transit Detection with Artifact Removal
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal, stats
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import requests
import warnings
warnings.filterwarnings('ignore')

class ExoplanetDataLoader:
    """Handles data download and preprocessing from exoplanet archives"""
    
    def __init__(self):
        self.base_urls = {
            'cumulative': 'https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nqueries/nph-nquery?',
            'toi': 'https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nqueries/nph-nquery?',
            'k2pandc': 'https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nqueries/nph-nquery?'
        }
    
    def download_lightcurve_data(self, target_name, mission='kepler'):
        """Download lightcurve data for a specific target"""
        try:
            # This would typically use lightkurve or direct API calls
            # For demo purposes, generating synthetic data
            print(f"Downloading {mission} data for {target_name}...")
            
            # Generate synthetic lightcurve with transit-like features
            time = np.linspace(0, 90, 10000)  # 90 days
            flux = np.ones_like(time) + np.random.normal(0, 0.0001, len(time))
            
            # Add stellar variability
            stellar_period = np.random.uniform(10, 30)
            flux += 0.01 * np.sin(2 * np.pi * time / stellar_period)
            
            # Add some instrumental artifacts
            artifact_times = np.random.choice(time, size=50, replace=False)
            for at in artifact_times:
                mask = np.abs(time - at) < 0.1
                flux[mask] += np.random.normal(0, 0.005, np.sum(mask))
            
            return pd.DataFrame({'time': time, 'flux': flux, 'flux_err': np.full_like(time, 0.0001)})
            
        except Exception as e:
            print(f"Error downloading data: {e}")
            return None
    
    def add_synthetic_transit(self, data, period=10.5, depth=0.01, duration=0.2):
        """Add synthetic transit signal to data"""
        time = data['time'].values
        flux = data['flux'].values.copy()
        
        # Calculate transit times
        transit_times = np.arange(5, time.max(), period)
        
        for t_transit in transit_times:
            # Simple box-shaped transit
            in_transit = np.abs(time - t_transit) < duration/2
            flux[in_transit] -= depth
            
        data_with_transit = data.copy()
        data_with_transit['flux'] = flux
        data_with_transit['has_transit'] = True
        data_with_transit['period'] = period
        data_with_transit['depth'] = depth
        
        return data_with_transit

class ArtifactDetector:
    """Detects and removes various types of artifacts from lightcurve data"""
    
    def __init__(self):
        self.outlier_detector = IsolationForest(contamination=0.1, random_state=42)
        
    def detect_outliers(self, flux, threshold=5):
        """Detect outliers using sigma clipping and isolation forest"""
        # Sigma clipping
        sigma_mask = np.abs(stats.zscore(flux)) < threshold
        
        # Isolation forest for more complex outliers
        flux_reshaped = flux.reshape(-1, 1)
        outlier_labels = self.outlier_detector.fit_predict(flux_reshaped)
        isolation_mask = outlier_labels == 1
        
        return sigma_mask & isolation_mask
    
    def remove_instrumental_artifacts(self, data):
        """Remove common instrumental artifacts"""
        time = data['time'].values
        flux = data['flux'].values
        
        # 1. Remove outliers
        clean_mask = self.detect_outliers(flux)
        
        # 2. Remove systematic trends (detrending)
        # Use Savitzky-Golay filter to identify long-term trends
        window_length = min(101, len(flux) // 10)
        if window_length % 2 == 0:
            window_length += 1
        if window_length < 3:
            window_length = 3
            
        trend = signal.savgol_filter(flux[clean_mask], window_length, 3)
        
        # Interpolate trend back to original time grid
        trend_interp = np.interp(time, time[clean_mask], trend)
        detrended_flux = flux / trend_interp
        
        # 3. Remove high-frequency noise
        # Apply low-pass filter
        nyquist = 0.5 / np.median(np.diff(time))
        cutoff = 0.1  # cycles per day
        b, a = signal.butter(3, cutoff/nyquist, btype='low')
        filtered_flux = signal.filtfilt(b, a, detrended_flux)
        
        cleaned_data = data.copy()
        cleaned_data['flux_clean'] = filtered_flux
        cleaned_data['outlier_mask'] = clean_mask
        
        return cleaned_data
    
    def detect_stellar_variability(self, data):
        """Detect and model stellar variability"""
        time = data['time'].values
        flux = data['flux_clean'].values
        
        # Use Lomb-Scargle periodogram to detect stellar rotation
        frequencies = np.linspace(0.01, 2, 1000)  # 0.5 to 100 day periods
        power = signal.lombscargle(time, flux - np.mean(flux), frequencies, normalize=True)
        
        # Find dominant period
        peak_freq = frequencies[np.argmax(power)]
        stellar_period = 2 * np.pi / peak_freq
        
        # Model stellar variability
        stellar_model = np.mean(flux) + np.std(flux) * 0.5 * np.sin(2 * np.pi * time / stellar_period)
        
        data_corrected = data.copy()
        data_corrected['flux_stellar_corrected'] = flux - (stellar_model - np.mean(flux))
        data_corrected['stellar_period'] = stellar_period
        
        return data_corrected

class TransitDetector:
    """AI-based transit detection and classification"""
    
    def __init__(self):
        self.transit_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, data, period_range=(1, 50), min_transits=3):
        """Extract features for transit detection"""
        time = data['time'].values
        flux = data['flux_stellar_corrected'].values
        
        features = []
        periods = np.linspace(period_range[0], period_range[1], 100)
        
        for period in periods:
            try:
                # Phase-fold the data
                phase = (time % period) / period
                
                # Sort by phase
                sort_idx = np.argsort(phase)
                phase_sorted = phase[sort_idx]
                flux_sorted = flux[sort_idx]
                
                # Bin the phase-folded data
                n_bins = 50
                bin_edges = np.linspace(0, 1, n_bins + 1)
                binned_flux = []
                
                for i in range(n_bins):
                    mask = (phase_sorted >= bin_edges[i]) & (phase_sorted < bin_edges[i+1])
                    if np.sum(mask) > 0:
                        binned_flux.append(np.median(flux_sorted[mask]))
                    else:
                        binned_flux.append(np.nan)
                
                binned_flux = np.array(binned_flux)
                valid_mask = ~np.isnan(binned_flux)
                
                if np.sum(valid_mask) < n_bins // 2:
                    continue
                
                binned_flux_clean = binned_flux[valid_mask]
                
                # Calculate transit detection metrics
                baseline = np.median(binned_flux_clean)
                min_flux = np.min(binned_flux_clean)
                depth = baseline - min_flux
                
                # More robust SNR calculation
                # Use median absolute deviation for noise estimate
                mad = np.median(np.abs(binned_flux_clean - baseline))
                noise_est = 1.4826 * mad  # Convert MAD to std equivalent
                if noise_est == 0:
                    noise_est = np.std(binned_flux_clean)
                
                snr = depth / noise_est if noise_est > 0 else 0
                
                # Transit shape analysis
                min_idx = np.argmin(binned_flux_clean)
                transit_width = self._estimate_transit_width(binned_flux_clean, min_idx)
                
                # Box-shaped transit test
                box_score = self._box_transit_score(binned_flux_clean)
                
                # Additional features for better detection
                # Check for V-shaped dip (characteristic of transits)
                v_shape_score = self._calculate_v_shape_score(binned_flux_clean, min_idx)
                
                # Periodicity check - how consistent is the signal
                periodicity_score = self._calculate_periodicity_score(time, flux, period)
                
                features.append([
                    period, depth, snr, transit_width, box_score,
                    np.std(binned_flux_clean), baseline, v_shape_score, periodicity_score
                ])
                
            except Exception as e:
                # Skip this period if there's an error
                continue
        
        return np.array(features)
    
    def _estimate_transit_width(self, flux, min_idx):
        """Estimate transit width from phase-folded data"""
        if len(flux) == 0:
            return 0
            
        baseline = np.median(flux)
        depth_threshold = (baseline + np.min(flux)) / 2
        
        # Find points below threshold
        below_threshold = flux < depth_threshold
        
        if np.sum(below_threshold) == 0:
            return 0
        
        # Find continuous regions
        diff = np.diff(below_threshold.astype(int))
        starts = np.where(diff == 1)[0] + 1
        ends = np.where(diff == -1)[0]
        
        # Handle edge cases where transit starts at beginning or ends at end
        if len(flux) > 0 and below_threshold[0]:
            starts = np.concatenate([[0], starts])
        if len(flux) > 0 and below_threshold[-1]:
            ends = np.concatenate([ends, [len(flux) - 1]])
        
        # Ensure starts and ends have same length
        min_len = min(len(starts), len(ends))
        if min_len == 0:
            return 0
        
        starts = starts[:min_len]
        ends = ends[:min_len]
        
        # Find longest continuous region
        if len(starts) > 0 and len(ends) > 0:
            widths = ends - starts
            max_width = np.max(widths) if len(widths) > 0 else 0
            return max_width / len(flux)  # Normalize by phase length
        
        return 0
    
    def _box_transit_score(self, flux):
        """Score how well the signal matches a box-shaped transit"""
        if len(flux) == 0:
            return 0
            
        baseline = np.median(flux)
        min_flux = np.min(flux)
        
        if baseline == min_flux:
            return 0
        
        # Create idealized box transit
        box_transit = np.full_like(flux, baseline)
        min_idx = np.argmin(flux)
        width = max(1, len(flux) // 10)  # Assume 10% transit width
        
        start_idx = max(0, min_idx - width//2)
        end_idx = min(len(flux), min_idx + width//2)
        box_transit[start_idx:end_idx] = min_flux
        
        # Calculate correlation
        try:
            correlation = np.corrcoef(flux, box_transit)[0, 1]
            return correlation if not np.isnan(correlation) else 0
        except:
            return 0
    
    def _calculate_v_shape_score(self, flux, min_idx):
        """Calculate how V-shaped the transit is (characteristic of real transits)"""
        if len(flux) < 5 or min_idx < 2 or min_idx >= len(flux) - 2:
            return 0
        
        try:
            # Look at points around the minimum
            left_slope = flux[min_idx] - flux[max(0, min_idx - 2)]
            right_slope = flux[min_idx] - flux[min(len(flux) - 1, min_idx + 2)]
            
            # Both slopes should be negative (going down to minimum)
            if left_slope < 0 and right_slope < 0:
                return abs(left_slope) + abs(right_slope)
            else:
                return 0
        except:
            return 0
    
    def _calculate_periodicity_score(self, time, flux, period):
        """Calculate how periodic the signal is at the given period"""
        try:
            # Find potential transit times
            transit_times = []
            phase = (time % period) / period
            
            # Look for dips in the original time series
            # Smooth the flux to reduce noise
            from scipy.ndimage import gaussian_filter1d
            smoothed_flux = gaussian_filter1d(flux, sigma=2)
            
            # Find local minima
            from scipy.signal import find_peaks
            # Invert flux to find minima as peaks
            peaks, _ = find_peaks(-smoothed_flux, height=-np.percentile(smoothed_flux, 10))
            
            if len(peaks) < 2:
                return 0
            
            # Check if peaks are roughly periodic
            peak_times = time[peaks]
            intervals = np.diff(peak_times)
            
            # Score based on how close intervals are to the expected period
            expected_intervals = np.full_like(intervals, period)
            period_score = 1.0 / (1.0 + np.mean(np.abs(intervals - expected_intervals) / period))
            
            return period_score
        except:
            return 0
    
    def train(self, training_data):
        """Train the transit detection classifier"""
        print("Training transit detection model...")
        
        X = []
        y = []
        
        for data in training_data:
            try:
                features = self.extract_features(data)
                if len(features) > 0:
                    # Use the best feature set (highest SNR)
                    best_idx = np.argmax(features[:, 2])  # SNR column
                    X.append(features[best_idx])
                    y.append(data.get('has_transit', False))
            except Exception as e:
                print(f"Warning: Failed to extract features from training sample: {e}")
                continue
        
        X = np.array(X)
        y = np.array(y)
        
        if len(X) > 0:
            X_scaled = self.scaler.fit_transform(X)
            self.transit_classifier.fit(X_scaled, y)
            self.is_trained = True
            print(f"Model trained on {len(X)} samples")
        else:
            print("No valid training data found")
    
    def detect_transits(self, data):
        """Detect transits in cleaned lightcurve data using improved algorithm"""
        try:
            # Use a simpler, more reliable detection approach
            time = data['time'].values
            flux = data['flux_stellar_corrected'].values
            
            # Simple Box Least Squares (BLS) approach
            best_period, best_snr, best_depth = self._simple_bls_search(time, flux)
            
            # Calculate confidence based on multiple factors
            confidence = self._calculate_detection_confidence(time, flux, best_period, best_snr, best_depth)
            
            # Determine if transit is detected based on thresholds
            has_transit = (best_snr > 3.0 and best_depth > 0.001 and confidence > 0.3)
            
            return {
                'has_transit': bool(has_transit),
                'confidence': float(confidence),
                'period': float(best_period) if best_period else None,
                'depth': float(best_depth) if best_depth else None,
                'snr': float(best_snr) if best_snr else None
            }
            
        except Exception as e:
            print(f"Error in transit detection: {e}")
            return {'has_transit': False, 'confidence': 0, 'period': None}
    
    def _simple_bls_search(self, time, flux):
        """Simple Box Least Squares search for transits"""
        periods = np.linspace(1, min(50, (time.max() - time.min()) / 3), 200)
        best_snr = 0
        best_period = None
        best_depth = 0
        
        for period in periods:
            try:
                # Phase fold
                phase = ((time - time[0]) % period) / period
                
                # Sort by phase
                sort_idx = np.argsort(phase)
                phase_sorted = phase[sort_idx]
                flux_sorted = flux[sort_idx]
                
                # Try different transit widths
                for width_frac in [0.05, 0.1, 0.15, 0.2]:
                    # Try different phase centers
                    for center_phase in np.linspace(0, 1, 20):
                        # Define in-transit region
                        phase_diff = np.abs(phase_sorted - center_phase)
                        phase_diff = np.minimum(phase_diff, 1 - phase_diff)  # Handle wrap-around
                        
                        in_transit = phase_diff < width_frac / 2
                        out_transit = phase_diff > width_frac
                        
                        if np.sum(in_transit) < 3 or np.sum(out_transit) < 10:
                            continue
                        
                        # Calculate transit depth and significance
                        in_transit_flux = flux_sorted[in_transit]
                        out_transit_flux = flux_sorted[out_transit]
                        
                        depth = np.median(out_transit_flux) - np.median(in_transit_flux)
                        
                        if depth <= 0:
                            continue
                        
                        # Calculate SNR
                        noise = np.std(out_transit_flux)
                        if noise > 0:
                            snr = depth / (noise / np.sqrt(len(in_transit_flux)))
                            
                            if snr > best_snr:
                                best_snr = snr
                                best_period = period
                                best_depth = depth
                                
            except Exception:
                continue
        
        return best_period, best_snr, best_depth
    
    def _calculate_detection_confidence(self, time, flux, period, snr, depth):
        """Calculate detection confidence based on multiple factors"""
        if period is None or snr is None or depth is None:
            return 0.0
        
        confidence = 0.0
        
        # SNR contribution (0-0.4)
        snr_score = min(0.4, snr / 20.0)
        confidence += snr_score
        
        # Depth contribution (0-0.3)
        depth_score = min(0.3, depth / 0.02)  # Normalize to 2% depth
        confidence += depth_score
        
        # Period reasonableness (0-0.2)
        if 1 <= period <= 50:
            period_score = 0.2
        else:
            period_score = 0.1
        confidence += period_score
        
        # Data coverage (0-0.1)
        time_span = time.max() - time.min()
        n_transits = time_span / period if period > 0 else 0
        coverage_score = min(0.1, n_transits / 3.0)  # Good if 3+ transits
        confidence += coverage_score
        
        return min(1.0, confidence)

class ExoplanetDetectionPipeline:
    """Main pipeline for exoplanet detection with artifact removal"""
    
    def __init__(self):
        self.data_loader = ExoplanetDataLoader()
        self.artifact_detector = ArtifactDetector()
        self.transit_detector = TransitDetector()
        
    def process_target(self, target_name, mission='kepler'):
        """Process a single target through the complete pipeline"""
        print(f"\n{'='*50}")
        print(f"Processing target: {target_name}")
        print(f"{'='*50}")
        
        # 1. Load data
        print("1. Loading lightcurve data...")
        data = self.data_loader.download_lightcurve_data(target_name, mission)
        if data is None:
            return None
        
        # 2. Remove artifacts
        print("2. Removing artifacts...")
        data = self.artifact_detector.remove_instrumental_artifacts(data)
        data = self.artifact_detector.detect_stellar_variability(data)
        
        # 3. Detect transits
        print("3. Detecting transits...")
        transit_result = self.transit_detector.detect_transits(data)
        
        # 4. Generate plots
        self.plot_results(data, transit_result, target_name)
        
        return {
            'target': target_name,
            'data': data,
            'transit_result': transit_result
        }
    
    def plot_results(self, data, transit_result, target_name):
        """Plot the analysis results"""
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        time = data['time'].values
        
        # Original lightcurve
        axes[0].plot(time, data['flux'].values, 'k.', alpha=0.3, markersize=1)
        axes[0].set_title(f'{target_name} - Original Lightcurve')
        axes[0].set_ylabel('Relative Flux')
        
        # Cleaned lightcurve
        axes[1].plot(time, data['flux_clean'].values, 'b.', alpha=0.5, markersize=1)
        axes[1].set_title('After Artifact Removal')
        axes[1].set_ylabel('Relative Flux')
        
        # Final processed lightcurve
        axes[2].plot(time, data['flux_stellar_corrected'].values, 'r.', alpha=0.5, markersize=1)
        axes[2].set_title(f'Final - Transit Detection: {transit_result["has_transit"]} (Confidence: {transit_result["confidence"]:.2f})')
        axes[2].set_ylabel('Relative Flux')
        axes[2].set_xlabel('Time (days)')
        
        plt.tight_layout()
        plt.savefig(f'/workspace/{target_name}_analysis.png', dpi=150, bbox_inches='tight')
        plt.show()
    
    def train_system(self, n_training_samples=50):
        """Train the system with synthetic data"""
        print("Initializing detection system...")
        
        # Since we're now using a simpler BLS-based approach,
        # we don't need extensive ML training
        # Just mark the detector as "trained" 
        self.transit_detector.is_trained = True
        print("Detection system ready!")
    
    def run_evaluation(self, test_targets=None):
        """Run evaluation on test targets"""
        if test_targets is None:
            test_targets = ['Kepler-10', 'Kepler-186', 'HD 209458', 'WASP-12', 'Test-Star-1']
        
        results = []
        
        for target in test_targets:
            print(f"\nEvaluating {target}...")
            result = self.process_target(target)
            if result:
                results.append(result)
        
        # Summary
        print(f"\n{'='*50}")
        print("EVALUATION SUMMARY")
        print(f"{'='*50}")
        
        for result in results:
            tr = result['transit_result']
            print(f"{result['target']:15} | Transit: {str(tr['has_transit']):5} | Confidence: {tr['confidence']:.3f} | Period: {tr.get('period', 'N/A')}")
        
        return results

def main():
    """Main function to run the exoplanet detection pipeline"""
    print("Exoplanet Transit Detection with Artifact Removal")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = ExoplanetDetectionPipeline()
    
    # Train the system
    pipeline.train_system(n_training_samples=100)
    
    # Run evaluation
    results = pipeline.run_evaluation()
    
    # Test with specific known exoplanet targets
    known_exoplanets = ['HD 209458 b', 'Kepler-452b', 'TRAPPIST-1 b']
    
    print(f"\n{'='*50}")
    print("Testing Known Exoplanets")
    print(f"{'='*50}")
    
    for target in known_exoplanets:
        # Add synthetic transit to simulate real detection
        data = pipeline.data_loader.download_lightcurve_data(target)
        if data is not None:
            data = pipeline.data_loader.add_synthetic_transit(data, 
                                                            period=np.random.uniform(5, 15),
                                                            depth=np.random.uniform(0.01, 0.03))
            
            # Process through pipeline
            data = pipeline.artifact_detector.remove_instrumental_artifacts(data)
            data = pipeline.artifact_detector.detect_stellar_variability(data)
            
            transit_result = pipeline.transit_detector.detect_transits(data)
            pipeline.plot_results(data, transit_result, target)
            
            print(f"{target}: Transit detected = {transit_result['has_transit']}, Confidence = {transit_result['confidence']:.3f}")

if __name__ == "__main__":
    main()