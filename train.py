"""
Training script for exoplanet detection model
Downloads NASA data, trains neural network, and saves the model
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings

import numpy as np
import pandas as pd
from data_loader import ExoplanetDataLoader
from model import ExoplanetClassifier
import warnings
warnings.filterwarnings('ignore')


def main():
    print("="*80)
    print(" EXOPLANET DETECTION AI - TRAINING PIPELINE")
    print(" NASA Kepler, K2, and TESS Missions Data")
    print("="*80)
    
    # Step 1: Load and preprocess data
    print("\n[STEP 1/5] Loading NASA Exoplanet Data")
    print("-" * 80)
    
    loader = ExoplanetDataLoader(data_dir='data')
    
    # Check if data already exists
    combined_path = 'data/combined_exoplanet_data.csv'
    if os.path.exists(combined_path):
        print(f"Loading existing data from {combined_path}")
        df = pd.read_csv(combined_path)
    else:
        df = loader.load_and_combine_data()
        df.to_csv(combined_path, index=False)
        print(f"Data saved to {combined_path}")
    
    # Step 2: Prepare training data
    print("\n[STEP 2/5] Preparing Training Data")
    print("-" * 80)
    
    (X_train, y_train), (X_val, y_val), (X_test, y_test), scaler, feature_names = \
        loader.prepare_training_data(df)
    
    # Step 3: Build and train model
    print("\n[STEP 3/5] Building Neural Network")
    print("-" * 80)
    
    input_dim = X_train.shape[1]
    classifier = ExoplanetClassifier(input_dim=input_dim)
    classifier.build_model()
    
    print("\n[STEP 4/5] Training Model")
    print("-" * 80)
    print("This may take several minutes depending on your hardware...")
    
    history = classifier.train(
        X_train, y_train,
        X_val, y_val,
        epochs=100,
        batch_size=32
    )
    
    # Step 4: Evaluate model
    print("\n[STEP 5/5] Evaluating Model")
    print("-" * 80)
    
    results = classifier.evaluate(X_test, y_test)
    
    # Plot training history
    classifier.plot_training_history()
    
    # Save model
    classifier.save_model(scaler, feature_names)
    
    print("\n" + "="*80)
    print(" TRAINING COMPLETE")
    print("="*80)
    print(f"\nFinal Test Accuracy: {results['accuracy']:.4f}")
    print(f"Final Test Loss: {results['loss']:.4f}")
    print("\nModel artifacts saved:")
    print("  - models/exoplanet_classifier.h5")
    print("  - models/exoplanet_classifier_scaler.pkl")
    print("  - models/exoplanet_classifier_features.pkl")
    print("  - models/training_history.png")
    print("  - models/confusion_matrix.png")
    print("\nYou can now use the model with:")
    print("  - Web interface: python app.py")
    print("  - CLI: python predict.py")
    
    return classifier, results


if __name__ == "__main__":
    classifier, results = main()
