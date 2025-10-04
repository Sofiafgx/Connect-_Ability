# 🚀 Quick Start Guide - Exoplanet Detection System

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- numpy, pandas, scipy (scientific computing)
- scikit-learn, xgboost (machine learning)
- astropy, astroquery (NASA data access)
- joblib (model persistence)

## Step 2: Train the Model

### First Time Training

```bash
python3 train_model.py
```

This will:
1. **Download** ~9,000+ exoplanet observations from NASA
2. **Process** the data and calculate physics-based features
3. **Train** an ensemble ML model (Random Forest + XGBoost + Gradient Boosting + Neural Network)
4. **Save** the trained model to `exoplanet_model.pkl`

**Expected time**: 5-15 minutes depending on your internet speed and CPU

**Note**: The script uses "fast mode" by default for quicker training. To use full accuracy mode, edit line 69 in `train_model.py` and change `fast_mode=True` to `fast_mode=False`.

### If You Already Have Data

If `exoplanet_training_data.csv` exists, the script will use it instead of downloading again.

## Step 3: Make Predictions

### Interactive Mode (Recommended for Beginners)

```bash
python3 exoplanet_predict.py
```

You'll be prompted to enter parameters:

**Example Input:**
```
Orbital Period (days): 365.25
Transit Depth (ppm or %): 84
Transit Duration (hours): 13.0
Stellar Radius (solar radii): 1.0
Stellar Mass (solar masses) [default: 1.0]: 1.0
Stellar Temperature (K) [default: 5778]: 5778
Signal-to-Noise Ratio [default: 10.0]: 15.0
Stellar Magnitude [default: 12.0]: 11.5
```

**Example Output:**
```
📊 CLASSIFICATION: CONFIRMED
🎯 CONFIDENCE: 87.34%

🌍 Impact Parameter: 0.2345
🪐 Planet Radius: 1.021 Earth radii (Earth-like)
🌡️  Equilibrium Temperature: 278.3 K (Potentially habitable)
🔭 Semi-Major Axis: 1.0000 AU
🌱 POTENTIALLY IN HABITABLE ZONE!
```

### Batch Mode (For Multiple Candidates)

```bash
python3 batch_predict.py example_input.csv
```

This will:
1. Read all candidates from the CSV file
2. Analyze each one
3. Save results to `example_input_predictions.csv`
4. Show summary statistics

**CSV Format:**
```csv
orbital_period,transit_depth,transit_duration,stellar_radius,stellar_mass,stellar_temp,snr,stellar_magnitude
365.25,84,13.0,1.0,1.0,5778,15.0,11.5
3.52,2800,4.2,1.2,1.1,5200,22.5,10.8
```

## Understanding the Input Parameters

### Required Parameters

1. **Orbital Period** (days)
   - Time for one complete orbit around the star
   - Example: Earth = 365.25 days, Mercury = 88 days

2. **Transit Depth** (ppm or %)
   - How much starlight is blocked during transit
   - Can be in parts-per-million (ppm) or percentage
   - Example: 84 ppm = 0.0084% (Earth-like)
   - Hot Jupiters: ~10,000+ ppm

3. **Transit Duration** (hours)
   - How long the planet blocks the star
   - Example: Earth = ~13 hours

4. **Stellar Radius** (solar radii)
   - Size of the host star relative to our Sun
   - Example: Sun = 1.0, Betelgeuse = 764

### Optional Parameters (with defaults)

5. **Stellar Mass** (solar masses) - [default: 1.0]
   - Mass of the host star
   - Affects orbital calculations

6. **Stellar Temperature** (Kelvin) - [default: 5778]
   - Surface temperature of the star
   - Sun = 5778 K
   - Red dwarfs: 2,500-3,500 K
   - Blue giants: 10,000-50,000 K

7. **Signal-to-Noise Ratio** - [default: 10.0]
   - Quality of the detection signal
   - Higher = better quality
   - Minimum ~3 for detection, >7 for confidence

8. **Stellar Magnitude** - [default: 12.0]
   - Brightness of the star
   - Lower = brighter
   - Sun = 4.8, faintest visible = ~6.5

## Understanding the Output

### Classifications

- **CONFIRMED**: High-confidence exoplanet detection
  - Model is very confident this is a real planet
  - Safe for scientific reporting

