# 🚀 Quick Start Guide - Exoplanet Detection AI

## ✅ System Status

**Your exoplanet detection AI is fully trained and ready to use!**

- ✓ Model trained on 17,267 NASA observations
- ✓ Test accuracy: 67.86%
- ✓ Trained on Kepler + TESS missions data
- ✓ Web interface ready
- ✓ CLI tool ready
- ✓ REST API ready

---

## 🎯 Option 1: Web Interface (Recommended)

### Start the Server

```bash
python3 app.py
```

### Access the Interface

Open your browser to: **http://localhost:5000**

Features:
- ✨ Beautiful modern UI
- 📝 Interactive form with tooltips
- 📊 Real-time prediction visualization
- 🔄 Example data loader
- 📈 Confidence probability bars
- 💡 Detailed interpretation of results

---

## 💻 Option 2: Command Line Interface

### Interactive Mode (Easiest)

```bash
python3 predict.py --interactive
```

You'll be prompted to enter each parameter interactively.

### Direct Command-Line Input

```bash
python3 predict.py \
    --orbital_period 3.5 \
    --transit_duration 2.8 \
    --transit_depth 850 \
    --planet_radius 1.4 \
    --semi_major_axis 0.045 \
    --eq_temperature 1342 \
    --impact_parameter 0.42 \
    --stellar_temp 5778 \
    --stellar_radius 0.98 \
    --stellar_mass 0.95 \
    --stellar_magnitude 12.3 \
    --snr 18.5
```

---

## 🔌 Option 3: REST API

### Start the API Server

```bash
python3 app.py
```

### Single Prediction

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "orbital_period": 3.5,
    "transit_duration": 2.8,
    "transit_depth": 850,
    "planet_radius": 1.4,
    "semi_major_axis": 0.045,
    "eq_temperature": 1342,
    "impact_parameter": 0.42,
    "stellar_temp": 5778,
    "stellar_radius": 0.98,
    "stellar_mass": 0.95,
    "stellar_magnitude": 12.3,
    "snr": 18.5
  }'
```

### Batch Predictions

```bash
curl -X POST http://localhost:5000/batch_predict \
  -H "Content-Type: application/json" \
  -d '[
    {
      "orbital_period": 3.5,
      "transit_duration": 2.8,
      ...
    },
    {
      "orbital_period": 5.7,
      "transit_duration": 3.2,
      ...
    }
  ]'
```

---

## 📊 Understanding the Results

### Three Classification Categories

#### ✅ Confirmed Exoplanet
- **Meaning**: High confidence planetary detection
- **Action**: Excellent candidate for detailed characterization
- **Typical Confidence**: > 70%

#### ⚠️ Planetary Candidate  
- **Meaning**: Shows promise but needs validation
- **Action**: Priority for follow-up observations
- **Typical Confidence**: 40-70%

#### ❌ False Positive
- **Meaning**: Likely non-planetary signal
- **Action**: Low priority, possible eclipsing binary or artifact
- **Typical Confidence**: > 60% for false positive

---

## 🎓 Example Test Cases

### Confirmed Exoplanet Example
```bash
python3 predict.py \
    --orbital_period 3.5234 \
    --transit_duration 2.8 \
    --transit_depth 850 \
    --planet_radius 1.4 \
    --semi_major_axis 0.045 \
    --eq_temperature 1342 \
    --impact_parameter 0.42 \
    --stellar_temp 5778 \
    --stellar_radius 0.98 \
    --stellar_mass 0.95 \
    --stellar_magnitude 12.3 \
    --snr 18.5
```

### False Positive Example  
```bash
python3 predict.py \
    --orbital_period 0.5 \
    --transit_duration 0.8 \
    --transit_depth 15000 \
    --planet_radius 12.5 \
    --semi_major_axis 0.012 \
    --eq_temperature 2800 \
    --impact_parameter 0.1 \
    --stellar_temp 6200 \
    --stellar_radius 1.5 \
    --stellar_mass 1.3 \
    --stellar_magnitude 11.5 \
    --snr 8.2
