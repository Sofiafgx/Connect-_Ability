"""
Exoplanet Detection CLI
Interactive command-line interface for exoplanet predictions
"""

import sys
import numpy as np
import pandas as pd
from exoplanet_model import ExoplanetModel
from exoplanet_physics import ExoplanetPhysics

def print_banner():
    print("\n" + "=" * 70)
    print(" " * 15 + "EXOPLANET DETECTION & ANALYSIS")
    print(" " * 20 + "NASA ML Model v1.0")
    print("=" * 70 + "\n")

def print_result(result):
    """Pretty print prediction results"""
    print("\n" + "=" * 70)
    print(" " * 25 + "ANALYSIS RESULTS")
    print("=" * 70)
    
    # Classification
    classification = result['classification']
    confidence = result['confidence'] * 100
    
    print(f"\n📊 CLASSIFICATION: {classification}")
    print(f"🎯 CONFIDENCE: {confidence:.2f}%")
    
    print("\n📈 Probability Breakdown:")
    for class_name, prob in result['probabilities'].items():
        bar_length = int(prob * 40)
        bar = "█" * bar_length + "░" * (40 - bar_length)
        print(f"   {class_name:20s} [{bar}] {prob*100:.2f}%")
    
    # Exoplanet properties
    if classification in ['CONFIRMED', 'CANDIDATE']:
        print("\n" + "-" * 70)
        print(" " * 22 + "EXOPLANET PROPERTIES")
        print("-" * 70)
        
        if result.get('impact_parameter') is not None and not np.isnan(result['impact_parameter']):
            print(f"\n🌍 Impact Parameter: {result['impact_parameter']:.4f}")
            print(f"   (Distance from star center at mid-transit, in stellar radii)")
        
        if result.get('planet_radius') is not None and not np.isnan(result['planet_radius']):
            print(f"\n🪐 Planet Radius: {result['planet_radius']:.3f} Earth radii")
            
            # Context
            if result['planet_radius'] < 1.25:
                size_class = "Earth-like (Rocky)"
            elif result['planet_radius'] < 2.0:
                size_class = "Super-Earth"
            elif result['planet_radius'] < 6.0:
                size_class = "Neptune-like"
            else:
                size_class = "Jupiter-like (Gas Giant)"
            print(f"   Classification: {size_class}")
        
        if result.get('planet_temp') is not None and not np.isnan(result['planet_temp']):
            temp = result['planet_temp']
            print(f"\n🌡️  Equilibrium Temperature: {temp:.1f} K ({temp - 273.15:.1f} °C)")
            
            # Context
            if temp < 200:
                temp_class = "Frozen world"
            elif temp < 350:
                temp_class = "Potentially habitable zone"
            elif temp < 600:
                temp_class = "Hot world"
            else:
                temp_class = "Extremely hot world"
            print(f"   Classification: {temp_class}")
        
        if result.get('semi_major_axis') is not None and not np.isnan(result['semi_major_axis']):
            sma = result['semi_major_axis']
            print(f"\n🔭 Semi-Major Axis: {sma:.4f} AU")
            print(f"   (1 AU = Earth-Sun distance)")
            
            # Compare to Solar System
            if sma < 0.39:
                comparison = "Closer than Mercury"
            elif sma < 0.72:
                comparison = "Between Mercury and Venus"
            elif sma < 1.0:
                comparison = "Between Venus and Earth"
            elif sma < 1.52:
                comparison = "Between Earth and Mars"
            elif sma < 5.2:
                comparison = "In inner Solar System"
            else:
                comparison = "Beyond Jupiter's orbit"
            print(f"   Solar System comparison: {comparison}")
        
        # Habitability
        if result.get('potentially_habitable') == 1:
            print("\n🌱 POTENTIALLY IN HABITABLE ZONE!")
            print("   This planet may have conditions suitable for liquid water")
    
    elif classification == 'FALSE_POSITIVE':
        print("\n⚠️  This signal is likely a FALSE POSITIVE")
        print("   Possible causes: stellar activity, instrumental artifacts,")
        print("   eclipsing binary stars, or other astrophysical phenomena")
    
    print("\n" + "=" * 70 + "\n")

