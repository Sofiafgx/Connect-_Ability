# 📘 Usage Examples - Exoplanet Detection System

## Installation

```bash
pip install -r requirements.txt
python3 train_model.py  # First time only, takes 5-15 minutes
```

## Example 1: Interactive Single Prediction

```bash
python3 exoplanet_predict.py
```

### Input Example (Earth-like):
```
Orbital Period (days): 365.25
Transit Depth (ppm or %): 84
Transit Duration (hours): 13.0
Stellar Radius (solar radii): 1.0
Stellar Mass (solar masses): 1.0
Stellar Temperature (K): 5778
Signal-to-Noise Ratio: 15.0
Stellar Magnitude: 11.5
```

## Example 2: Batch Prediction from CSV

```bash
python3 batch_predict.py example_input.csv
```

### Input CSV Format:
```csv
orbital_period,transit_depth,transit_duration,stellar_radius,stellar_mass,stellar_temp,snr,stellar_magnitude
365.25,84,13.0,1.0,1.0,5778,15.0,11.5
3.52,2800,4.2,1.2,1.1,5200,22.5,10.8
```

### Output:
```
Classification Summary:
CONFIRMED         3
FALSE_POSITIVE    2

High-confidence confirmed exoplanets: 0
Results saved to: example_input_predictions.csv
```

## Example 3: Python API

```python
import pandas as pd
from exoplanet_model import ExoplanetModel
from exoplanet_physics import ExoplanetPhysics

# Load the trained model
model = ExoplanetModel()
model.load_model('exoplanet_model.pkl')

# Define input parameters
data = {
    'orbital_period': 10.5,
    'transit_depth': 4200,
    'transit_duration': 5.8,
    'stellar_radius': 1.3,
    'stellar_mass': 1.25,
    'stellar_temp': 4800,
    'snr': 25.3,
    'stellar_magnitude': 9.7
}

# Process and predict
df = pd.DataFrame([data])
df = ExoplanetPhysics.enrich_features(df)
result = model.predict(df)

# Display results
print(f"Classification: {result['classification']}")
print(f"Confidence: {result['confidence']:.2%}")

if result['classification'] in ['CONFIRMED', 'CANDIDATE']:
    print(f"Planet Radius: {result['planet_radius']:.2f} Earth radii")
    print(f"Temperature: {result['planet_temp']:.1f} K")
    print(f"Orbit: {result['semi_major_axis']:.4f} AU")
```

## Example 4: Real Exoplanet - Kepler-452b (Earth's Cousin)

Kepler-452b is known as "Earth's cousin" - in the habitable zone.

```python
kepler_452b = {
    'orbital_period': 384.8,
    'transit_depth': 200,
    'transit_duration': 14.2,
    'stellar_radius': 1.11,
    'stellar_mass': 1.04,
    'stellar_temp': 5757,
    'snr': 20.0,
    'stellar_magnitude': 13.4
}
```

Expected: CONFIRMED or CANDIDATE, potentially habitable

## Example 5: Hot Jupiter - HD 209458 b (Osiris)

One of the first exoplanets discovered by transit method.

```python
hd_209458_b = {
    'orbital_period': 3.52,
    'transit_depth': 15000,
    'transit_duration': 3.04,
    'stellar_radius': 1.2,
    'stellar_mass': 1.1,
    'stellar_temp': 6065,
    'snr': 30.0,
    'stellar_magnitude': 7.65
}
```

Expected: CONFIRMED, large radius (~13 Earth radii), very hot

## Example 6: Super-Earth - Kepler-22b

First confirmed Kepler planet in habitable zone.

```python
kepler_22b = {
    'orbital_period': 289.9,
    'transit_depth': 492,
    'transit_duration': 11.5,
    'stellar_radius': 0.979,
    'stellar_mass': 0.97,
    'stellar_temp': 5518,
    'snr': 18.0,
    'stellar_magnitude': 11.7
}
```

Expected: CONFIRMED, radius ~2.4 Earth radii, potentially habitable

## Example 7: Batch Analysis of Multiple Systems

