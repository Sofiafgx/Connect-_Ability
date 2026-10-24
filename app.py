"""
Flask web application for exoplanet detection
Provides interactive web interface for the ML model
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from model import ExoplanetClassifier
import numpy as np
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Global model instance
classifier = None


def load_model():
    """Load the trained model"""
    global classifier
    if classifier is None:
        classifier = ExoplanetClassifier(input_dim=1)
        classifier.load_model()
    return classifier


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    API endpoint for predictions
    Accepts JSON with transit parameters
    """
    try:
        # Get data from request
        data = request.get_json()
        
        # Extract features
        features = {
            'orbital_period': float(data.get('orbital_period', 0)),
            'transit_duration': float(data.get('transit_duration', 0)),
            'transit_depth': float(data.get('transit_depth', 0)),
            'planet_radius': float(data.get('planet_radius', 0)),
            'semi_major_axis': float(data.get('semi_major_axis', 0)),
            'eq_temperature': float(data.get('eq_temperature', 0)),
            'impact_parameter': float(data.get('impact_parameter', 0)),
            'stellar_temp': float(data.get('stellar_temp', 0)),
            'stellar_radius': float(data.get('stellar_radius', 0)),
            'stellar_mass': float(data.get('stellar_mass', 0)),
            'stellar_magnitude': float(data.get('stellar_magnitude', 0)),
            'snr': float(data.get('snr', 0))
        }
        
        # Load model if not already loaded
        model = load_model()
        
        # Make prediction
        prediction, probabilities = model.predict_single(features)
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'probabilities': probabilities,
            'features': features
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """
    API endpoint for batch predictions
    Accepts JSON array of transit parameters
    """
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({
                'success': False,
                'error': 'Expected array of observations'
            }), 400
        
        model = load_model()
        results = []
        
        for item in data:
            features = {
                'orbital_period': float(item.get('orbital_period', 0)),
                'transit_duration': float(item.get('transit_duration', 0)),
                'transit_depth': float(item.get('transit_depth', 0)),
                'planet_radius': float(item.get('planet_radius', 0)),
                'semi_major_axis': float(item.get('semi_major_axis', 0)),
                'eq_temperature': float(item.get('eq_temperature', 0)),
                'impact_parameter': float(item.get('impact_parameter', 0)),
                'stellar_temp': float(item.get('stellar_temp', 0)),
                'stellar_radius': float(item.get('stellar_radius', 0)),
                'stellar_mass': float(item.get('stellar_mass', 0)),
                'stellar_magnitude': float(item.get('stellar_magnitude', 0)),
                'snr': float(item.get('snr', 0))
            }
            
            prediction, probabilities = model.predict_single(features)
            results.append({
                'prediction': prediction,
                'probabilities': probabilities
            })
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        model_exists = os.path.exists('models/exoplanet_classifier.h5')
        return jsonify({
            'status': 'healthy',
            'model_loaded': classifier is not None,
            'model_exists': model_exists
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Check if model exists
    if not os.path.exists('models/exoplanet_classifier.h5'):
        print("\n" + "="*80)
        print(" WARNING: Model not found!")
        print("="*80)
        print("\nPlease train the model first by running:")
        print("  python train.py")
        print("\nThe web server will start, but predictions will fail until the model is trained.")
        print("="*80 + "\n")
    
    print("\n" + "="*80)
    print(" EXOPLANET DETECTION WEB INTERFACE")
    print("="*80)
    print("\nStarting Flask server...")
    print("Access the web interface at: http://localhost:5000")
    print("\nAPI Endpoints:")
    print("  POST /predict       - Single prediction")
    print("  POST /batch_predict - Batch predictions")
    print("  GET  /health        - Health check")
    print("\nPress Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