- **CANDIDATE**: Potential exoplanet needing follow-up
  - Interesting signal but needs more data
  - Should be observed again

- **FALSE POSITIVE**: Likely not a planet
  - Could be stellar activity, binary stars, or artifacts
  - Should be deprioritized

### Exoplanet Properties (for confirmed/candidates)

- **Impact Parameter**: Distance from star center at mid-transit (0 = perfectly centered)
- **Planet Radius**: Size in Earth radii
  - <1.25: Earth-like (rocky)
  - 1.25-2.0: Super-Earth
  - 2.0-6.0: Neptune-like
  - >6.0: Jupiter-like (gas giant)

- **Equilibrium Temperature**: Surface temperature estimate
  - <200 K: Frozen world
  - 200-350 K: Potentially habitable
  - >350 K: Hot world

- **Semi-Major Axis**: Average distance from star (in AU)
  - 1 AU = Earth-Sun distance
  - Mars = 1.52 AU, Jupiter = 5.2 AU

- **Habitability Flag**: Whether it's in the "Goldilocks zone"

## Troubleshooting

### "Model file not found"
Run `python3 train_model.py` first to train the model.

### "Error fetching data from NASA"
- Check your internet connection
- NASA servers might be temporarily down
- Try again in a few minutes

### Training takes too long
- Fast mode is enabled by default (~5-10 minutes)
- You can interrupt (Ctrl+C) and it will resume from cached data
- Or use existing data if `exoplanet_training_data.csv` exists

### Low confidence predictions
- Check your input data quality (SNR should be >7)
- Verify parameters are in reasonable ranges
- Very unusual systems may confuse the model

## Advanced Usage

### Python API

```python
from exoplanet_model import ExoplanetModel
from exoplanet_physics import ExoplanetPhysics
import pandas as pd

# Load model
model = ExoplanetModel()
model.load_model('exoplanet_model.pkl')

# Prepare input
data = {
    'orbital_period': 365.25,
    'transit_depth': 84,
    'transit_duration': 13.0,
    'stellar_radius': 1.0,
    'stellar_mass': 1.0,
    'stellar_temp': 5778,
    'snr': 15.0,
    'stellar_magnitude': 11.5
}

# Calculate features
df = pd.DataFrame([data])
df = ExoplanetPhysics.enrich_features(df)

# Predict
result = model.predict(df)
print(f"Classification: {result['classification']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### Retraining with Your Own Data

1. Create a CSV with columns: `orbital_period`, `transit_depth`, `transit_duration`, `stellar_radius`, `stellar_temp`, and `disposition`
2. Add `disposition` column with values: `CONFIRMED`, `CANDIDATE`, or `FALSE_POSITIVE`
3. Load and process:

```python
import pandas as pd
from exoplanet_physics import ExoplanetPhysics
from exoplanet_model import ExoplanetModel

df = pd.read_csv('your_data.csv')
df = ExoplanetPhysics.enrich_features(df)

model = ExoplanetModel()
model.train(df)
model.save_model('custom_model.pkl')
```

## Example Scenarios

### 🌍 Earth-like Planet Search
```
Orbital Period: 365
Transit Depth: 84
Transit Duration: 13
Stellar Radius: 1.0
→ Look for CONFIRMED + Potentially Habitable flag
```

### 🔥 Hot Jupiter Detection
```
Orbital Period: 3-10
Transit Depth: 10000+
Transit Duration: 4-6
Stellar Radius: 1.0-1.5
→ Should be CONFIRMED with high confidence
```

### 🌊 Super-Earth in Habitable Zone
```
Orbital Period: 100-300
Transit Depth: 200-500
Transit Duration: 10-15
Stellar Radius: 0.8-1.2
→ Look for CONFIRMED/CANDIDATE + Radius 1.5-2.0 Earth
```

## Next Steps

- Check `README_EXOPLANET.md` for detailed technical documentation
- Explore feature importance: `cat feature_importance.csv`
- Try batch predictions on multiple candidates
- Experiment with different stellar types and planet sizes

## Questions or Issues?

The model is trained on real NASA data and uses physics-based calculations. However:
- Predictions are probabilistic, not definitive
- Always verify with additional observations
- False positives can occur with noisy data
- The model works best with SNR >7

Happy planet hunting! 🔭🌟
