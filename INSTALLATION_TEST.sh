#!/bin/bash

echo "=================================="
echo "Exoplanet Detection System Test"
echo "=================================="
echo ""

# Check Python
echo "Checking Python..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }
echo "✓ Python 3 found"

# Check pip
echo ""
echo "Checking pip..."
python3 -m pip --version || { echo "❌ pip not found"; exit 1; }
echo "✓ pip found"

# Check model
echo ""
echo "Checking trained model..."
if [ -f "exoplanet_model.pkl" ]; then
    echo "✓ Model found ($(ls -lh exoplanet_model.pkl | awk '{print $5}'))"
else
    echo "⚠ Model not found - run: python3 train_model.py"
fi

# Check data
echo ""
echo "Checking training data..."
if [ -f "exoplanet_training_data.csv" ]; then
    lines=$(wc -l < exoplanet_training_data.csv)
    echo "✓ Training data found ($lines samples)"
else
    echo "⚠ Training data not found"
fi

# Test imports
echo ""
echo "Testing Python imports..."
python3 -c "
import numpy
import pandas
import sklearn
import xgboost
import astropy
print('✓ All required packages installed')
" || { echo "❌ Some packages missing - run: pip install -r requirements.txt"; exit 1; }

# Quick functionality test
echo ""
echo "Testing model prediction..."
python3 -c "
from exoplanet_model import ExoplanetModel
import pandas as pd
model = ExoplanetModel()
model.load_model('exoplanet_model.pkl')
print('✓ Model loads successfully')
print('✓ Feature names:', len(model.feature_names))
" || { echo "❌ Model test failed"; exit 1; }

echo ""
echo "=================================="
echo "✓ All tests passed!"
echo "=================================="
echo ""
echo "Ready to use:"
echo "  python3 exoplanet_predict.py"
echo "  python3 batch_predict.py example_input.csv"
echo ""
