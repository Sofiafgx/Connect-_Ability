# 🌌 Exoplanet Detection & Analysis System

An advanced machine learning system that detects and analyzes exoplanets using NASA's Kepler, K2, and TESS mission data. Features terminal-based input, automatic impact parameter calculation, and comprehensive exoplanet property prediction.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the model (first time only, takes 5-15 minutes)
python3 train_model.py

# 3. Make predictions
python3 exoplanet_predict.py
```

## ✨ Key Features

- ✅ **Terminal Input**: Enter 8 parameters directly from command line
- ✅ **Automatic Calculations**: Impact parameter, planet radius, temperature, orbital distance
- ✅ **ML Classification**: CONFIRMED / CANDIDATE / FALSE_POSITIVE
- ✅ **NASA Data**: Trained on 15,775+ real observations
- ✅ **High Accuracy**: 76.74% accuracy, ensemble of 4 ML algorithms
- ✅ **Batch Processing**: Analyze multiple candidates from CSV

## 📊 Model Performance

- **Accuracy**: 76.74%
- **F1 Score**: 0.767
- **Training Data**: 15,775 NASA observations
- **Cross-Validation**: 77.22% ± 1.68%

## 📁 Project Files

### Core Scripts
- `exoplanet_predict.py` - Interactive CLI for single predictions
- `batch_predict.py` - Batch processing from CSV files
- `train_model.py` - Train the model on NASA data

### Modules
- `exoplanet_model.py` - ML ensemble model
- `exoplanet_physics.py` - Physics-based calculations
- `exoplanet_data_fetcher.py` - NASA data acquisition

### Documentation
- `README_EXOPLANET.md` - Complete technical documentation
- `QUICKSTART.md` - Step-by-step beginner guide
- `USAGE_EXAMPLES.md` - 10+ practical examples
- `PROJECT_SUMMARY.md` - Comprehensive project overview
- `QUICK_REFERENCE.txt` - Quick reference card

## 📝 Example Usage

### Interactive Mode

```bash
$ python3 exoplanet_predict.py

Orbital Period (days): 365.25
Transit Depth (ppm): 84
Transit Duration (hours): 13.0
Stellar Radius (solar radii): 1.0
...

📊 CLASSIFICATION: CONFIRMED
🎯 CONFIDENCE: 87.34%
🪐 Planet Radius: 1.021 Earth radii
🌡️  Temperature: 278.3 K (Potentially habitable)
🔭 Semi-major axis: 1.0000 AU
```

### Batch Mode

```bash
$ python3 batch_predict.py example_input.csv

Total candidates analyzed: 5
Classification Summary:
  CONFIRMED: 3
  FALSE_POSITIVE: 2
  
Results saved to: example_input_predictions.csv
```

## 📖 Documentation

- **Getting Started**: Read `QUICKSTART.md`
- **Examples**: See `USAGE_EXAMPLES.md`
- **Technical Details**: Check `README_EXOPLANET.md`
- **Project Overview**: View `PROJECT_SUMMARY.md`
- **Quick Reference**: Open `QUICK_REFERENCE.txt`

## 🎯 Input Parameters

### Required
1. Orbital Period (days)
2. Transit Depth (ppm or %)
3. Transit Duration (hours)
4. Stellar Radius (solar radii)

### Optional (with defaults)
5. Stellar Mass (solar masses) - default: 1.0
6. Stellar Temperature (K) - default: 5778
7. Signal-to-Noise Ratio - default: 10.0
8. Stellar Magnitude - default: 12.0

## 🌟 Output

- **Classification**: CONFIRMED / CANDIDATE / FALSE_POSITIVE
- **Confidence Score**: Probability-based confidence
- **Impact Parameter**: Automatically calculated
- **Planet Properties**: Radius, temperature, orbital distance
- **Habitability Assessment**: Based on temperature and size

## 🔬 Technical Highlights

- **Ensemble ML**: Random Forest + XGBoost + Gradient Boosting + Neural Network
- **Physics Integration**: Kepler's Laws, transit geometry, thermal equilibrium
- **Real NASA Data**: Kepler and TESS missions
- **Production Ready**: Error handling, model persistence, batch processing

## 📚 Requirements

See `requirements.txt` for full list. Key dependencies:
- Python 3.7+
- scikit-learn, xgboost
- pandas, numpy
- astropy, astroquery

## 🤝 Contributing

This project improves upon existing exoplanet detection solutions by:
- Integrating physics-based calculations
- Providing user-friendly CLI interface
- Offering comprehensive property predictions
- Using ensemble ML for robustness

## 📄 License

Uses public NASA data and open-source libraries. Please cite NASA Exoplanet Archive if using for research.

## 🌐 Resources

- NASA Exoplanet Archive: https://exoplanetarchive.ipac.caltech.edu/
- NASA Exoplanet Exploration: https://exoplanets.nasa.gov/

---

**Made with ❤️ and astrophysics | Version 1.0 | Helping discover worlds beyond our solar system** 🔭✨
