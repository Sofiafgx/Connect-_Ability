#!/usr/bin/env python3
"""
Quick Command-Line Exoplanet Transit Analysis
Simple script for fast lightcurve analysis
"""

import argparse
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import json

from main import ExoplanetDetectionPipeline

def load_lightcurve_data(filepath):
    """Load lightcurve data from file"""
    try:
        # Try different delimiters
        for delimiter in [',', '\t', ' ', ';']:
            try:
                data = pd.read_csv(filepath, delimiter=delimiter)
                if len(data.columns) >= 2:
                    break
            except:
                continue
        else:
            raise ValueError("Could not parse file format")
        
        # Standardize column names
        columns = data.columns.tolist()
        
        # Find time column
        time_col = columns[0]
        for col in columns:
            if any(keyword in col.lower() for keyword in ['time', 'bjd', 'mjd', 'jd', 'days']):
                time_col = col
                break
        
        # Find flux column
        flux_col = columns[1] if len(columns) > 1 else columns[0]
        for col in columns:
            if any(keyword in col.lower() for keyword in ['flux', 'mag', 'brightness']):
                flux_col = col
                break
        
        # Find error column
        err_col = None
        for col in columns:
            if any(keyword in col.lower() for keyword in ['err', 'error', 'sigma']):
                err_col = col
                break
        
        # Create standardized DataFrame
        standardized = pd.DataFrame({
            'time': data[time_col],
            'flux': data[flux_col],
            'flux_err': data[err_col] if err_col else np.full(len(data), 0.0001)
        })
        
        # Clean data
        standardized = standardized.dropna()
        standardized = standardized.sort_values('time').reset_index(drop=True)
        
        return standardized
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def print_analysis_results(results, data_stats):
    """Print formatted analysis results"""
    tr = results['transit_result']
    confidence_pct = tr['confidence'] * 100
    
    # Header
    print("\n" + "="*70)
    print("🌟 EXOPLANET TRANSIT DETECTION RESULTS")
    print("="*70)
    
    # Main result with emoji indicators
    if confidence_pct >= 90:
        status_emoji = "🎯"
        status_text = "VERY LIKELY EXOPLANET TRANSIT"
    elif confidence_pct >= 70:
        status_emoji = "🔍"
        status_text = "PROBABLE TRANSIT - Investigate Further"
    elif confidence_pct >= 50:
        status_emoji = "⚠️"
        status_text = "UNCERTAIN - Could be False Positive"
    else:
        status_emoji = "❌"
        status_text = "UNLIKELY TO BE TRANSIT"
    
    print(f"\n{status_emoji} DETECTION RESULT:")
    print(f"   Transit Detected: {'YES' if tr['has_transit'] else 'NO'}")
    print(f"   Confidence: {confidence_pct:.1f}%")
    print(f"   Status: {status_text}")
    
    # Signal characteristics
    print(f"\n📊 SIGNAL CHARACTERISTICS:")
    if tr.get('period'):
        print(f"   Orbital Period: {tr['period']:.3f} days")
    if tr.get('depth'):
        print(f"   Transit Depth: {tr['depth']:.4f} ({tr['depth']*100:.2f}%)")
    if tr.get('snr'):
        print(f"   Signal-to-Noise: {tr['snr']:.2f}σ")
    
    # Data quality
    print(f"\n📈 DATA QUALITY:")
    print(f"   Data Points: {data_stats['n_points']:,}")
    print(f"   Time Coverage: {data_stats['time_span']:.2f} days")
    print(f"   Noise Level: {data_stats['processed_rms']*1e6:.0f} ppm")
    print(f"   Outliers Removed: {data_stats['outlier_fraction']*100:.1f}%")
    
    # Recommendation
    print(f"\n💡 RECOMMENDATION:")
    if confidence_pct >= 90:
        print("   ✅ High confidence detection - recommend follow-up observations")
    elif confidence_pct >= 70:
        print("   🔍 Promising candidate - requires validation with additional data")
    elif confidence_pct >= 50:
        print("   ⚠️ Weak signal - consider improving data quality or longer observations")
    else:
        print("   ❌ No convincing transit signal - likely false positive or noise")
    
    print("\n" + "="*70)

