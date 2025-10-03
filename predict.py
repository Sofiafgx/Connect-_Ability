"""
CLI interface for exoplanet prediction
Allows users to input transit parameters and get classification
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import argparse
import numpy as np
from model import ExoplanetClassifier
import warnings
warnings.filterwarnings('ignore')


def get_user_input_interactive():
    """
    Get transit parameters from user interactively
    """
    print("\n" + "="*80)
    print(" EXOPLANET DETECTION - INTERACTIVE PREDICTION")
    print("="*80)
    print("\nEnter transit parameters (press Enter to skip optional fields):\n")
    
    features = {}
    
    # Define expected features with descriptions
    feature_prompts = {
        'orbital_period': 'Orbital Period (days)',
        'transit_duration': 'Transit Duration (hours)',
        'transit_depth': 'Transit Depth (ppm)',
        'planet_radius': 'Planet Radius (Earth radii)',
        'semi_major_axis': 'Semi-major Axis (AU)',
        'eq_temperature': 'Equilibrium Temperature (K)',
        'impact_parameter': 'Impact Parameter',
        'stellar_temp': 'Stellar Temperature (K)',
        'stellar_radius': 'Stellar Radius (Solar radii)',
        'stellar_mass': 'Stellar Mass (Solar masses)',
        'stellar_magnitude': 'Stellar Magnitude',
        'snr': 'Signal-to-Noise Ratio'
    }
    
    for key, prompt in feature_prompts.items():
        while True:
            try:
                value = input(f"{prompt}: ").strip()
                if value == '':
                    features[key] = 0  # Use 0 for missing values
                    break
                features[key] = float(value)
                break
            except ValueError:
                print("  Invalid input. Please enter a number.")
    
    return features


def predict_from_dict(features_dict):
    """
    Make prediction from feature dictionary
    """
    # Load model
    classifier = ExoplanetClassifier(input_dim=1)  # Will be updated when loading
    classifier.load_model()
    
    # Make prediction
    prediction, probabilities = classifier.predict_single(features_dict)
    
    return prediction, probabilities


def main():
    parser = argparse.ArgumentParser(
        description='Exoplanet Detection CLI - Predict from transit parameters'
    )
    parser.add_argument('--orbital_period', type=float, help='Orbital period in days')
    parser.add_argument('--transit_duration', type=float, help='Transit duration in hours')
    parser.add_argument('--transit_depth', type=float, help='Transit depth in ppm')
    parser.add_argument('--planet_radius', type=float, help='Planet radius in Earth radii')
    parser.add_argument('--semi_major_axis', type=float, help='Semi-major axis in AU')
    parser.add_argument('--eq_temperature', type=float, help='Equilibrium temperature in K')
    parser.add_argument('--impact_parameter', type=float, help='Impact parameter')
    parser.add_argument('--stellar_temp', type=float, help='Stellar temperature in K')
    parser.add_argument('--stellar_radius', type=float, help='Stellar radius in solar radii')
    parser.add_argument('--stellar_mass', type=float, help='Stellar mass in solar masses')
    parser.add_argument('--stellar_magnitude', type=float, help='Stellar magnitude')
    parser.add_argument('--snr', type=float, help='Signal-to-noise ratio')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Interactive mode - prompt for each parameter')
    
    args = parser.parse_args()
    
    # Check if model exists
    if not os.path.exists('models/exoplanet_classifier.h5'):
        print("\nError: Model not found!")
        print("Please train the model first by running: python train.py")
        return
    
    # Get features
    if args.interactive or not any(vars(args).values()):
        features = get_user_input_interactive()
    else:
        features = {
            'orbital_period': args.orbital_period or 0,
            'transit_duration': args.transit_duration or 0,
            'transit_depth': args.transit_depth or 0,
            'planet_radius': args.planet_radius or 0,
            'semi_major_axis': args.semi_major_axis or 0,
            'eq_temperature': args.eq_temperature or 0,
            'impact_parameter': args.impact_parameter or 0,
            'stellar_temp': args.stellar_temp or 0,
            'stellar_radius': args.stellar_radius or 0,
            'stellar_mass': args.stellar_mass or 0,
            'stellar_magnitude': args.stellar_magnitude or 0,
            'snr': args.snr or 0
        }
    
    # Make prediction
    print("\nMaking prediction...")
    prediction, probabilities = predict_from_dict(features)
    
    # Display results
    print("\n" + "="*80)
    print(" PREDICTION RESULTS")
    print("="*80)
    print(f"\nClassification: {prediction}")
    print(f"\nConfidence Scores:")
    print(f"  False Positive:      {probabilities['false_positive']:.2%}")
    print(f"  Planetary Candidate: {probabilities['candidate']:.2%}")
    print(f"  Confirmed Exoplanet: {probabilities['confirmed']:.2%}")
    print("\n" + "="*80)
    
    # Interpretation
    if prediction == "Confirmed Exoplanet":
        print("\n✓ High confidence detection! This transit signal has characteristics")
        print("  consistent with a confirmed exoplanet.")
    elif prediction == "Planetary Candidate":
        print("\n⚠ Potential exoplanet candidate. Further observations recommended")
        print("  to rule out false positive scenarios.")
    else:
        print("\n✗ Likely a false positive. The signal characteristics suggest")
        print("  this is not a genuine planetary transit.")
    

if __name__ == "__main__":
    main()
