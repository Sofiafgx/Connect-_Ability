"""
NASA Exoplanet Data Fetcher
Downloads and preprocesses data from Kepler, K2, and TESS missions
"""

import pandas as pd
import numpy as np
from astroquery.mast import Catalogs
from astroquery.nasa_exoplanet_archive import NasaExoplanetArchive
import warnings
warnings.filterwarnings('ignore')

class ExoplanetDataFetcher:
    def __init__(self):
        self.data = None
        
    def fetch_confirmed_exoplanets(self):
        """Fetch confirmed exoplanets from NASA Exoplanet Archive"""
        try:
            print("Fetching confirmed exoplanets from NASA Archive...")
            # Get planetary systems composite data
            exoplanets = NasaExoplanetArchive.query_criteria(
                table="pscomppars",
                select="*",
                cache=True
            )
            print(f"Fetched {len(exoplanets)} confirmed exoplanets")
            return exoplanets.to_pandas()
        except Exception as e:
            print(f"Error fetching confirmed exoplanets: {e}")
            return None
    
    def fetch_kepler_objects(self):
        """Fetch Kepler Objects of Interest (KOIs)"""
        try:
            print("Fetching Kepler Objects of Interest...")
            kois = NasaExoplanetArchive.query_criteria(
                table="cumulative",
                select="*",
                cache=True
            )
            print(f"Fetched {len(kois)} Kepler objects")
            return kois.to_pandas()
        except Exception as e:
            print(f"Error fetching Kepler objects: {e}")
            return None
    
    def fetch_tess_objects(self):
        """Fetch TESS Objects of Interest (TOIs)"""
        try:
            print("Fetching TESS Objects of Interest...")
            tois = NasaExoplanetArchive.query_criteria(
                table="toi",
                select="*",
                cache=True
            )
            print(f"Fetched {len(tois)} TESS objects")
            return tois.to_pandas()
        except Exception as e:
            print(f"Error fetching TESS objects: {e}")
            return None
    
    def fetch_all_data(self):
        """Fetch all available exoplanet data"""
        print("=" * 60)
        print("Fetching NASA Exoplanet Data")
        print("=" * 60)
        
        confirmed = self.fetch_confirmed_exoplanets()
        kepler = self.fetch_kepler_objects()
        tess = self.fetch_tess_objects()
        
        return {
            'confirmed': confirmed,
            'kepler': kepler,
            'tess': tess
        }
    
    def prepare_training_data(self, use_kepler_only=True):
        """Prepare unified training dataset from multiple sources"""
        data_dict = self.fetch_all_data()
        
        # Process Kepler data (most comprehensive for training)
        if data_dict['kepler'] is not None:
            kepler_df = self.process_kepler_data(data_dict['kepler'])
            print(f"Processed Kepler data: {len(kepler_df)} samples")
        else:
            kepler_df = pd.DataFrame()
        
        # For faster training, use only Kepler data
        if use_kepler_only and not kepler_df.empty:
            combined_df = kepler_df
        else:
            # Process TESS data
            if data_dict['tess'] is not None:
                tess_df = self.process_tess_data(data_dict['tess'])
                print(f"Processed TESS data: {len(tess_df)} samples")
            else:
                tess_df = pd.DataFrame()
            
            # Combine datasets
            if not kepler_df.empty and not tess_df.empty:
                combined_df = pd.concat([kepler_df, tess_df], ignore_index=True)
            elif not kepler_df.empty:
                combined_df = kepler_df
            elif not tess_df.empty:
                combined_df = tess_df
            else:
                raise ValueError("No data available")
        
        print(f"\nTotal training samples: {len(combined_df)}")
        print(f"Distribution:")
        print(combined_df['disposition'].value_counts())
        
        return combined_df
    
    def process_kepler_data(self, df):
        """Process Kepler data with relevant features"""
        processed = pd.DataFrame()
        
        # Map column names (Kepler specific)
        column_mapping = {
            'koi_period': 'orbital_period',
            'koi_depth': 'transit_depth',
            'koi_duration': 'transit_duration',
            'koi_srad': 'stellar_radius',
            'koi_smass': 'stellar_mass',
            'koi_steff': 'stellar_temp',
            'koi_snr': 'snr',
            'koi_kepmag': 'stellar_magnitude',
            'koi_impact': 'impact_parameter',
            'koi_prad': 'planet_radius',
            'koi_teq': 'planet_temp',
            'koi_disposition': 'disposition'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                processed[new_col] = df[old_col]
        
        # Clean disposition labels
        if 'disposition' in processed.columns:
            processed['disposition'] = processed['disposition'].map({
                'CONFIRMED': 'CONFIRMED',
                'CANDIDATE': 'CANDIDATE',
                'FALSE POSITIVE': 'FALSE_POSITIVE'
            })
        
        # Remove rows with missing critical values
        critical_cols = ['orbital_period', 'stellar_radius', 'stellar_temp', 'disposition']
        # Only check columns that exist
        critical_cols_present = [col for col in critical_cols if col in processed.columns]
        if critical_cols_present:
            processed = processed.dropna(subset=critical_cols_present)
        
        # Remove invalid values
        if 'orbital_period' in processed.columns:
            processed = processed[processed['orbital_period'] > 0]
        if 'transit_depth' in processed.columns:
            processed = processed[processed['transit_depth'] > 0]
        if 'stellar_radius' in processed.columns:
            processed = processed[processed['stellar_radius'] > 0]
        
        return processed
    
    def process_tess_data(self, df):
        """Process TESS data with relevant features"""
        processed = pd.DataFrame()
        
        # Map column names (TESS specific)
        column_mapping = {
            'pl_orbper': 'orbital_period',
            'pl_trandep': 'transit_depth',
            'pl_trandur': 'transit_duration',
            'st_rad': 'stellar_radius',
            'st_mass': 'stellar_mass',
            'st_teff': 'stellar_temp',
            'toi_snr': 'snr',
            'st_tmag': 'stellar_magnitude',
            'pl_imppar': 'impact_parameter',
            'pl_rade': 'planet_radius',
            'pl_eqt': 'planet_temp',
            'tfopwg_disp': 'disposition'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                processed[new_col] = df[old_col]
        
        # Clean disposition labels
        if 'disposition' in processed.columns:
            processed['disposition'] = processed['disposition'].map({
                'CP': 'CONFIRMED',
                'PC': 'CANDIDATE',
                'FP': 'FALSE_POSITIVE',
                'KP': 'CANDIDATE'
            })
        
        # Remove rows with missing critical values
        critical_cols = ['orbital_period', 'stellar_radius', 'stellar_temp', 'disposition']
        # Only check columns that exist
        critical_cols_present = [col for col in critical_cols if col in processed.columns]
        if critical_cols_present:
            processed = processed.dropna(subset=critical_cols_present)
        
        # Remove invalid values
        if 'orbital_period' in processed.columns:
            processed = processed[processed['orbital_period'] > 0]
        if 'transit_depth' in processed.columns:
            processed = processed[processed['transit_depth'] > 0]
        if 'stellar_radius' in processed.columns:
            processed = processed[processed['stellar_radius'] > 0]
        
        return processed

if __name__ == "__main__":
    fetcher = ExoplanetDataFetcher()
    data = fetcher.prepare_training_data()
    
    # Save to CSV
    data.to_csv('exoplanet_training_data.csv', index=False)
    print("\nData saved to 'exoplanet_training_data.csv'")