```

---

## 📁 Project Files

### Core Files
- `data_loader.py` - NASA data downloader and preprocessor
- `model.py` - Neural network architecture and training logic
- `train.py` - Training pipeline script
- `predict.py` - CLI prediction interface
- `app.py` - Flask web application
- `test_system.py` - System validation tests

### Web Interface
- `templates/index.html` - Web UI HTML
- `static/css/style.css` - Modern styling
- `static/js/script.js` - Frontend JavaScript

### Data & Models
- `data/` - Downloaded NASA datasets (17,267 observations)
- `models/` - Trained model files and visualizations
  - `exoplanet_classifier.h5` - Trained neural network
  - `exoplanet_classifier_scaler.pkl` - Feature scaler
  - `exoplanet_classifier_features.pkl` - Feature names
  - `training_history.png` - Training metrics plot
  - `confusion_matrix.png` - Classification performance

### Documentation
- `README_EXOPLANET.md` - Full documentation
- `QUICKSTART.md` - This quick start guide
- `requirements.txt` - Python dependencies

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Use a different port
python3 app.py
# Then access: http://localhost:5000
```

### Module Not Found Errors
```bash
pip3 install -r requirements.txt
```

### Model Not Found
```bash
# Retrain if needed
python3 train.py
```

---

## 📈 Model Performance

**Training Dataset**: 17,267 observations
- Kepler Mission: 9,564 observations
- TESS Mission: 7,703 observations

**Test Set Performance**:
- Overall Accuracy: **67.86%**
- False Positive Detection: 84% precision
- Confirmed Exoplanet: 77% precision and recall
- Candidate Detection: 57% recall

**Architecture**:
- 56,515 trainable parameters
- 4 dense layers with batch normalization
- Attention mechanism for feature weighting
- SMOTE class balancing
- Early stopping and learning rate reduction

---

## 🎯 Input Parameters Guide

### Transit Properties
| Parameter | Unit | Description | Typical Range |
|-----------|------|-------------|---------------|
| orbital_period | days | Planet orbital period | 0.5 - 500 |
| transit_duration | hours | Transit duration | 0.5 - 10 |
| transit_depth | ppm | Brightness drop | 10 - 50,000 |
| snr | - | Signal quality | 5 - 100+ |

### Planetary Properties
| Parameter | Unit | Description | Typical Range |
|-----------|------|-------------|---------------|
| planet_radius | R⊕ | Planet radius | 0.5 - 20 |
| semi_major_axis | AU | Orbital distance | 0.01 - 10 |
| eq_temperature | K | Surface temp | 200 - 3000 |
| impact_parameter | - | Transit geometry | 0 - 1 |

### Stellar Properties
| Parameter | Unit | Description | Typical Range |
|-----------|------|-------------|---------------|
| stellar_temp | K | Star temperature | 3000 - 10,000 |
| stellar_radius | R☉ | Star radius | 0.1 - 100 |
| stellar_mass | M☉ | Star mass | 0.1 - 10 |
| stellar_magnitude | mag | Brightness | 5 - 20 |

---

## 🌟 Next Steps

1. **Try the Web Interface**: Most user-friendly option
2. **Experiment with Examples**: Test different parameter combinations
3. **Integrate with Your Workflow**: Use the REST API
4. **Explore the Code**: Understand the neural network architecture
5. **Read Full Documentation**: Check `README_EXOPLANET.md`

---

## 💡 Tips for Best Results

1. **Complete Data**: More parameters = better predictions
2. **Realistic Values**: Use typical astronomical ranges
3. **Cross-Validate**: Compare with known exoplanets
4. **Understand Context**: Model trained on Kepler/TESS data
5. **Check Confidence**: Low confidence = need more data

---

## 🤝 Support & Resources

- **Full Documentation**: `README_EXOPLANET.md`
- **NASA Exoplanet Archive**: https://exoplanetarchive.ipac.caltech.edu/
- **Model Architecture**: See `model.py`
- **Training Details**: See `train.py`

---

**Built with TensorFlow/Keras • Trained on 17,267 NASA observations**

*"The universe is a pretty big place. If it's just us, seems like an awful waste of space." - Carl Sagan*
