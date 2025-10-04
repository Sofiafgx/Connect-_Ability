"""
Batch Prediction Script
Analyze multiple exoplanet candidates from a CSV file
"""

import sys
import pandas as pd
import numpy as np
from exoplanet_model import ExoplanetModel
from exoplanet_physics import ExoplanetPhysics

def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_predict.py <input_csv_file>")
        print("\nCSV file should contain columns:")
        print("  - orbital_period")
        print("  - transit_depth")
        print("  - transit_duration")
        print("  - stellar_radius")
        print("  - stellar_mass (optional, default: 1.0)")
        print("  - stellar_temp (optional, default: 5778)")
        print("  - snr (optional, default: 10.0)")
        print("  - stellar_magnitude (optional, default: 12.0)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    print("=" * 70)
    print(" " * 15 + "BATCH EXOPLANET ANALYSIS")
    print("=" * 70)
    
    # Load input data
    print(f"\nLoading data from {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)
    
    print(f"Loaded {len(df)} candidates")
    
    # Fill missing values with defaults
    if 'stellar_mass' not in df.columns:
        df['stellar_mass'] = 1.0
    else:
        df['stellar_mass'].fillna(1.0, inplace=True)
    
    if 'stellar_temp' not in df.columns:
        df['stellar_temp'] = 5778
    else:
        df['stellar_temp'].fillna(5778, inplace=True)
    
    if 'snr' not in df.columns:
        df['snr'] = 10.0
    else:
        df['snr'].fillna(10.0, inplace=True)
    
    if 'stellar_magnitude' not in df.columns:
        df['stellar_magnitude'] = 12.0
    else:
        df['stellar_magnitude'].fillna(12.0, inplace=True)
    
    # Load model
    print("\nLoading trained model...")
    try:
        model = ExoplanetModel()
        model.load_model('exoplanet_model.pkl')
    except FileNotFoundError:
        print("Error: Model file 'exoplanet_model.pkl' not found.")
        print("Please run 'python train_model.py' first.")
        sys.exit(1)
    
    # Calculate derived features
    print("\nCalculating physics-based features...")
    df = ExoplanetPhysics.enrich_features(df)
    
    # Make predictions
    print("\nAnalyzing candidates...")
    results = []
    
    for idx, row in df.iterrows():
        try:
            # Convert Series to DataFrame with single row
            row_df = pd.DataFrame([row])
            result = model.predict(row_df)
            
            results.append({
                'candidate_id': idx,
                'classification': result['classification'],
                'confidence': result['confidence'],
                'prob_confirmed': result['probabilities'].get('CONFIRMED', 0),
                'prob_candidate': result['probabilities'].get('CANDIDATE', 0),
                'prob_false_positive': result['probabilities'].get('FALSE_POSITIVE', 0),
                'impact_parameter': result.get('impact_parameter'),
                'planet_radius': result.get('planet_radius'),
                'planet_temp': result.get('planet_temp'),
                'semi_major_axis': result.get('semi_major_axis'),
                'potentially_habitable': result.get('potentially_habitable', 0)
            })
        except Exception as e:
            print(f"Error processing candidate {idx}: {e}")
            results.append({
                'candidate_id': idx,
                'classification': 'ERROR',
                'confidence': 0,
                'error': str(e)
            })
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Save results
    output_file = input_file.replace('.csv', '_predictions.csv')
    results_df.to_csv(output_file, index=False)
    
    # Summary
    print("\n" + "=" * 70)
    print(" " * 20 + "ANALYSIS COMPLETE")
    print("=" * 70)
    
    print(f"\nTotal candidates analyzed: {len(results_df)}")
    print("\nClassification Summary:")
    print(results_df['classification'].value_counts())
    
    # High-confidence detections
    confirmed = results_df[
        (results_df['classification'] == 'CONFIRMED') & 
        (results_df['confidence'] > 0.8)
    ]
    print(f"\nHigh-confidence confirmed exoplanets: {len(confirmed)}")
    
    # Potentially habitable
    if 'potentially_habitable' in results_df.columns:
        habitable = results_df[results_df['potentially_habitable'] == 1]
        print(f"Potentially habitable planets: {len(habitable)}")
    else:
        habitable = pd.DataFrame()
    
    print(f"\nResults saved to: {output_file}")
    print("=" * 70)
    
    # Display top candidates
    if len(confirmed) > 0:
        print("\nTop 5 Confirmed Exoplanet Candidates:")
        print("-" * 70)
        top_5 = confirmed.nlargest(5, 'confidence')
        for _, row in top_5.iterrows():
            print(f"\nCandidate #{int(row['candidate_id'])}")
            print(f"  Confidence: {row['confidence']*100:.2f}%")
            if not pd.isna(row['planet_radius']):
                print(f"  Radius: {row['planet_radius']:.3f} Earth radii")
            if not pd.isna(row['planet_temp']):
                print(f"  Temperature: {row['planet_temp']:.1f} K")
            if not pd.isna(row['semi_major_axis']):
                print(f"  Semi-major axis: {row['semi_major_axis']:.4f} AU")
            if row['potentially_habitable'] == 1:
                print("  ⭐ POTENTIALLY HABITABLE!")

if __name__ == "__main__":
    main()