def get_user_input():
    """Get exoplanet parameters from user"""
    print("Enter the following parameters for your exoplanet candidate:")
    print("(Press Enter to use default values for optional parameters)\n")
    
    inputs = {}
    
    # Required parameters
    try:
        inputs['orbital_period'] = float(input("Orbital Period (days): "))
        inputs['transit_depth'] = float(input("Transit Depth (ppm or %): "))
        inputs['transit_duration'] = float(input("Transit Duration (hours): "))
        inputs['stellar_radius'] = float(input("Stellar Radius (solar radii): "))
        
        # Optional parameters with defaults
        stellar_mass_input = input("Stellar Mass (solar masses) [default: 1.0]: ")
        inputs['stellar_mass'] = float(stellar_mass_input) if stellar_mass_input else 1.0
        
        stellar_temp_input = input("Stellar Temperature (K) [default: 5778]: ")
        inputs['stellar_temp'] = float(stellar_temp_input) if stellar_temp_input else 5778
        
        snr_input = input("Signal-to-Noise Ratio [default: 10.0]: ")
        inputs['snr'] = float(snr_input) if snr_input else 10.0
        
        stellar_mag_input = input("Stellar Magnitude [default: 12.0]: ")
        inputs['stellar_magnitude'] = float(stellar_mag_input) if stellar_mag_input else 12.0
        
        return inputs
        
    except ValueError:
        print("\n❌ Invalid input. Please enter numeric values.")
        return None

def calculate_derived_features(inputs):
    """Calculate derived features from input parameters"""
    df = pd.DataFrame([inputs])
    
    # Calculate impact parameter
    df['impact_parameter'] = ExoplanetPhysics.calculate_impact_parameter(
        inputs['transit_duration'],
        inputs['orbital_period'],
        inputs['stellar_radius'],
        inputs['transit_depth']
    )
    
    # Calculate semi-major axis
    df['semi_major_axis'] = ExoplanetPhysics.calculate_semi_major_axis(
        inputs['orbital_period'],
        inputs['stellar_mass']
    )
    
    # Calculate planet radius
    df['planet_radius'] = ExoplanetPhysics.calculate_planet_radius(
        inputs['transit_depth'],
        inputs['stellar_radius']
    )
    
    # Calculate equilibrium temperature
    df['planet_temp'] = ExoplanetPhysics.calculate_equilibrium_temperature(
        inputs['stellar_temp'],
        inputs['stellar_radius'],
        df['semi_major_axis'].values[0]
    )
    
    # Calculate insolation flux
    df['insolation_flux'] = ExoplanetPhysics.calculate_insolation_flux(
        inputs['stellar_temp'],
        inputs['stellar_radius'],
        df['semi_major_axis'].values[0]
    )
    
    # Calculate transit probability
    df['transit_probability'] = ExoplanetPhysics.calculate_transit_probability(
        df['semi_major_axis'].values[0],
        inputs['stellar_radius'],
        df['planet_radius'].values[0]
    )
    
    # Calculate SNR metric
    df['snr_metric'] = ExoplanetPhysics.calculate_transit_snr_metric(
        inputs['transit_depth'],
        inputs['snr'],
        inputs['transit_duration'],
        inputs['orbital_period']
    )
    
    # Check habitability
    df['potentially_habitable'] = ExoplanetPhysics.is_potentially_habitable(
        df['planet_temp'].values[0],
        df['planet_radius'].values[0]
    )
    
    # Additional features
    df['log_orbital_period'] = np.log10(df['orbital_period'].clip(lower=0.001))
    df['log_transit_depth'] = np.log10(df['transit_depth'].clip(lower=0.001))
    df['stellar_density'] = df['stellar_mass'] / (df['stellar_radius'] ** 3)
    
    return df

def main():
    print_banner()
    
    # Load model
    print("Loading trained model...\n")
    try:
        model = ExoplanetModel()
        model.load_model('exoplanet_model.pkl')
        print("✓ Model loaded successfully!\n")
    except FileNotFoundError:
        print("❌ Error: Model file 'exoplanet_model.pkl' not found.")
        print("Please run 'python train_model.py' first to train the model.\n")
        return
    except Exception as e:
        print(f"❌ Error loading model: {e}\n")
        return
    
    # Get user input
    inputs = get_user_input()
    
    if inputs is None:
        return
    
    print("\n" + "-" * 70)
    print("Calculating derived properties...")
    print("-" * 70)
    
    # Calculate derived features
    input_df = calculate_derived_features(inputs)
    
    print("\nCalculated Properties:")
    print(f"  • Impact Parameter: {input_df['impact_parameter'].values[0]:.4f}")
    print(f"  • Semi-Major Axis: {input_df['semi_major_axis'].values[0]:.4f} AU")
    print(f"  • Planet Radius: {input_df['planet_radius'].values[0]:.3f} Earth radii")
    print(f"  • Equilibrium Temperature: {input_df['planet_temp'].values[0]:.1f} K")
    
    # Make prediction
    print("\n" + "-" * 70)
    print("Running ML analysis...")
    print("-" * 70)
    
    result = model.predict(input_df)
    
    # Display results
    print_result(result)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
