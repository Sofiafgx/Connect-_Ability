"""
Data loader for NASA Exoplanet Archive datasets
Downloads and preprocesses data from Kepler, K2, and TESS missions
"""

import pandas as pd
import numpy as np
import requests
from io import StringIO
import os
import warnings
warnings.filterwarnings('ignore')


class ExoplanetDataLoader:
    """Load and preprocess NASA exoplanet data"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # NASA Exoplanet Archive API endpoints
        self.kepler_url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+cumulative&format=csv"
        self.tess_url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+toi&format=csv"
        
    def download_kepler_data(self):
        """Download Kepler cumulative dataset"""
        print("Downloading Kepler cumulative dataset...")
        try:
            response = requests.get(self.kepler_url, timeout=120)
            response.raise_for_status()
            
            filepath = os.path.join(self.data_dir, 'kepler_data.csv')
            with open(filepath, 'w') as f:
                f.write(response.text)
            
            print(f"Kepler data saved to {filepath}")
            return pd.read_csv(filepath)
        except Exception as e:
            print(f"Error downloading Kepler data: {e}")
            return None
    
    def download_tess_data(self):
        """Download TESS Objects of Interest dataset"""
        print("Downloading TESS TOI dataset...")
        try:
            response = requests.get(self.tess_url, timeout=120)
            response.raise_for_status()
            
            filepath = os.path.join(self.data_dir, 'tess_data.csv')
            with open(filepath, 'w') as f:
                f.write(response.text)
            
            print(f"TESS data saved to {filepath}")
            return pd.read_csv(filepath)
        except Exception as e:
            print(f"Error downloading TESS data: {e}")
            return None
    
    def preprocess_kepler_data(self, df):
        """
        Preprocess Kepler dataset to extract relevant features
        """
        if df is None:
            return None
            
        print(f"Preprocessing Kepler data: {len(df)} rows")
        
        # Select relevant columns with fallback names
        feature_map = {
            'koi_period': 'orbital_period',
            'koi_duration': 'transit_duration', 
            'koi_depth': 'transit_depth',
            'koi_prad': 'planet_radius',
            'koi_sma': 'semi_major_axis',
            'koi_teq': 'eq_temperature',
            'koi_impact': 'impact_parameter',
            'koi_steff': 'stellar_temp',
            'koi_srad': 'stellar_radius',
            'koi_smass': 'stellar_mass',
            'koi_kepmag': 'stellar_magnitude',
            'koi_snr': 'snr',
            'koi_disposition': 'label'
        }
        
        # Extract available columns
        available_cols = [col for col in feature_map.keys() if col in df.columns]
        df_processed = df[available_cols].copy()
        df_processed.columns = [feature_map[col] for col in available_cols]
        
        # Map labels to numeric values
        if 'label' in df_processed.columns:
            label_map = {
                'CONFIRMED': 2,  # Confirmed exoplanet
                'CANDIDATE': 1,  # Planetary candidate
                'FALSE POSITIVE': 0  # False positive
            }
            df_processed['label'] = df_processed['label'].map(label_map)
            df_processed = df_processed.dropna(subset=['label'])
        
        # Handle missing values
        df_processed = df_processed.replace([np.inf, -np.inf], np.nan)
        
        print(f"Processed Kepler data: {len(df_processed)} rows")
        if 'label' in df_processed.columns:
            print(f"Label distribution:\n{df_processed['label'].value_counts()}")
        
        return df_processed
    
    def preprocess_tess_data(self, df):
        """
        Preprocess TESS dataset to extract relevant features
        """
        if df is None:
            return None
            
        print(f"Preprocessing TESS data: {len(df)} rows")
        
        # Map TESS columns to our standard features
        feature_map = {
            'pl_orbper': 'orbital_period',
            'pl_trandur': 'transit_duration',
            'pl_trandep': 'transit_depth',
            'pl_rade': 'planet_radius',
            'pl_orbsmax': 'semi_major_axis',
            'pl_eqt': 'eq_temperature',
            'pl_imppar': 'impact_parameter',
            'st_teff': 'stellar_temp',
            'st_rad': 'stellar_radius',
            'st_mass': 'stellar_mass',
            'sy_tmag': 'stellar_magnitude',
            'toi_snr': 'snr',
            'tfopwg_disp': 'label'
        }
        
        available_cols = [col for col in feature_map.keys() if col in df.columns]
        df_processed = df[available_cols].copy()
        df_processed.columns = [feature_map[col] for col in available_cols]
        
        # Map TESS dispositions to labels
        if 'label' in df_processed.columns:
            # TESS has different disposition labels
            df_processed['label'] = df_processed['label'].apply(
                lambda x: 2 if 'CP' in str(x).upper() or 'PC' in str(x).upper() 
                else 1 if 'APC' in str(x).upper() or 'KP' in str(x).upper()
                else 0
            )
        
        df_processed = df_processed.replace([np.inf, -np.inf], np.nan)
        
        print(f"Processed TESS data: {len(df_processed)} rows")
        if 'label' in df_processed.columns:
            print(f"Label distribution:\n{df_processed['label'].value_counts()}")
        
        return df_processed
    
    def load_and_combine_data(self):
        """
        Load and combine all available datasets
        """
        all_data = []
        
        # Try to load Kepler data
        kepler_df = self.download_kepler_data()
        if kepler_df is not None:
            kepler_processed = self.preprocess_kepler_data(kepler_df)
            if kepler_processed is not None and len(kepler_processed) > 0:
                all_data.append(kepler_processed)
        
        # Try to load TESS data
        tess_df = self.download_tess_data()
        if tess_df is not None:
            tess_processed = self.preprocess_tess_data(tess_df)
            if tess_processed is not None and len(tess_processed) > 0:
                all_data.append(tess_processed)
        
        if not all_data:
            raise ValueError("No data could be loaded from NASA archives")
        
        # Combine all datasets
        combined_df = pd.concat(all_data, ignore_index=True, sort=False)
        print(f"\nCombined dataset: {len(combined_df)} rows")
        
        return combined_df
    
    def prepare_training_data(self, df, test_size=0.2, val_size=0.1):
        """
        Prepare data for training by handling missing values and splitting
        """
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        
        # Separate features and labels
        if 'label' not in df.columns:
            raise ValueError("Dataset must contain 'label' column")
        
        y = df['label'].values
        X = df.drop('label', axis=1)
        
        # Get feature names before processing
        feature_names = X.columns.tolist()
        
        # Fill missing values with median
        for col in X.columns:
            if X[col].isnull().any():
                X[col].fillna(X[col].median(), inplace=True)
        
        # Remove rows with any remaining NaN values
        mask = ~(X.isnull().any(axis=1))
        X = X[mask]
        y = y[mask]
        
        print(f"\nFinal dataset shape: {X.shape}")
        print(f"Features: {feature_names}")
        print(f"Label distribution:\n{pd.Series(y).value_counts().sort_index()}")
        
        # Split data
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size/(1-test_size), 
            random_state=42, stratify=y_temp
        )
        
        # Standardize features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)
        
        print(f"\nTraining set: {len(X_train_scaled)}")
        print(f"Validation set: {len(X_val_scaled)}")
        print(f"Test set: {len(X_test_scaled)}")
        
        return (X_train_scaled, y_train), (X_val_scaled, y_val), \
               (X_test_scaled, y_test), scaler, feature_names


if __name__ == "__main__":
    # Test data loading
    loader = ExoplanetDataLoader()
    df = loader.load_and_combine_data()
    
    # Save combined dataset
    df.to_csv('data/combined_exoplanet_data.csv', index=False)
    print("\nCombined data saved to data/combined_exoplanet_data.csv")