Create `my_candidates.csv`:
```csv
orbital_period,transit_depth,transit_duration,stellar_radius,stellar_mass,stellar_temp,snr,stellar_magnitude
384.8,200,14.2,1.11,1.04,5757,20.0,13.4
3.52,15000,3.04,1.2,1.1,6065,30.0,7.65
289.9,492,11.5,0.979,0.97,5518,18.0,11.7
1.58,8500,2.1,0.85,0.92,5000,22.0,12.3
687.0,95,15.8,1.05,1.02,5800,12.0,10.9
```

Run:
```bash
python3 batch_predict.py my_candidates.csv
```

## Example 8: Finding Habitable Zone Planets

```python
import pandas as pd
from exoplanet_model import ExoplanetModel
from exoplanet_physics import ExoplanetPhysics

model = ExoplanetModel()
model.load_model('exoplanet_model.pkl')

# Load candidates
candidates = pd.read_csv('my_candidates.csv')
candidates = ExoplanetPhysics.enrich_features(candidates)

# Find habitable planets
habitable = []
for idx, row in candidates.iterrows():
    result = model.predict(pd.DataFrame([row]))
    
    if result['classification'] in ['CONFIRMED', 'CANDIDATE']:
        if result.get('potentially_habitable') == 1:
            habitable.append({
                'id': idx,
                'confidence': result['confidence'],
                'radius': result['planet_radius'],
                'temp': result['planet_temp']
            })

# Display
print(f"Found {len(habitable)} potentially habitable planets:")
for planet in habitable:
    print(f"  Candidate #{planet['id']}: "
          f"{planet['radius']:.2f} R_earth, "
          f"{planet['temp']:.1f} K, "
          f"{planet['confidence']:.1%} confidence")
```

## Example 9: Model Performance Analysis

```python
import pandas as pd

# Load feature importance
importance = pd.read_csv('feature_importance.csv')

print("Top 5 Most Important Features:")
print(importance.head())

# Sample output:
#          feature  importance
# 0  planet_radius    0.173560
# 1  stellar_mag    0.096589
# 2  impact_param   0.087518
# 3  transit_depth  0.078600
# 4  log_transit_d  0.076180
```

## Example 10: Custom Training Data

If you have your own labeled data:

```python
import pandas as pd
from exoplanet_physics import ExoplanetPhysics
from exoplanet_model import ExoplanetModel

# Your data should have disposition labels
custom_data = pd.read_csv('my_labeled_data.csv')
# Must contain: orbital_period, transit_depth, transit_duration,
#               stellar_radius, stellar_temp, disposition

# Add physics features
custom_data = ExoplanetPhysics.enrich_features(custom_data)

# Train new model
model = ExoplanetModel()
model.train(custom_data, fast_mode=False)  # Use full accuracy
model.save_model('my_custom_model.pkl')

# Use your custom model
model.load_model('my_custom_model.pkl')
result = model.predict(new_candidate)
```

## Tips for Best Results

### High-Quality Detections (SNR > 15)
- More reliable classifications
- Better confidence scores
- Use for publication-quality results

### Moderate-Quality (7 < SNR < 15)
- Good for candidate identification
- May need follow-up observations
- Still useful for filtering

### Low-Quality (SNR < 7)
- Use with caution
- High false positive rate
- Consider as preliminary only

### Stellar Parameters
- More accurate stellar parameters = better planet characterization
- If stellar mass unknown, provide stellar radius (used as proxy)
- Temperature affects equilibrium temperature calculation

### Transit Depth Units
- Can input as ppm (parts per million) or percentage
- Model auto-detects: >1 = ppm, ≤1 = percentage
- Earth-like: ~84 ppm = 0.0084%
- Hot Jupiter: ~10,000-30,000 ppm = 1-3%

## Interpreting Confidence Scores

- **>80%**: Very confident, likely real or false positive
- **60-80%**: Moderate confidence, good candidate
- **40-60%**: Uncertain, needs more data
- **<40%**: Low confidence, questionable

## Common Pitfalls

1. **Very short periods (<0.5 days)**: Often false positives or stellar activity
2. **Very shallow transits (<10 ppm with low SNR)**: Hard to confirm
3. **Inconsistent parameters**: E.g., huge transit depth but short duration
4. **Missing stellar parameters**: Reduces accuracy of derived properties

## Getting More Help

- Check `README_EXOPLANET.md` for technical details
- See `QUICKSTART.md` for step-by-step guide
- Review `feature_importance.csv` to understand model decisions

Happy planet hunting! 🔭✨