def create_quick_plot(data, results, output_file=None):
    """Create a quick visualization of the results"""
    tr = results['transit_result']
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle(f'Exoplanet Analysis - Confidence: {tr["confidence"]*100:.1f}%', fontsize=14)
    
    time = data['time'].values
    
    # Original vs processed lightcurve
    axes[0].plot(time, data['flux'].values, 'k.', alpha=0.3, markersize=1, label='Original')
    axes[0].plot(time, data['flux_stellar_corrected'].values, 'r-', alpha=0.7, linewidth=1, label='Processed')
    axes[0].set_title('Lightcurve: Original vs Processed')
    axes[0].set_ylabel('Relative Flux')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Phase-folded data if transit detected
    if tr['has_transit'] and tr.get('period'):
        period = tr['period']
        phase = ((time % period) / period - 0.5) * 24  # Hours from mid-transit
        
        axes[1].plot(phase, data['flux_stellar_corrected'].values, 'b.', alpha=0.5, markersize=2)
        axes[1].set_title(f'Phase-Folded Transit (P={period:.3f}d)')
        axes[1].set_xlabel('Hours from Mid-Transit')
        axes[1].set_ylabel('Relative Flux')
        axes[1].grid(True, alpha=0.3)
        
        # Highlight transit
        in_transit = np.abs(phase) < 2
        if np.any(in_transit):
            axes[1].plot(phase[in_transit], data['flux_stellar_corrected'].values[in_transit], 
                        'r.', markersize=3, alpha=0.8, label='In Transit')
            axes[1].legend()
    else:
        axes[1].text(0.5, 0.5, 'No Transit Detected', ha='center', va='center', 
                    transform=axes[1].transAxes, fontsize=12)
        axes[1].set_title('Phase-Folded Data (No Transit)')
        axes[1].set_xlabel('Time (days)')
        axes[1].set_ylabel('Relative Flux')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"📊 Plot saved to: {output_file}")
    else:
        plt.show()
    
    plt.close()

def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(
        description="🌟 Quick Exoplanet Transit Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quick_analyze.py data.csv
  python quick_analyze.py lightcurve.txt --plot results.png
  python quick_analyze.py data.csv --json results.json --no-plot
  
Supported file formats:
  • CSV with time,flux columns
  • Space/tab separated values
  • Optional flux error column
        """
    )
    
    parser.add_argument('input_file', help='Input lightcurve data file')
    parser.add_argument('--plot', '-p', help='Save plot to file (optional)')
    parser.add_argument('--json', '-j', help='Save results to JSON file (optional)')
    parser.add_argument('--no-plot', action='store_true', help='Skip plotting')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input_file).exists():
        print(f"❌ Error: File '{args.input_file}' not found")
        sys.exit(1)
    
    if not args.quiet:
        print("🌟 Exoplanet Transit Detector - Quick Analysis")
        print("=" * 50)
        print(f"📁 Input file: {args.input_file}")
        print("🤖 Initializing AI system...")
    
    # Initialize pipeline
    try:
        pipeline = ExoplanetDetectionPipeline()
        pipeline.train_system(n_training_samples=50)  # Faster training for quick analysis
        
        if not args.quiet:
            print("✅ AI system ready!")
            print("📊 Loading and analyzing data...")
        
        # Load data
        data = load_lightcurve_data(args.input_file)
        if data is None:
            sys.exit(1)
        
        # Validate data
        if len(data) < 50:
            print("⚠️ Warning: Less than 50 data points. Results may be unreliable.")
        
        # Run analysis
        processed_data = pipeline.artifact_detector.remove_instrumental_artifacts(data)
        processed_data = pipeline.artifact_detector.detect_stellar_variability(processed_data)
        transit_result = pipeline.transit_detector.detect_transits(processed_data)
        
        # Calculate statistics
        data_stats = {
            'n_points': len(data),
            'time_span': data['time'].max() - data['time'].min(),
            'cadence': np.median(np.diff(data['time'])),
            'original_rms': data['flux'].std(),
            'processed_rms': processed_data['flux_stellar_corrected'].std(),
            'noise_reduction': 1 - (processed_data['flux_stellar_corrected'].std() / data['flux'].std()),
            'outlier_fraction': 1 - np.mean(processed_data['outlier_mask']),
            'stellar_period': processed_data.get('stellar_period', [None])[0] if 'stellar_period' in processed_data.columns else None
        }
        
        results = {
            'transit_result': transit_result,
            'data_stats': data_stats,
            'input_file': args.input_file,
            'analysis_timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Print results
        if not args.quiet:
            print_analysis_results(results, data_stats)
        else:
            # Minimal output for quiet mode
            confidence = transit_result['confidence'] * 100
            detected = "YES" if transit_result['has_transit'] else "NO"
            print(f"Transit: {detected}, Confidence: {confidence:.1f}%")
        
        # Save JSON results if requested
        if args.json:
            with open(args.json, 'w') as f:
                # Convert numpy types to native Python types for JSON serialization
                json_results = {}
                for key, value in results.items():
                    if isinstance(value, dict):
                        json_results[key] = {k: float(v) if isinstance(v, (np.float32, np.float64)) 
                                           else int(v) if isinstance(v, (np.int32, np.int64))
                                           else bool(v) if isinstance(v, np.bool_)
                                           else v for k, v in value.items()}
                    else:
                        json_results[key] = value
                
                json.dump(json_results, f, indent=2, default=str)
            
            if not args.quiet:
                print(f"💾 Results saved to: {args.json}")
        
        # Create plot if requested
        if not args.no_plot:
            processed_data['flux_stellar_corrected'] = processed_data['flux_stellar_corrected']
            create_quick_plot(processed_data, results, args.plot)
        
        if not args.quiet:
            print("✅ Analysis complete!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()