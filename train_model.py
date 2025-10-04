"""
Train Exoplanet Detection Model
Downloads NASA data, processes it, and trains the ML model
"""

import os
import pandas as pd
import numpy as np
from exoplanet_data_fetcher import ExoplanetDataFetcher
from exoplanet_physics import ExoplanetPhysics
from exoplanet_model import ExoplanetModel

def main():
    print("=" * 70)
    print(" " * 15 + "EXOPLANET DETECTION MODEL TRAINING")
    print("=" * 70)
    
    # Step 1: Fetch data
    print("\n[1/4] Fetching NASA Exoplanet Data...")
    print("-" * 70)
    
    # Check if data already exists
    if os.path.exists('exoplanet_training_data.csv'):
        print("Found existing training data file.")
        print("Loading from exoplanet_training_data.csv...")
        df = pd.read_csv('exoplanet_training_data.csv')
        print(f"Loaded {len(df)} samples")
    else:
        print("Fetching data from NASA archives...")
        fetcher = ExoplanetDataFetcher()
        df = fetcher.prepare_training_data()
        
        # Save raw data
        df.to_csv('exoplanet_training_data_raw.csv', index=False)
        print("Raw data saved to 'exoplanet_training_data_raw.csv'")
    
    print(f"\nDataset shape: {df.shape}")
    print(f"Features: {df.columns.tolist()}")
    
    # Step 2: Feature Engineering
    print("\n[2/4] Feature Engineering & Physics Calculations...")
    print("-" * 70)
    
    df = ExoplanetPhysics.enrich_features(df)
    
    # Remove rows with too many missing values
    print("\nCleaning data...")
    initial_count = len(df)
    
    # Count non-null values per row
    non_null_counts = df.count(axis=1)
    min_required_features = 10
    df = df[non_null_counts >= min_required_features]
    
    print(f"Removed {initial_count - len(df)} samples with insufficient data")
    print(f"Final dataset: {len(df)} samples")
    
    # Save processed data
    df.to_csv('exoplanet_training_data.csv', index=False)
    print("Processed data saved to 'exoplanet_training_data.csv'")
    
    # Step 3: Train Model
    print("\n[3/4] Training Machine Learning Model...")
    print("-" * 70)
    print("NOTE: Using fast training mode for quicker results")
    print("      (You can edit train_model.py to use full mode)")
    
    model = ExoplanetModel()
    results = model.train(df, test_size=0.2, validate=True, fast_mode=True)
    
    # Step 4: Save Model
    print("\n[4/4] Saving Model...")
    print("-" * 70)
    
    model.save_model('exoplanet_model.pkl')
    
    # Save feature importance
    if model.feature_importance is not None:
        model.feature_importance.to_csv('feature_importance.csv', index=False)
        print("Feature importance saved to 'feature_importance.csv'")
    
    # Final summary
    print("\n" + "=" * 70)
    print(" " * 20 + "TRAINING COMPLETE!")
    print("=" * 70)
    print(f"\n✓ Model trained with accuracy: {results['accuracy']:.4f}")
    print(f"✓ F1 Score: {results['f1_score']:.4f}")
    print(f"✓ Model saved to: exoplanet_model.pkl")
    print(f"✓ Training data: exoplanet_training_data.csv")
    print("\nYou can now use 'exoplanet_predict.py' to make predictions!")
    print("=" * 70)

if __name__ == "__main__":
    main()
